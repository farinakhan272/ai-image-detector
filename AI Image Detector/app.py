import os
import json
import time
import hashlib
import numpy as np
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from PIL import Image
from scipy import fftpack, signal
from scipy.ndimage import gaussian_filter
from scipy.stats import entropy

# Try to import advanced libraries
try:
    import cv2
    CV2_AVAILABLE = True
except Exception as e:
    print(f"cv2 import unavailable: {e}")
    CV2_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    from torchvision import models, transforms
    PYTORCH_AVAILABLE = True
except Exception as e:
    print(f"PyTorch import unavailable: {e}")
    PYTORCH_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
DB_PATH = 'image_database.json'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==================== BACKEND LOGIC ====================

class ImageHasher:
    @staticmethod
    def compute_hashes(image_path):
        try:
            img = Image.open(image_path).convert('L')
            # pHash
            img_p = img.resize((32, 32), Image.Resampling.LANCZOS)
            pixels_p = np.array(img_p).flatten()
            avg_p = pixels_p.mean()
            phash = ''.join(['1' if p > avg_p else '0' for p in pixels_p])
            
            # dHash
            img_d = img.resize((33, 32), Image.Resampling.LANCZOS)
            pixels_d = np.array(img_d).flatten()
            dhash = ''
            for i in range(len(pixels_d) - 1):
                if i % 33 != 32: # avoid row ends
                    dhash += '1' if pixels_d[i] < pixels_d[i+1] else '0'
            
            return phash, dhash[:1024]
        except Exception as e:
            print(f"Hash error: {e}")
            return None, None

    @staticmethod
    def similarity(h1, h2):
        if not h1 or not h2 or len(h1) != len(h2):
            return 0
        distance = sum(c1 != c2 for c1, c2 in zip(h1, h2))
        return max(0, 100 - (distance / len(h1) * 100))

class ImageDatabase:
    def __init__(self, path=DB_PATH):
        self.path = path
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    return json.load(f)
            except:
                return {"images": []}
        return {"images": []}

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def add(self, filename, phash, dhash, is_ai):
        entry = {
            "filename": filename,
            "phash": phash,
            "dhash": dhash,
            "is_ai": is_ai,
            "timestamp": datetime.now().isoformat()
        }
        self.data["images"].append(entry)
        self.save()

    def find_duplicates(self, phash, dhash, threshold=85):
        matches = []
        for entry in self.data["images"]:
            p_sim = ImageHasher.similarity(phash, entry["phash"])
            d_sim = ImageHasher.similarity(dhash, entry["dhash"])
            avg_sim = (p_sim + d_sim) / 2
            if avg_sim >= threshold:
                matches.append({"filename": entry["filename"], "similarity": avg_sim})
        return sorted(matches, key=lambda x: x["similarity"], reverse=True)

