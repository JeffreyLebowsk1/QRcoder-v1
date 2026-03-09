# Release Notes - Version 1.0.0

**Release Date**: March 9, 2025

## Overview

We are proud to present **QR Code Generator v1.0.0**, a comprehensive and feature-rich QR code generation application for Windows.

## What's New

This is the **initial release** featuring a complete QR code generator with both desktop GUI and web interfaces.

### 🎯 Key Features

#### Desktop GUI Application
- Intuitive tkinter-based interface
- Real-time QR code preview
- One-click save functionality (PNG/JPG)
- Standalone executable - no Python installation required

#### Customization & Design
- **Box Size Control**: Adjust QR code module size (1-40)
- **Border Configuration**: Customize quiet zone (0-20 pixels)
- **Error Correction**: Choose between 4 levels (7-30% recovery capacity)
- **Module Styles**: Square, Rounded, Circle, Gapped
- **Color Customization**: Pick any foreground/background color, Gradient support, Glow effects

#### Advanced Features
- **Logo Integration**: Embed logos in QR code center
- **vCard Support**: Generate contact QR codes
- **Calendar Support**: Generate calendar event QR codes
- **Web Interface**: FastAPI-based web server
- **Remote Access**: ngrok tunneling support

## Installation & Usage

### Option 1: Standalone Executable (Recommended)
1. Download QRCodeGenerator.exe
2. Double-click to run
3. No installation or Python needed

### Option 2: Run from Source
1. Download project
2. Run build.bat to create EXE
3. Use dist/QRCodeGenerator.exe

## System Requirements

- **Windows**: 7 or later
- **Memory**: 50MB minimum
- **Disk Space**: 100MB for standalone EXE
- **Additional**: No dependencies for EXE version

## Technical Stack

- **Python**: 3.8+
- **GUI**: tkinter
- **QR Generation**: qrcode library
- **Image Processing**: Pillow
- **Web Backend**: FastAPI (optional)
- **Packaging**: PyInstaller