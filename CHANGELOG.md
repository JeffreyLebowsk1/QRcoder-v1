# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-03-09

### Added
- ✨ **Desktop GUI Application**: Full-featured tkinter-based interface for QR code generation
- 🎨 **Customization Options**:
  - Adjustable box size (1-40)
  - Configurable border/quiet zone (0-20)
  - Four error correction levels (Low, Medium, Quartile, High)
  - Multiple module styles (Square, Rounded, Circle, Gapped)
  - Custom foreground and background colors with color picker
  - Gradient color support
  - Glow effects
- 📸 **Logo Integration**: Add logos/images to QR code center with size and border adjustments
- 📝 **Text/URL Input**: Real-time QR code generation from text or URLs
- 🔍 **Live Preview**: Immediate visual preview of generated QR codes
- 💾 **Export Options**: Save as PNG or JPG with configurable output paths
- 🌐 **Web Interface** (Optional): FastAPI-based web server for QR code generation
- 🔐 **Ngrok Tunneling**: Optional remote access via ngrok tunnels
- 📦 **Standalone Executable**: PyInstaller-built EXE for easy distribution (no Python required)
- 🚀 **Auto Backup**: Automatic project backup functionality
- 📋 **vCard Support**: Generate QR codes for contact information
- 📅 **Calendar Support**: Generate QR codes for calendar events

### Features
- Standalone Windows EXE - no installation required
- Portable - copy executable anywhere
- Python source available for customization
- Dual interface (Desktop GUI + Web)
- Comprehensive error handling
- Professional GUI with intuitive controls

### Technical Details
- Python 3.8+ compatible
- Dependencies: qrcode, Pillow, tkinter (standard library)
- Optional: FastAPI, uvicorn for web interface, ngrok for tunneling
- Build system: PyInstaller for EXE generation

## Release Information

### Installation
- **Recommended**: Download `QRCodeGenerator.exe` and run directly
- **From Source**: Clone repository and run `build.bat` to create EXE

### Requirements
- Windows 7 or later
- No Python installation needed for EXE
- For source: Python 3.8+

### Known Limitations
- Desktop GUI available on Windows only
- Web interface available on Windows and Linux with Python installed

---

For more information, see [README.md](README.md) and [SETUP.md](SETUP.md)