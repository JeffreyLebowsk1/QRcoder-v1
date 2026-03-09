@echo off
REM QR Code Generator - Build Script for Windows
REM This script will create a standalone EXE

echo ===============================================
echo QR Code Generator - Building EXE
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

echo.
echo [3/4] Building EXE...
pyinstaller --onefile --windowed --name "QRCodeGenerator" ^
  --hidden-import=uvicorn ^
  --hidden-import=uvicorn.logging ^
  --hidden-import=uvicorn.loops ^
  --hidden-import=uvicorn.loops.auto ^
  --hidden-import=uvicorn.protocols ^
  --hidden-import=uvicorn.protocols.http ^
  --hidden-import=uvicorn.protocols.http.auto ^
  --hidden-import=uvicorn.protocols.websockets ^
  --hidden-import=uvicorn.protocols.websockets.auto ^
  --hidden-import=uvicorn.lifespan ^
  --hidden-import=uvicorn.lifespan.on ^
  --hidden-import=fastapi ^
  --hidden-import=starlette ^
  --hidden-import=starlette.routing ^
  --hidden-import=pydantic ^
  --hidden-import=pydantic_core ^
  --hidden-import=qrcode ^
  --hidden-import=PIL ^
  --hidden-import=PIL._tkinter_finder ^
  --collect-data=uvicorn ^
  --copy-metadata=uvicorn ^
  --copy-metadata=fastapi ^
  --copy-metadata=starlette ^
  --copy-metadata=pydantic ^
  --noupx ^
  src/qr_generator.py

echo.
if exist dist\QRCodeGenerator.exe (
    echo [4/4] Success!
    echo.
    echo ===============================================
    echo EXE created successfully!
    echo Location: dist\QRCodeGenerator.exe
    echo ===============================================
    echo.
    echo You can now run: dist\QRCodeGenerator.exe
    pause
) else (
    echo Error: Failed to create EXE
    pause
    exit /b 1
)