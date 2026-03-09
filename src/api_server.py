"""
FastAPI backend for QR Code Generator with ngrok integration
"""
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import io
import os
import tempfile
import base64
from datetime import datetime
from qr_core import QRGeneratorCore


app = FastAPI(title="QR Code Generator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request models
class TextQRRequest(BaseModel):
    data: str
    box_size: int = 10
    border: int = 4
    outer_buffer: int = 0
    error_correction: str = "M"
    fg_color: str = "#000000"
    bg_color: str = "#FFFFFF"
    module_style: str = "square"
    module_corner_radius: int = 0
    bg_pattern: str = "solid"
    bg_gradient_type: str = "none"
    bg_gradient_color2: str = "#FFFFFF"
    bg_gradient_angle: int = 0
    fg_gradient: bool = False
    fg_gradient_color2: str = "#FFFFFF"
    glow_enabled: bool = False
    glow_radius: int = 2
    glow_intensity: int = 50
    glow_color: Optional[str] = None
    drop_shadow_enabled: bool = False
    drop_shadow_distance: int = 5
    drop_shadow_blur: int = 3
    drop_shadow_opacity: int = 50
    blur_background: bool = False
    blur_intensity: int = 2
    fade_effect: bool = False
    fade_intensity: int = 30
    frame_enabled: bool = False
    frame_width: int = 10
    frame_color: Optional[str] = None
    frame_pattern: str = "solid"
    logo_path: Optional[str] = None
    logo_size_percent: int = 30
    logo_border: int = 5
    logo_corner_radius: int = 0
    circular: bool = False
    eye_style: str = "standard"
    format: str = "png"  # png or svg


class VCardRequest(BaseModel):
    fn: str = ""
    ln: str = ""
    email: str = ""
    phone: str = ""
    org: str = ""
    title: str = ""
    website: str = ""
    street: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    country: str = ""
    bday: str = ""
    note: str = ""
    box_size: int = 10
    border: int = 4
    outer_buffer: int = 0
    error_correction: str = "M"
    fg_color: str = "#000000"
    bg_color: str = "#FFFFFF"
    module_style: str = "square"
    module_corner_radius: int = 0
    bg_pattern: str = "solid"
    bg_gradient_type: str = "none"
    bg_gradient_color2: str = "#FFFFFF"
    bg_gradient_angle: int = 0
    fg_gradient: bool = False
    fg_gradient_color2: str = "#FFFFFF"
    glow_enabled: bool = False
    glow_radius: int = 2
    glow_intensity: int = 50
    glow_color: Optional[str] = None
    drop_shadow_enabled: bool = False
    drop_shadow_distance: int = 5
    drop_shadow_blur: int = 3
    drop_shadow_opacity: int = 50
    blur_background: bool = False
    blur_intensity: int = 2
    fade_effect: bool = False
    fade_intensity: int = 30
    frame_enabled: bool = False
    frame_width: int = 10
    frame_color: Optional[str] = None
    frame_pattern: str = "solid"
    logo_path: Optional[str] = None
    logo_size_percent: int = 30
    logo_border: int = 5
    logo_corner_radius: int = 0
    circular: bool = False
    eye_style: str = "standard"
    format: str = "png"  # png or svg


class VCalRequest(BaseModel):
    title: str = ""
    description: str = ""
    location: str = ""
    organizer_name: str = ""
    organizer_email: str = ""
    start_date: str = ""
    start_time: str = ""
    end_date: str = ""
    end_time: str = ""
    url: str = ""
    categories: str = ""
    attendees: str = ""
    box_size: int = 10
    border: int = 4
    outer_buffer: int = 0
    error_correction: str = "M"
    fg_color: str = "#000000"
    bg_color: str = "#FFFFFF"
    module_style: str = "square"
    module_corner_radius: int = 0
    bg_pattern: str = "solid"
    bg_gradient_type: str = "none"
    bg_gradient_color2: str = "#FFFFFF"
    bg_gradient_angle: int = 0
    fg_gradient: bool = False
    fg_gradient_color2: str = "#FFFFFF"
    glow_enabled: bool = False
    glow_radius: int = 2
    glow_intensity: int = 50
    glow_color: Optional[str] = None
    drop_shadow_enabled: bool = False
    drop_shadow_distance: int = 5
    drop_shadow_blur: int = 3
    drop_shadow_opacity: int = 50
    blur_background: bool = False
    blur_intensity: int = 2
    fade_effect: bool = False
    fade_intensity: int = 30
    frame_enabled: bool = False
    frame_width: int = 10
    frame_color: Optional[str] = None
    frame_pattern: str = "solid"
    logo_path: Optional[str] = None
    logo_size_percent: int = 30
    logo_border: int = 5
    logo_corner_radius: int = 0
    circular: bool = False
    eye_style: str = "standard"
    format: str = "png"  # png or svg


# Routes
@app.get("/")
def root():
    """Serve the web interface HTML"""
    html_file = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_file):
        return FileResponse(html_file, media_type="text/html")
    return {"message": "QR Code Generator API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/api/qr/text")