class AIDetector:
    model = None
    transform = None
    device = None

    @classmethod
    def initialize(cls):
        if not PYTORCH_AVAILABLE:
            print("PyTorch unavailable: neural analysis disabled")
            return

        if cls.model is None:
            try:
                cls.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                cls.model = models.efficientnet_b0(weights='DEFAULT')
                cls.model.eval()
                cls.model = cls.model.to(cls.device)
                cls.transform = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
                ])
                print("NN Neural Network initialized")
            except Exception as e:
                print(f"Neural Network failed: {e}")
                cls.model = None

    @staticmethod
    def analyze(image_path):
        try:
            img = Image.open(image_path).convert('RGB')
            pixels = np.array(img, dtype=np.float32)
            
            AIDetector.initialize()
            
            scores = {
                'frequency': AIDetector._freq_analysis(pixels),
                'color': AIDetector._color_analysis(pixels),
                'noise': AIDetector._noise_analysis(pixels),
                'metadata': AIDetector._metadata_analysis(image_path),
                'neural': AIDetector._neural_analysis(image_path) if AIDetector.model else 50
            }
            
            # Weighted average
            ai_score = (
                scores['frequency'] * 0.30 +
                scores['neural'] * 0.30 +
                scores['color'] * 0.20 +
                scores['noise'] * 0.15 +
                scores['metadata'] * 0.05
            )
            
            return min(100, max(0, ai_score)), scores
        except Exception as e:
            print(f"Analysis error: {e}")
            return 50, {}

    @staticmethod
    def _freq_analysis(pixels):
        try:
            gray = np.mean(pixels, axis=2)
            fft_2d = np.fft.fft2(gray)
            fft_magnitude = np.abs(np.fft.fftshift(fft_2d))
            fft_log = np.log(fft_magnitude + 1)
            h, w = fft_log.shape
            ch, cw = h // 2, w // 2
            center = fft_log[ch-15:ch+15, cw-15:cw+15]
            periphery = np.mean(fft_log)
            ratio = np.mean(center) / (periphery + 1e-10)
            # AI images often have extremely high central frequency concentration
            score = (ratio - 2.0) * 20 
            return min(100, max(0, score))
        except: return 50

    @staticmethod
    def _color_analysis(pixels):
        try:
            # Analyze color distribution entropy
            r_hist, _ = np.histogram(pixels[:,:,0], bins=256, range=(0,255))
            g_hist, _ = np.histogram(pixels[:,:,1], bins=256, range=(0,255))
            b_hist, _ = np.histogram(pixels[:,:,2], bins=256, range=(0,255))
            
            ent_r = entropy(r_hist + 1e-10)
            ent_g = entropy(g_hist + 1e-10)
            ent_b = entropy(b_hist + 1e-10)
            avg_ent = (ent_r + ent_g + ent_b) / 3
            
            # AI images often have lower color entropy (more "ordered" or quantized)
            # Real photos usually have entropy around 4.5 - 5.5
            score = (5.2 - avg_ent) * 40
            return min(100, max(0, score))
        except: return 50

    @staticmethod
    def _noise_analysis(pixels):
        try:
            gray = np.mean(pixels, axis=2)
            # High-pass filter to extract noise
            kernel = np.array([[-1,-1,-1], [-1,8,-1], [-1,-1,-1]]) / 8
            noise = signal.convolve2d(gray, kernel, mode='same')
            noise_std = np.std(noise)
            # AI images often have unnaturally low or uniform noise
            score = (0.05 - noise_std) * 1000 
            return min(100, max(0, score))
        except: return 50

    @staticmethod
    def _metadata_analysis(path):
        try:
            img = Image.open(path)
            exif = img._getexif()
            if not exif: return 65 # No EXIF is suspicious for high-end photos
            
            # Common AI tool signatures
            tags = {305: "Software", 271: "Make", 272: "Model", 42036: "LensModel"}
            meta_str = ""
            for tag_id, val in exif.items():
                if tag_id in tags:
                    meta_str += str(val).lower() + " "
            
            ai_keywords = ['midjourney', 'stable diffusion', 'dall-e', 'firefly', 'generative', 'ai', 'canvas', 'photoshop']
            if any(kw in meta_str for kw in ai_keywords):
                return 95
            
            # Check for camera makes - their presence decreases AI score
            camera_keywords = ['canon', 'nikon', 'sony', 'apple', 'samsung', 'google', 'fujifilm']
            if any(kw in meta_str for kw in camera_keywords):
                return 15
                
            return 40
        except: return 50

    @staticmethod
    def _neural_analysis(path):
        try:
            img = Image.open(path).convert('RGB')
            tensor = AIDetector.transform(img).unsqueeze(0).to(AIDetector.device)
            with torch.no_grad():
                out = AIDetector.model(tensor).cpu().numpy().flatten()
                ent = entropy(np.abs(out) / np.sum(np.abs(out)))
                return min(100, (5 - ent) * 20)
        except: return 50

db = ImageDatabase()

# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Save file
    filename = f"{int(time.time())}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Process
    phash, dhash = ImageHasher.compute_hashes(filepath)
    duplicates = db.find_duplicates(phash, dhash)
    ai_score, details = AIDetector.analyze(filepath)
    
    # Convert numpy types to standard Python types for JSON serialization
    ai_score = float(ai_score)
    is_ai = bool(ai_score > 50)
    
    # Add to DB
    db.add(filename, phash, dhash, is_ai)
    
    return jsonify({
        "filename": filename,
        "ai_score": round(ai_score, 2),
        "ai_details": {k: float(v) for k, v in details.items()},
        "is_ai": is_ai,
        "duplicates": duplicates,
        "is_duplicate": len(duplicates) > 0
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, port=port, host='0.0.0.0')
