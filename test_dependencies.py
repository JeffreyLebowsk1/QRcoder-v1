"""
QR Code Generator - Dependency Test Script
Run this on the target Windows 11 laptop to diagnose issues
"""

import sys
print("=" * 70)
print("QR CODE GENERATOR - DEPENDENCY TEST")
print("=" * 70)

print(f"\nPython Version: {sys.version}")
print(f"Platform: {sys.platform}")

# Test Core GUI Dependencies
print("\n[1/4] Testing Core GUI Dependencies...")
errors = []

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, colorchooser, scrolledtext
    print("  ✓ tkinter - OK")
    
    # Test if tkinter works
    root = tk.Tk()
    root.withdraw()
    root.destroy()
    print("  ✓ tkinter GUI initialization - OK")
except Exception as e:
    print(f"  ✗ tkinter - FAILED: {e}")
    errors.append(("tkinter", str(e)))

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
    print("  ✓ PIL (Pillow) - OK")
    
    # Test image creation
    img = Image.new('RGB', (100, 100), color='white')
    print("  ✓ PIL image creation - OK")
except Exception as e:
    print(f"  ✗ PIL - FAILED: {e}")
    errors.append(("PIL", str(e)))

try:
    import qrcode
    import qrcode.image.svg
    from qrcode.image.styles.moduledrawers import CircleModuleDrawer, SquareModuleDrawer, RoundedModuleDrawer
    from qrcode.image.styles.colormasks import SolidFillColorMask
    from qrcode.image.styledpil import StyledPilImage
    print("  ✓ qrcode and submodules - OK")
    
    # Test QR generation
    qr = qrcode.QRCode()
    qr.add_data("Test")
    qr.make()
    img = qr.make_image(fill_color="black", back_color="white")
    print("  ✓ QR code generation - OK")
except Exception as e:
    print(f"  ✗ qrcode - FAILED: {e}")
    errors.append(("qrcode", str(e)))

# Test Web Server Dependencies
print("\n[2/4] Testing Web Server Dependencies (optional)...")

try:
    import fastapi
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import FileResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    print("  ✓ FastAPI - OK")
except Exception as e:
    print(f"  ✗ FastAPI - FAILED: {e}")
    errors.append(("FastAPI", str(e)))

try:
    import uvicorn
    print("  ✓ Uvicorn - OK")
except Exception as e:
    print(f"  ✗ Uvicorn - FAILED: {e}")
    errors.append(("Uvicorn", str(e)))

try:
    import pydantic
    from pydantic import BaseModel
    import pydantic_core
    print("  ✓ Pydantic - OK")
except Exception as e:
    print(f"  ✗ Pydantic - FAILED: {e}")
    errors.append(("Pydantic", str(e)))

# Test Standard Library
print("\n[3/4] Testing Standard Library Modules...")

try:
    import base64, io, os, pathlib, datetime
    import subprocess, time, json, threading
    import webbrowser, signal, tempfile
    print("  ✓ All standard library modules - OK")
except Exception as e:
    print(f"  ✗ Standard library - FAILED: {e}")
    errors.append(("stdlib", str(e)))

# Test Application Core Files
print("\n[4/4] Testing Application Core Files...")

try:
    from qr_core import QRGeneratorCore
    print("  ✓ qr_core module - OK")
    
    # Test core QR generation
    img = QRGeneratorCore.generate_qr_image("Test QR Code")
    print("  ✓ QRGeneratorCore.generate_qr_image - OK")
except Exception as e:
    print(f"  ✗ qr_core - FAILED: {e}")
    errors.append(("qr_core", str(e)))

# Summary
print("\n" + "=" * 70)
if not errors:
    print("✅ ALL TESTS PASSED - Application should work correctly!")
else:
    print(f"❌ {len(errors)} ERROR(S) FOUND:")
    print("\nDetails:")
    for module, error in errors:
        print(f"\n  Module: {module}")
        print(f"  Error: {error}")
    
    print("\n" + "=" * 70)
    print("TROUBLESHOOTING SUGGESTIONS:")
    print("=" * 70)
    
    if any("tkinter" in m for m, _ in errors):
        print("\n🔧 tkinter Issues:")
        print("   - Ensure Python was installed with tkinter support")
        print("   - Try: python -m tkinter (should open a test window)")
    
    if any("PIL" in m for m, _ in errors):
        print("\n🔧 PIL/Pillow Issues:")
        print("   - Run: pip install --upgrade Pillow")
        print("   - May need Visual C++ redistributable")
    
    if any("qrcode" in m for m, _ in errors):
        print("\n🔧 qrcode Issues:")
        print("   - Run: pip install qrcode[pil]")
    
    if any(m in ["FastAPI", "Uvicorn", "Pydantic"] for m, _ in errors):
        print("\n🔧 Web Server Issues (Optional):")
        print("   - These are only needed for web interface mode")
        print("   - Desktop GUI will still work without them")
        print("   - Run: pip install fastapi uvicorn pydantic")

print("\n" + "=" * 70)
print("Test completed. Press Enter to exit...")
input()