def generate_text_qr(request: TextQRRequest):
    """Generate QR code from text/URL"""
    try:
        # Handle logo if provided
        logo_path = None
        if request.logo_path:
            try:
                # Decode base64 logo data
                import base64
                header, data = request.logo_path.split(',', 1)
                logo_bytes = base64.b64decode(data)
                # Save to temporary file
                logo_path = os.path.join(tempfile.gettempdir(), f"qr_logo_{datetime.now().timestamp()}.png")
                with open(logo_path, 'wb') as f:
                    f.write(logo_bytes)
            except Exception as e:
                print(f"Error processing logo: {e}")
                logo_path = None
        
        img = QRGeneratorCore.generate_qr_image(
            data=request.data,
            box_size=request.box_size,
            border=request.border,
            outer_buffer=request.outer_buffer,
            error_correction=request.error_correction,
            fg_color=request.fg_color,
            bg_color=request.bg_color,
            module_style=request.module_style,
            module_corner_radius=request.module_corner_radius,
            bg_pattern=request.bg_pattern,
            bg_gradient_type=request.bg_gradient_type,
            bg_gradient_color2=request.bg_gradient_color2,
            bg_gradient_angle=request.bg_gradient_angle,
            fg_gradient=request.fg_gradient,
            fg_gradient_color2=request.fg_gradient_color2,
            glow_enabled=request.glow_enabled,
            glow_radius=request.glow_radius,
            glow_intensity=request.glow_intensity,
            glow_color=request.glow_color,
            drop_shadow_enabled=request.drop_shadow_enabled,
            drop_shadow_distance=request.drop_shadow_distance,
            drop_shadow_blur=request.drop_shadow_blur,
            drop_shadow_opacity=request.drop_shadow_opacity,
            blur_background=request.blur_background,
            blur_intensity=request.blur_intensity,
            fade_effect=request.fade_effect,
            fade_intensity=request.fade_intensity,
            frame_enabled=request.frame_enabled,
            frame_width=request.frame_width,
            frame_color=request.frame_color,
            frame_pattern=request.frame_pattern,
            logo_path=logo_path,
            logo_size_percent=request.logo_size_percent,
            logo_border=request.logo_border,
            logo_corner_radius=request.logo_corner_radius,
            circular=request.circular,
            eye_style=request.eye_style
        )
        
        # Clean up temporary logo file
        if logo_path and os.path.exists(logo_path):
            try:
                os.remove(logo_path)
            except:
                pass
        
        img_bytes = QRGeneratorCore.image_to_bytes(img)
        return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/qr/vcard")
