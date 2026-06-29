# Python Version Compatibility Notes

## Recommended Python Version

**Python 3.10 - 3.13** is recommended for full compatibility with all features.

## Python 3.14+ Notes

If you're using **Python 3.14** or newer, some packages may not be fully compatible yet:

### Known Issues:

1. **librosa** - Audio processing library
   - Requires Python 3.10-3.13
   - Uses `numba` which doesn't support Python 3.14 yet
   - **Workaround**: Audio models will work with basic preprocessing. Install librosa when it supports Python 3.14.

### What Still Works:

✅ All model architectures (Image, Text, Video, Tabular, Time Series, Medical, Genomic)
✅ Audio models (with basic audio loading, without advanced librosa features)
✅ Training infrastructure
✅ FastAPI backend
✅ All UI features
✅ Model export

### Installing with Python 3.14:

```bash
pip install -r requirements.txt
```

This will install all compatible packages. Audio processing will work with basic features.

### Full Audio Support (Python 3.10-3.13):

If you need full librosa features, use Python 3.10-3.13:

```bash
# On Windows, use py launcher to select version
py -3.13 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install librosa
```

### Alternative for Python 3.14:

For audio processing without librosa, you can use:
- `pydub` - Basic audio manipulation
- `soundfile` - Audio file I/O (already included)
- `wave` (built-in) - WAV file handling

## Checking Your Python Version:

```bash
python --version
```

## Installing a Specific Python Version:

1. Download from: https://www.python.org/downloads/
2. Install Python 3.13.x
3. Create virtual environment with that version
4. Install all dependencies

---

**Note:** This is a temporary limitation. Once `numba` and `librosa` add Python 3.14 support, 
you'll be able to install them normally.

