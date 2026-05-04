# Quick Start Guide - Aura Vision Setup

## Step 1: Install Dependencies

Run this command in your terminal (PowerShell/CMD):

```bash
pip install customtkinter pillow numpy
```

## Step 2: Verify Installation

Run this to check everything is set up correctly:

```bash
python verify_setup.py
```

## Step 3: Run the Application

```bash
python python.py
```

The application window should appear with:
- **Left Panel**: Image upload and preview
- **Right Panel**: Analysis progress and results
- **Sidebar**: Navigation menu

## How It Works

### 1. Upload an Image
- Click "Browse Files"
- Select any image (PNG, JPG, GIF, WEBP)
- Preview appears in the left panel

### 2. Start Analysis
- Click "Start Analysis" button
- Watch progress bar move through 3 stages:
  1. Computing visual hashes
  2. Querying Global Registry (comparing with database)
  3. Running AI Heuristics

### 3. View Results
- **AI Generation Scan**: Shows if image is AI-generated with confidence %
- **Duplication Check**: Shows if image matches existing images in database
- **Confidence Score**: Overall confidence in the analysis

## Understanding Results

### Colors
- 🟢 **Green (Emerald)**: Original/Human-made/Trusted
- 🔴 **Red (Danger)**: AI-generated/Duplicate/Flagged

### Example Results

**Good Result:**
```
AI Generation Scan: Human Created (85%)
Duplication Check: Original / No Matches
Overall Confidence Score: 92%
```

**Suspicious Result:**
```
AI Generation Scan: AI Generated (78%)
Duplication Check: Match Found: photo.jpg (94%)
Overall Confidence Score: 88%
```

## Features Explained

### Duplication Detection
- Uses **perceptual hashing** to find similar images
- Works even if image is slightly modified (resized, rotated, filtered)
- Compares against all previous images in database
- Match threshold: 75% similarity

### AI Detection
Uses 5 analysis methods:
1. **Metadata** - Checks EXIF data for AI model signatures
2. **Frequency** - Analyzes edge patterns
3. **Color** - Checks color consistency per channel
4. **Texture** - Detects unnatural texture patterns
5. **Artifacts** - Looks for gradient anomalies

### Database
- Automatically saves all analyzed images
- Stored in `image_database.json` file
- Grows with each analysis
- Delete file anytime to start fresh

## Tips for Best Results

✅ **For AI Detection:**
- Use high-quality original images
- AI detection works best on realistic images
- Abstract/artistic images may show mixed results

✅ **For Duplication Detection:**
- Build up your database first (analyze 10+ images)
- More images = better duplicate detection
- Works with modified/filtered versions of originals

## Troubleshooting

### App crashes on startup
```bash
python -m pip install --upgrade customtkinter pillow numpy
```

### "No module named 'tkinter'" (Linux users)
```bash
sudo apt-get install python3-tk
```

### Image not loading
- Check file format is supported (PNG, JPG, GIF, WEBP)
- Ensure file is not corrupted
- Try with a different image

### Database too large
- Delete `image_database.json` to reset
- Or manually edit to remove old entries

## Keyboard Shortcuts (if added later)
- `Ctrl+O` - Open file
- `Ctrl+Q` - Quit
- `Enter` - Start analysis (if image selected)

## What's Being Saved

**In image_database.json:**
- Image filename and path
- Image hash (pHash and dHash)
- AI detection result
- Timestamp of analysis

**No actual image data is stored** - only metadata and hashes!

## Performance

- Analysis time: 2-3 seconds per image
- Database size: ~50 KB per 1000 images
- Memory usage: ~50-100 MB during analysis
- CPU usage: Spikes during analysis, minimal at rest

## Next Steps

1. ✅ Analyze some images to build your database
2. ✅ Try uploading a similar image to test duplication detection
3. ✅ Experiment with AI-generated images (from DALL-E, Midjourney, etc.)
4. ✅ Check the analysis results and understand the scoring

## Support & Documentation

See `README.md` for:
- Detailed technical documentation
- Implementation details
- Extension guides
- Performance notes

---

**Enjoy analyzing images with Aura Vision!** 🎯✨
