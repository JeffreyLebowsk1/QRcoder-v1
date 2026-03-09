# QR Code Generator - Source Code Guide

This document guides you through the source code structure and main components.

## Core Components

### 1. **qr_generator.py** - Main GUI Application
**Location:** `src/qr_generator.py` (591 lines)

The main tkinter-based graphical user interface.

**Key Classes:**
- `QRCodeGenerator` - Main application window and logic

**Features In This File:**
- Text/URL, vCard, and vCalendar input tabs
- Real-time QR code preview
- Customization controls (box size, border, colors, styles)
- Logo integration
- Export options (PNG, JPG, SVG)
- Base64 export

**How to Use:**
```bash
python src/qr_generator.py
```

### 2. **qr_core.py** - Core QR Generation Logic
**Location:** `src/qr_core.py` (844 lines)

UI-independent QR code generation engine.

**Key Methods:**
- `generate_qr_image()` - Main QR generation with all customizations
- `generate_vcard()` - Create vCard format
- `generate_vcal()` - Create vCalendar format
- `generate_circular_qr_image()` - Circular QR codes
- `generate_qr_svg()` - SVG format output

**Features:**
- Advanced customization (colors, gradients, glows, shadows)
- Logo embedding
- Multiple module styles
- Background patterns
- Special effects

**Integration:**
Used by `qr_generator.py` and `api_server.py`

### 3. **api_server.py** - Web Interface (Optional)
**Location:** `src/api_server.py`

FastAPI-based web server for QR code generation.

**Endpoints:**
- `GET /` - Web interface
- `POST /api/qr/text` - Generate QR from text
- `POST /api/qr/vcard` - Generate vCard QR
- `POST /api/qr/vcal` - Generate calendar QR
- `POST /api/qr/text/base64` - Get Base64 output

**How to Run:**
```bash
pip install fastapi uvicorn
python src/start_web.py
```

### 4. **launcher.py** - Dual-Mode Launcher
**Location:** `src/launcher.py`

Choose between Desktop GUI or Web Interface at startup.

### 5. **ngrok_manager.py** - Remote Access
**Location:** `src/ngrok_manager.py`

Manages ngrok tunnels for remote QR generator access.

**Usage:**
```python
from ngrok_manager import NgrokTunnelManager

manager = NgrokTunnelManager(port=8000)
manager.start()
print(manager.public_url)
```

### 6. **start_web.py** - Web Server Launcher
**Location:** `src/start_web.py`

Starts the FastAPI server.

```bash
python src/start_web.py
```

### 7. **index.html** - Web UI
**Location:** `src/index.html`

Web interface for the QR code generator.

## Configuration Files

### requirements.txt
Python dependencies:
```
qrcode[pil]==8.0          # QR code generation
Pillow==10.1.0            # Image processing
pyinstaller==6.1.0        # EXE builder
fastapi==0.104.1          # Web framework
uvicorn[standard]==0.24.0 # Web server
pydantic==2.5.0           # Data validation
requests==2.31.0          # HTTP client
```

### build.bat
Automatic build script for creating EXE:
```batch
REM Install dependencies
pip install -r requirements.txt

REM Clean previous builds
rmdir /s /q build dist __pycache__

REM Build using PyInstaller
pyinstaller --onefile --windowed src/qr_generator.py
```

## Data Flow

```
┌─────────────────┐
│ User Input      │
│ (GUI/Web)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ qr_generator.py │  (GUI) or api_server.py (Web)
 │ or              │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ qr_core.py      │  ← Core logic
│ (QRGeneratorCore)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Output          │
│ (PNG/JPG/SVG)   │
└─────────────────┘
```

## Code Organization by Feature

### QR Generation
- `qr_core.py` - `QRGeneratorCore.generate_qr_image()`
- `qr_generator.py` - `QRCodeGenerator.generate_qr()`
- `api_server.py` - `/api/qr/text` endpoint

### User Input
- Text/URL: `qr_generator.py` lines 67-77 (Text Tab)
- vCard: `qr_generator.py` lines 79-103 (vCard Tab)
- Calendar: `qr_generator.py` lines 105-127 (vCalendar Tab)

### Customization
- Colors: `qr_generator.py` lines 298-313 (pick_fg_color, pick_bg_color)
- Styles: `qr_core.py` lines 146-189 (_draw_regular_module)
- Effects: `qr_core.py` lines 238-294 (glow, shadows, fade)

### Export
- PNG/JPG: `qr_generator.py` line 237 (save_qr)
- Base64: `qr_generator.py` line 253 (show_base64_options)
- SVG: `qr_core.py` line 795 (generate_qr_svg)

## Extending the Application

### Add a New Module Style
1. Edit `qr_core.py` - Update `_draw_regular_module()` method
2. Add new style case (e.g., "star", "hexagon")
3. Update UI in `qr_generator.py` - Add to module_style combobox

### Add API Endpoint
1. Edit `api_server.py`
2. Add new @app.post() function
3. Use `QRGeneratorCore` methods
4. Test with curl or Postman

### Add Web Feature
1. Update `src/index.html`
2. Import necessary JavaScript
3. Call API endpoints from HTML

## Testing

### Unit Testing
Create `test_qr_core.py`:
```python
from src.qr_core import QRGeneratorCore

def test_generate_qr():
    img = QRGeneratorCore.generate_qr_image(
        data="Test",
        box_size=10,
        border=4
    )
    assert img is not None
```

### Manual Testing
1. Run GUI: `python src/qr_generator.py`
2. Run Web: `python src/start_web.py` → http://localhost:8080
3. Test with various inputs and settings

## Performance Notes

- QR generation: ~50-100ms per image
- Large logos: Can slow down rendering
- Circular QR codes: More expensive than regular
- EXE startup: ~2-3 seconds on first run

## Dependencies Analysis

**Core Dependencies:**
- `qrcode` - QR encoding algorithm
- `Pillow` - Image manipulation
- `tkinter` - GUI (included with Python)

**Optional Dependencies:**
- `fastapi` - Only for web interface
- `uvicorn` - Only for web server
- `requests` - Only for fetching remote content
- `pyngrok` - Only for automatic ngrok tunneling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes in `src/` directory
4. Test locally: `python src/qr_generator.py`
5. Build EXE: `build.bat`
6. Submit pull request

## Debugging Tips

### Enable Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues
- **Logo not embedding:** Check image format and path
- **QR too small:** Increase `box_size` parameter
- **Export fails:** Ensure write permissions in target directory
- **Web interface timeout:** Check firewall settings

---

For more information, see [README.md](README.md) and [SETUP.md](SETUP.md)