def generate_vcard_qr(request: VCardRequest):
    """Generate QR code from vCard data"""
    try:
        # Handle logo if provided
        logo_path = None
        if request.logo_path:
            try:
                # Decode base64 logo data
                header, data = request.logo_path.split(',', 1)
                logo_bytes = base64.b64decode(data)
                # Save to temporary file
                logo_path = os.path.join(tempfile.gettempdir(), f"qr_logo_{datetime.now().timestamp()}.png")
                with open(logo_path, 'wb') as f:
                    f.write(logo_bytes)
            except Exception as e:
                print(f"Error processing logo: {e}")
                logo_path = None
        
        vcard = QRGeneratorCore.generate_vcard(
            fn=request.fn,
            ln=request.ln,
            email=request.email,
            phone=request.phone,
            org=request.org,
            title=request.title,
            website=request.website,
            street=request.street,
            city=request.city,
            state=request.state,
            zip_code=request.zip_code,
            country=request.country,
            bday=request.bday,
            note=request.note
        )
        
        img = QRGeneratorCore.generate_qr_image(
            data=vcard,
            box_size=request.box_size,
            border=request.border,
            outer_buffer=request.outer_buffer,
            error_correction=request.error_correction,
            fg_color=request.fg_color,
            bg_color=request.bg_color,
            module_style=request.module_style,
            module_corner_radius=request.module_corner_radius,
            bg_pattern=request.bg_pattern,
            bg_gradient_type=request.bg_gradient_type,
            bg_gradient_color2=request.bg_gradient_color2,
            bg_gradient_angle=request.bg_gradient_angle,
            fg_gradient=request.fg_gradient,
            fg_gradient_color2=request.fg_gradient_color2,
            glow_enabled=request.glow_enabled,
            glow_radius=request.glow_radius,
            glow_intensity=request.glow_intensity,
            glow_color=request.glow_color,
            drop_shadow_enabled=request.drop_shadow_enabled,
            drop_shadow_distance=request.drop_shadow_distance,
            drop_shadow_blur=request.drop_shadow_blur,
            drop_shadow_opacity=request.drop_shadow_opacity,
            blur_background=request.blur_background,
            blur_intensity=request.blur_intensity,
            fade_effect=request.fade_effect,
            fade_intensity=request.fade_intensity,
            frame_enabled=request.frame_enabled,
            frame_width=request.frame_width,
            frame_color=request.frame_color,
            frame_pattern=request.frame_pattern,
            logo_path=logo_path,
            logo_size_percent=request.logo_size_percent,
            logo_border=request.logo_border,
            logo_corner_radius=request.logo_corner_radius,
            circular=request.circular,
            eye_style=request.eye_style
        )
        
        # Clean up temporary logo file
        if logo_path and os.path.exists(logo_path):
            try:
                os.remove(logo_path)
            except:
                pass
        
        img_bytes = QRGeneratorCore.image_to_bytes(img)
        return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/qr/vcal")
