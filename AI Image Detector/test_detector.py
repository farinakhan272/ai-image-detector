#!/usr/bin/env python3
"""Quick test of the AI detector"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Test imports
try:
    import numpy as np
    print("✓ NumPy imported")
    
    from PIL import Image
    print("✓ PIL imported")
    
    from scipy import fftpack, signal, stats
    from scipy.stats import entropy
    from scipy.ndimage import median_filter
    print("✓ SciPy imported")
    
    # Try importing optional modules
    try:
        import cv2
        print("✓ OpenCV imported (CV2_AVAILABLE = True)")
        CV2_AVAILABLE = True
    except:
        print("⚠ OpenCV not available (CV2_AVAILABLE = False)")
        CV2_AVAILABLE = False
    
    try:
        import torch
        import torchvision.models as models
        import torchvision.transforms as transforms
        print("✓ PyTorch imported")
        PYTORCH_AVAILABLE = True
    except:
        print("⚠ PyTorch not available (PYTORCH_AVAILABLE = False)")
        PYTORCH_AVAILABLE = False
    
    print("\n" + "="*50)
    print("All imports successful!")
    print("="*50)
    
    # Import the AIDetector class
    from python import AIDetector
    print("\n✓ AIDetector class imported successfully")
    
    # Initialize
    print("\nInitializing AIDetector...")
    AIDetector.initialize()
    print("✓ AIDetector initialized")
    
    # Create a test image (simple gradient)
    print("\n" + "="*50)
    print("Testing on synthetic image...")
    print("="*50)
    
    # Create a gradient image
    img_data = np.zeros((256, 256, 3), dtype=np.uint8)
    for i in range(256):
        img_data[i, :] = [i, 128, 255-i]
    
    test_img_path = "test_image.png"
    Image.fromarray(img_data).save(test_img_path)
    
    results = AIDetector.analyze_image(test_img_path)
    
    print(f"\nResults for synthetic gradient image:")
    for key, value in results.items():
        if isinstance(value, (int, float)):
            print(f"  {key}: {value:.1f}")
        else:
            print(f"  {key}: {value}")
    
    os.remove(test_img_path)
    print("\n✓ Test completed successfully!")
    
except Exception as e:
    import traceback
    print(f"\n❌ Error: {e}")
    traceback.print_exc()
    sys.exit(1)
