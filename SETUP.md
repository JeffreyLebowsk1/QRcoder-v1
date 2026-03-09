# QR Code Generator - Setup Guide

Up and running in minutes!

## Option 1: Use the EXE (Easiest) ⭐

1. **Clone this repository:**
   ```bash
   git clone https://github.com/JeffreyLebowsk1/QRcoder-v1.git
   ```

2. **Navigate to the dist folder** and double-click `QRCodeGenerator.exe`
   - That's it! No installation needed.

## Option 2: Build from Source

### Prerequisites
- **Python 3.8+** installed (download from [python.org](https://www.python.org))
- **Windows 7 or later**

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/JeffreyLebowsk1/QRcoder-v1.git
   cd QRcoder-v1
   ```

2. **Run the build script:**
   ```bash
   build.bat
   ```
   
   This will:
   - Install all Python dependencies from `requirements.txt`
   - Build a standalone EXE using PyInstaller
   - Create `dist/QRCodeGenerator.exe`

3. **Run the application:**
   ```bash
   dist/QRCodeGenerator.exe
   ```

### Manual Build (If build.bat doesn't work)

```bash
# Install dependencies
pip install -r requirements.txt

# Build using PyInstaller
pyinstaller --onefile --windowed --name "QRCodeGenerator" src/qr_generator.py

# Run
dist/QRCodeGenerator.exe
```

## Option 3: Run Directly from Python

```bash
pip install -r requirements.txt
python src/qr_generator.py
```

## Features Quick Start

- **Text/URL**: Enter text or URL and generate QR code instantly
- **Customize**: Control size, colors, error correction, and more
- **Preview**: See changes in real-time
- **Export**: Save as PNG or JPG
- **Logo**: Add images to your QR codes
- **vCard**: Generate contact QR codes
- **Calendar**: Create event QR codes

## System Requirements

- Windows 7 or later
- 50MB RAM minimum
- 100MB disk space for EXE
- No Python needed (for EXE version)

## Troubleshooting

### Build Script Fails
- Ensure Python is in your PATH: `python --version`
- Try `python.exe` instead of `python`
- Install pip: `python -m ensurepip`
- Update pip: `pip install --upgrade pip`

### Application Won't Start
- Try running as Administrator
- Check Windows Defender/Antivirus settings
- For source build: ensure all dependencies installed: `pip install -r requirements.txt`

### Logo Not Showing
- Use PNG, JPG, GIF, or BMP format
- Ensure file path is correct
- Try a smaller image size

## Project Structure

```
QRcoder-v1/
├── dist/                     # Pre-built executable
│   └── QRCodeGenerator.exe   # ⭐ Main application
├── src/                      # Python source code
│   ├── qr_generator.py       # Main GUI application
│   ├── qr_core.py            # Core QR generation logic
│   ├── api_server.py         # Web interface (optional)
│   └── ...
├── build.bat                 # Build script
├── run.bat                   # Quick launch script
├── requirements.txt          # Python dependencies
├── VERSION                   # Version info
├── CHANGELOG.md              # Version history
├── RELEASE_NOTES.md          # Release details
└── README.md                 # Features and usage
```

## Development

### Adding Features
1. Modify files in `src/` directory
2. Test with: `python src/qr_generator.py`
3. Rebuild EXE: `build.bat`

### Dependencies
All dependencies are listed in `requirements.txt`:
- `qrcode` - QR code generation
- `Pillow` - Image processing
- `pyinstaller` - EXE builder
- `fastapi` - Web server (optional)

## Support & Issues

Found a bug? Have a feature request?
- Check existing issues on GitHub
- Create a new issue with details
- Include screenshots if applicable

## Related Docs

- [README.md](README.md) - Feature overview
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [RELEASE_NOTES.md](RELEASE_NOTES.md) - Release information

## License

See LICENSE file in repository

---

**Happy QR code generating!** 🎉