def generate_vcal_qr(request: VCalRequest):
    """Generate QR code from vCalendar data"""
    try:
        # Handle logo if provided
        logo_path = None
        if request.logo_path:
            try:
                # Decode base64 logo data
                header, data = request.logo_path.split(',', 1)
                logo_bytes = base64.b64decode(data)
                # Save to temporary file
                logo_path = os.path.join(tempfile.gettempdir(), f"qr_logo_{datetime.now().timestamp()}.png")
                with open(logo_path, 'wb') as f:
                    f.write(logo_bytes)
            except Exception as e:
                print(f"Error processing logo: {e}")
                logo_path = None
        
        vcal = QRGeneratorCore.generate_vcal(
            title=request.title,
            description=request.description,
            location=request.location,
            organizer_name=request.organizer_name,
            organizer_email=request.organizer_email,
            start_date=request.start_date,
            start_time=request.start_time,
            end_date=request.end_date,
            end_time=request.end_time,
            url=request.url,
            categories=request.categories,
            attendees=request.attendees
        )
        
        img = QRGeneratorCore.generate_qr_image(
            data=vcal,
            box_size=request.box_size,
            border=request.border,
            outer_buffer=request.outer_buffer,
            error_correction=request.error_correction,
            fg_color=request.fg_color,
            bg_color=request.bg_color,
            module_style=request.module_style,
            module_corner_radius=request.module_corner_radius,
            bg_pattern=request.bg_pattern,
            bg_gradient_type=request.bg_gradient_type,
            bg_gradient_color2=request.bg_gradient_color2,
            bg_gradient_angle=request.bg_gradient_angle,
            fg_gradient=request.fg_gradient,
            fg_gradient_color2=request.fg_gradient_color2,
            glow_enabled=request.glow_enabled,
            glow_radius=request.glow_radius,
            glow_intensity=request.glow_intensity,
            glow_color=request.glow_color,
            drop_shadow_enabled=request.drop_shadow_enabled,
            drop_shadow_distance=request.drop_shadow_distance,
            drop_shadow_blur=request.drop_shadow_blur,
            drop_shadow_opacity=request.drop_shadow_opacity,
            blur_background=request.blur_background,
            blur_intensity=request.blur_intensity,
            circular=request.circular,
            eye_style=request.eye_style,
            fade_effect=request.fade_effect,
            fade_intensity=request.fade_intensity,
            frame_enabled=request.frame_enabled,
            frame_width=request.frame_width,
            frame_color=request.frame_color,
            frame_pattern=request.frame_pattern,
            logo_path=logo_path,
            logo_size_percent=request.logo_size_percent,
            logo_border=request.logo_border,
            logo_corner_radius=request.logo_corner_radius
        )
        
        # Clean up temporary logo file
        if logo_path and os.path.exists(logo_path):
            try:
                os.remove(logo_path)
            except:
                pass
        
        img_bytes = QRGeneratorCore.image_to_bytes(img)
        return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/qr/text/base64")
def generate_text_qr_base64(request: TextQRRequest):
    """Generate QR code from text/URL and return as base64"""
    try:
        # Handle logo if provided
        logo_path = None
        if request.logo_path:
            try:
                # Decode base64 logo data
                header, data = request.logo_path.split(',', 1)
                logo_bytes = base64.b64decode(data)
                # Save to temporary file
                logo_path = os.path.join(tempfile.gettempdir(), f"qr_logo_{datetime.now().timestamp()}.png")
                with open(logo_path, 'wb') as f:
                    f.write(logo_bytes)
            except Exception as e:
                print(f"Error processing logo: {e}")
                logo_path = None
        
        img = QRGeneratorCore.generate_qr_image(
            data=request.data,
            box_size=request.box_size,
            border=request.border,
            outer_buffer=request.outer_buffer,
            error_correction=request.error_correction,
            fg_color=request.fg_color,
            bg_color=request.bg_color,
            module_style=request.module_style,
            module_corner_radius=request.module_corner_radius,
            bg_pattern=request.bg_pattern,
            bg_gradient_type=request.bg_gradient_type,
            bg_gradient_color2=request.bg_gradient_color2,
            bg_gradient_angle=request.bg_gradient_angle,
            fg_gradient=request.fg_gradient,
            fg_gradient_color2=request.fg_gradient_color2,
            glow_enabled=request.glow_enabled,
            glow_radius=request.glow_radius,
            glow_intensity=request.glow_intensity,
            glow_color=request.glow_color,
            drop_shadow_enabled=request.drop_shadow_enabled,
            drop_shadow_distance=request.drop_shadow_distance,
            drop_shadow_blur=request.drop_shadow_blur,
            drop_shadow_opacity=request.drop_shadow_opacity,
            blur_background=request.blur_background,
            blur_intensity=request.blur_intensity,
            fade_effect=request.fade_effect,
            fade_intensity=request.fade_intensity,
            frame_enabled=request.frame_enabled,
            frame_width=request.frame_width,
            frame_color=request.frame_color,
            frame_pattern=request.frame_pattern,
            logo_path=logo_path,
            logo_size_percent=request.logo_size_percent,
            logo_border=request.logo_border,
            logo_corner_radius=request.logo_corner_radius
        )
        
        # Clean up temporary logo file
        if logo_path and os.path.exists(logo_path):
            try:
                os.remove(logo_path)
            except:
                pass
        
        base64_str = QRGeneratorCore.get_base64_string(img)
        return {"base64": base64_str}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
