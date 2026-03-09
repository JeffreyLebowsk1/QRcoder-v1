# QR Code Generator

A feature-rich Windows QR code generator with a simple GUI. Generate and customize QR codes with visual preview and immediate save functionality.

## Features

✨ **Core Features:**
- Text/URL input with real-time QR generation
- Live preview of generated QR codes
- One-click save to PNG/JPG
- No installation required (standalone EXE)

🎨 **Customization Options:**
- **Box Size**: Control the size of individual QR code modules (1-40)
- **Border**: Adjust the quiet zone around the QR code (0-20)
- **Error Correction**: Choose between Low (7%), Medium (15%), Quartile (25%), or High (30%)
- **Module Styles**: Square, Rounded, Circle, or Gapped designs
- **Foreground Color**: Pick any color for the QR code modules (with visual color picker)
- **Background Color**: Pick any color for the background (with visual color picker)

📸 **Logo Integration:**
- Add a logo/image to the center of your QR code
- Logo size adjustment (10-50% of QR code)
- Logo border customization (0-20px white border around logo)
- Support for PNG, JPG, GIF, BMP formats

## Quick Start

### Running from EXE (No Installation Needed)

1. Double-click `QRCodeGenerator.exe` in the `dist` folder
2. Enter text or URL
3. Customize settings as desired
4. Click "Save QR Code" to export

### Building from Source

**Prerequisites:**
- Python 3.8 or higher
- Windows operating system

**Steps:**

1. Download and extract the project
2. Double-click `build.bat` to automatically:
   - Install all required dependencies
   - Build the standalone EXE
   - Create `dist/QRCodeGenerator.exe`

**Manual Build (if build.bat doesn't work):**