"""
Core QR Code generation logic (UI-independent)
"""
import qrcode
import qrcode.image.svg
from qrcode.image.styles.moduledrawers import CircleModuleDrawer, SquareModuleDrawer, RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styledpil import StyledPilImage
try:
    from qrcode.image.styles.eyes import RoundedEyeDrawer
except ImportError:
    RoundedEyeDrawer = None
from PIL import Image, ImageDraw, ImageFilter
import base64
import io
from datetime import datetime


class QRGeneratorCore:
    """Pure QR code generation logic without UI dependencies"""
    
    @staticmethod
    def generate_qr_image(
        data,
        box_size=10,
        border=4,
        outer_buffer=0,
        error_correction="M",
        fg_color="#000000",
        bg_color="#FFFFFF",
        module_style="square",
        module_corner_radius=0,
        bg_pattern="solid",
        bg_gradient_type="none",
        bg_gradient_color2="#FFFFFF",
        bg_gradient_angle=0,
        fg_gradient=False,
        fg_gradient_color2="#FFFFFF",
        glow_enabled=False,
        glow_radius=2,
        glow_intensity=50,
        glow_color=None,
        drop_shadow_enabled=False,
        drop_shadow_distance=5,
        drop_shadow_blur=3,
        drop_shadow_opacity=50,
        blur_background=False,
        blur_intensity=2,
        fade_effect=False,
        fade_intensity=30,
        frame_enabled=False,
        frame_width=10,
        frame_color=None,
        frame_pattern="solid",
        logo_path=None,
        logo_size_percent=30,
        logo_border=5,
        logo_corner_radius=0,
        circular=False,
        eye_style="standard"
    ):
        """Generate a complete QR code image with all customizations"""
        
        # Use circular QR generation if requested
        if circular:
            # For circular QR, default border to 16 and drawer to circle module style
            if border == 4:  # Default unchanged border
                border = 16
            return QRGeneratorCore.generate_circular_qr_image(
                data=data,
                box_size=box_size,
                border=border,
                outer_buffer=outer_buffer,
                error_correction=error_correction,
                fg_color=fg_color,
                bg_color=bg_color,
                eye_style=eye_style if eye_style != "standard" else "rounded",
                logo_path=logo_path,
                logo_size_percent=logo_size_percent,
                logo_border=logo_border,
                logo_corner_radius=logo_corner_radius
            )
        
        # Handle transparent background
        is_transparent = bg_color.lower() == 'transparent'
        if is_transparent:
            bg_color = "#FFFFFF"  # Use white as placeholder, will make transparent later
        
        # Generate base QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{error_correction}"),
            box_size=box_size,
            border=border
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Render the QR code
        modules = qr.modules
        qr_size = len(modules) * box_size
        
        # Create image with outer buffer
        if outer_buffer > 0:
            final_size = qr_size + 2 * outer_buffer
            if is_transparent:
                img = Image.new("RGBA", (final_size, final_size), (255, 255, 255, 0))
                qr_img = Image.new("RGBA", (qr_size, qr_size), (255, 255, 255, 0))
            else:
                img = Image.new("RGB", (final_size, final_size), bg_color)
                qr_img = Image.new("RGB", (qr_size, qr_size), bg_color)
        else:
            if is_transparent:
                img = Image.new("RGBA", (qr_size, qr_size), (255, 255, 255, 0))
                qr_img = img
            else:
                img = Image.new("RGB", (qr_size, qr_size), bg_color)
                qr_img = img
        
        # Apply background pattern or gradient
        if bg_gradient_type != "none":
            QRGeneratorCore._apply_gradient_background(
                qr_img, qr_size, bg_gradient_type, bg_color, bg_gradient_color2, bg_gradient_angle
            )
        elif not is_transparent:
            QRGeneratorCore._apply_background_pattern(qr_img, qr_size, bg_pattern, box_size, bg_color)
        
        draw = ImageDraw.Draw(qr_img)
        
        size = len(modules)
        
        # Draw all modules - the qrcode library already has correct corner patterns in modules array
        for y, row in enumerate(modules):
            for x, is_dark in enumerate(row):
                if is_dark:
                    x0 = x * box_size
                    y0 = y * box_size
                    x1 = x0 + box_size
                    y1 = y0 + box_size
                    
                    # Get module color (gradient if enabled)
                    module_color = QRGeneratorCore._get_module_color(
                        x, y, size, fg_gradient, fg_color, fg_gradient_color2
                    )
                    
                    QRGeneratorCore._draw_regular_module(draw, x0, y0, x1, y1, module_color, module_style, module_corner_radius)
        
        # Apply blur effect to background if enabled
        if blur_background and not is_transparent:
            qr_img = QRGeneratorCore._apply_background_blur(qr_img, blur_intensity)
        
        # Apply glow effect if enabled
        if glow_enabled:
            glow_col = glow_color if glow_color else fg_color
            if is_transparent:
                qr_img = QRGeneratorCore._apply_glow_effect(qr_img, glow_radius, glow_intensity, "#00000000", glow_col)
            else:
                qr_img = QRGeneratorCore._apply_glow_effect(qr_img, glow_radius, glow_intensity, bg_color, glow_col)
        
        # Apply drop shadow if enabled
        if drop_shadow_enabled:
            qr_img = QRGeneratorCore._apply_drop_shadow(qr_img, drop_shadow_distance, drop_shadow_blur, drop_shadow_opacity)
        
        # Apply fade effect if enabled
        if fade_effect and not is_transparent:
            qr_img = QRGeneratorCore._apply_fade_effect(qr_img, fade_intensity)
        
        # Paste QR code onto outer buffer if needed
        if outer_buffer > 0:
            if is_transparent:
                img.paste(qr_img, (outer_buffer, outer_buffer), qr_img)
            else:
                img.paste(qr_img, (outer_buffer, outer_buffer))
            final_img = img
        else:
            final_img = qr_img
        
        # Add decorative frame if enabled
        if frame_enabled:
            frame_col = frame_color if frame_color else fg_color
            final_img = QRGeneratorCore._add_frame(final_img, frame_width, frame_col, frame_pattern, bg_color)
        
        # Add logo if provided
        if logo_path:
            final_img = QRGeneratorCore._add_logo_to_qr(
                final_img, logo_path, logo_size_percent, logo_border, 
                logo_corner_radius, fg_color
            )
        
        return final_img
    

    @staticmethod
    def _draw_regular_module(draw, x0, y0, x1, y1, fg, style, corner_radius=0):
        """Draw a regular (non-corner) module with various styles"""
        width = x1 - x0
        height = y1 - y0
        
        if style == "square":
            if corner_radius > 0:
                draw.rounded_rectangle([x0, y0, x1-1, y1-1], radius=corner_radius, fill=fg)
            else:
                draw.rectangle([x0, y0, x1, y1], fill=fg)
        elif style == "circle":
            draw.ellipse([x0, y0, x1, y1], fill=fg)
        elif style == "diamond":
            points = [
                (x0 + width//2, y0),      # top
                (x1, y0 + height//2),     # right
                (x0 + width//2, y1),      # bottom
                (x0, y0 + height//2)      # left
            ]
            draw.polygon(points, fill=fg)
        elif style == "star":
            cx, cy = x0 + width//2, y0 + height//2
            r = width // 3
            points = []
            for i in range(10):
                angle = i * 3.14159 / 5
                if i % 2 == 0:
                    rx, ry = r, r
                else:
                    rx, ry = r // 2, r // 2
                x = cx + int(rx * __import__('math').cos(angle))
                y = cy + int(ry * __import__('math').sin(angle))
                points.append((x, y))
            draw.polygon(points, fill=fg)
        elif style == "hexagon":
            cx, cy = x0 + width//2, y0 + height//2
            r = width // 2.5
            points = []
            for i in range(6):
                angle = i * 3.14159 / 3
                x = cx + int(r * __import__('math').cos(angle))
                y = cy + int(r * __import__('math').sin(angle))
                points.append((x, y))
            draw.polygon(points, fill=fg)
        elif style == "gapped":
            margin = width // 4
            if corner_radius > 0:
                draw.rounded_rectangle([x0 + margin, y0 + margin, x1 - margin - 1, y1 - margin - 1], 
                                       radius=corner_radius, fill=fg)
            else:
                draw.rectangle([x0 + margin, y0 + margin, x1 - margin, y1 - margin], fill=fg)
    

    @staticmethod
    def _apply_background_pattern(img, size, pattern, box_size, bg_color):
        """Apply background patterns to the QR code"""
        if pattern == "solid":
            return
        
        draw = ImageDraw.Draw(img)
        
        if pattern == "stripes":
            stripe_width = box_size * 2
            for x in range(0, size, stripe_width * 2):
                draw.rectangle([x, 0, x + stripe_width, size], fill=QRGeneratorCore._darken_color(bg_color, 0.95))
        
        elif pattern == "dots":
            dot_spacing = box_size * 3
            dot_size = box_size
            for x in range(0, size, dot_spacing):
                for y in range(0, size, dot_spacing):
                    draw.ellipse([x, y, x + dot_size, y + dot_size], fill=QRGeneratorCore._darken_color(bg_color, 0.93))
        
        elif pattern == "grid":
            grid_spacing = box_size * 4
            for x in range(0, size, grid_spacing):
                draw.line([x, 0, x, size], fill=QRGeneratorCore._darken_color(bg_color, 0.90), width=1)
            for y in range(0, size, grid_spacing):
                draw.line([0, y, size, y], fill=QRGeneratorCore._darken_color(bg_color, 0.90), width=1)
    
    @staticmethod
    def _darken_color(hex_color, factor):
        """Darken a hex color by a given factor (0-1)"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    @staticmethod
    def _get_module_color(x, y, size, fg_gradient, fg_color, fg_gradient_color2):
        """Get the color for a module, applying gradient if enabled"""
        if not fg_gradient:
            return fg_color
        
        max_dist = (size ** 2 + size ** 2) ** 0.5
        current_dist = (x ** 2 + y ** 2) ** 0.5
        ratio = current_dist / max_dist
        
        return QRGeneratorCore._interpolate_color(fg_color, fg_gradient_color2, ratio)
    
    @staticmethod
    def _interpolate_color(color1, color2, ratio):
        """Interpolate between two hex colors"""
        hex1 = color1.lstrip('#')
        hex2 = color2.lstrip('#')
        r1, g1, b1 = tuple(int(hex1[i:i+2], 16) for i in (0, 2, 4))
        r2, g2, b2 = tuple(int(hex2[i:i+2], 16) for i in (0, 2, 4))
        
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    @staticmethod
    def _apply_glow_effect(img, glow_radius, glow_intensity, bg_color, glow_color=None):
        """Apply a glow/shadow effect to the QR code with optional color tinting"""
        if glow_color is None:
            glow_color = bg_color
        
        # Create glow layer
        glow = img.filter(ImageFilter.GaussianBlur(radius=glow_radius))
        
        # If glow_color is specified, tint the glow
        if glow_color != bg_color and glow_color != "#00000000":
            hex_color = glow_color.lstrip('#')
            if len(hex_color) == 6:
                r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                glow_pixels = glow.load()
                for y in range(glow.size[1]):
                    for x in range(glow.size[0]):
                        if img.mode == 'RGBA':
                            _, _, _, a = glow_pixels[x, y]
                        else:
                            a = 255
                        glow_pixels[x, y] = (r, g, b, int(a * glow_intensity / 100.0))
        else:
            blend_alpha = int(255 * glow_intensity / 100.0)
            if glow.mode != 'RGBA':
                glow = glow.convert('RGBA')
            glow.putalpha(blend_alpha)
        
        # Blend glow back
        result = Image.new("RGBA", img.size, (0, 0, 0, 0))
        result.paste(glow, (0, 0), glow if glow.mode == 'RGBA' else None)
        
        if img.mode == 'RGBA':
            result.paste(img, (0, 0), img)
        else:
            img_rgba = img.convert('RGBA')
            result.paste(img_rgba, (0, 0), img_rgba)
        
        return result
    
    @staticmethod
    def _apply_gradient_background(img, size, gradient_type, color1, color2, angle):
        """Apply a gradient background to the image"""
        gradient_img = Image.new('RGB', (size, size))
        pixels = gradient_img.load()
        
        # Parse colors
        hex1 = color1.lstrip('#')
        hex2 = color2.lstrip('#')
        r1, g1, b1 = tuple(int(hex1[i:i+2], 16) for i in (0, 2, 4))
        r2, g2, b2 = tuple(int(hex2[i:i+2], 16) for i in (0, 2, 4))
        
        if gradient_type == "linear":
            # Simple linear gradient (top to bottom by default, can be rotated)
            for y in range(size):
                ratio = y / size
                r = int(r1 + (r2 - r1) * ratio)
                g = int(g1 + (g2 - g1) * ratio)
                b = int(b1 + (b2 - b1) * ratio)
                for x in range(size):
                    pixels[x, y] = (r, g, b)
        
        elif gradient_type == "radial":
            # Radial gradient from center outward
            center_x, center_y = size // 2, size // 2
            max_dist = ((size // 2) ** 2 + (size // 2) ** 2) ** 0.5
            
            for y in range(size):
                for x in range(size):
                    dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                    ratio = min(1.0, dist / max_dist)
                    r = int(r1 + (r2 - r1) * ratio)
                    g = int(g1 + (g2 - g1) * ratio)
                    b = int(b1 + (b2 - b1) * ratio)
                    pixels[x, y] = (r, g, b)
        
        # Blend gradient with original
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, size-1, size-1], fill=(r1, g1, b1))
        
        # Apply gradient with transparency so QR modules show through
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            gradient_img = gradient_img.convert('RGBA')
            gradient_img.putalpha(200)  # Semi-transparent gradient
            img.paste(gradient_img, (0, 0), gradient_img)
    
    @staticmethod
    def _apply_background_blur(img, blur_intensity):
        """Apply blur effect to background only"""
        # This is a subtle effect applied after the QR code modules are drawn
        return img.filter(ImageFilter.GaussianBlur(radius=blur_intensity))
    
    @staticmethod
    def _apply_drop_shadow(img, distance, blur_radius, opacity):
        """Apply drop shadow effect"""
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create shadow layer
        shadow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)
        
        # Create dark area for shadow
        shadow_color = (0, 0, 0, int(255 * opacity / 100.0))
        shadow_draw.rectangle([distance, distance, img.size[0], img.size[1]], fill=shadow_color)
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        # Composite shadow behind image
        result = Image.new('RGBA', img.size, (0, 0, 0, 0))
        result.paste(shadow_layer, (0, 0))
        result.paste(img, (0, 0), img)
        
        return result
    
    @staticmethod
    def _apply_fade_effect(img, fade_intensity):
        """Apply fade effect (edges fade into background)"""
        fade_mask = Image.new('L', img.size, 255)
        fade_draw = ImageDraw.Draw(fade_mask)
        
        fade_width = int(img.size[0] * fade_intensity / 100.0)
        # Create gradient fade mask from edges
        for i in range(fade_width):
            alpha = int(255 * (1 - i / fade_width))
            fade_draw.rectangle([i, 0, i+1, img.size[1]], fill=alpha)
            fade_draw.rectangle([img.size[0]-i-1, 0, img.size[0]-i, img.size[1]], fill=alpha)
            fade_draw.rectangle([0, i, img.size[0], i+1], fill=alpha)
            fade_draw.rectangle([0, img.size[1]-i-1, img.size[0], img.size[1]-i], fill=alpha)
        
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        img.putalpha(fade_mask)
        return img
    
    @staticmethod
    def _add_frame(img, frame_width, frame_color, frame_pattern, bg_color):
        """Add decorative frame around the QR code"""
        new_size = (img.size[0] + 2 * frame_width, img.size[1] + 2 * frame_width)
        
        if img.mode == 'RGBA':
            framed = Image.new('RGBA', new_size, (255, 255, 255, 0))
        else:
            framed = Image.new('RGB', new_size, bg_color)
        
        # Draw frame
        draw = ImageDraw.Draw(framed)
        
        if frame_pattern == "solid":
            hex_color = frame_color.lstrip('#')
            frame_rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            draw.rectangle([0, 0, new_size[0]-1, new_size[1]-1], outline=frame_rgb, width=frame_width)
        elif frame_pattern == "dashed":
            hex_color = frame_color.lstrip('#')
            frame_rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            # Draw dashed frame
            dash_size = 10
            for i in range(0, new_size[0], dash_size * 2):
                draw.line([i, 0, min(i + dash_size, new_size[0]), 0], fill=frame_rgb, width=frame_width)
                draw.line([i, new_size[1]-frame_width, min(i + dash_size, new_size[0]), new_size[1]-frame_width], fill=frame_rgb, width=frame_width)
            for i in range(0, new_size[1], dash_size * 2):
                draw.line([0, i, 0, min(i + dash_size, new_size[1])], fill=frame_rgb, width=frame_width)
                draw.line([new_size[0]-frame_width, i, new_size[0]-frame_width, min(i + dash_size, new_size[1])], fill=frame_rgb, width=frame_width)
        
        # Paste original image centered on frame
        framed.paste(img, (frame_width, frame_width), img if img.mode == 'RGBA' else None)
        
        return framed
    
    
    @staticmethod
    def _add_logo_to_qr(qr_img, logo_path, logo_size_percent, logo_border, logo_corner_radius, fg_color):
        """Add a logo to the center of the QR code"""
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_size = int(min(qr_img.size) * logo_size_percent / 100)
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Apply corner rounding
            if logo_corner_radius > 0:
                logo = QRGeneratorCore._round_corners(logo, logo_corner_radius)
            
            # Create bordered version
            if logo_border > 0:
                bordered_size = logo_size + 2 * logo_border
                fg_rgb = tuple(int(fg_color[i:i+2], 16) for i in (1, 3, 5))
                bordered = Image.new("RGBA", (bordered_size, bordered_size), fg_rgb + (255,))
                
                if logo_corner_radius > 0:
                    bordered = QRGeneratorCore._round_corners(bordered, logo_corner_radius + logo_border)
                
                bordered.paste(logo, (logo_border, logo_border), logo)
                logo = bordered
            
            # Position logo in center
            final_size = logo_size + 2 * logo_border
            pos = ((qr_img.size[0] - final_size) // 2, (qr_img.size[1] - final_size) // 2)
            qr_img.paste(logo, pos, logo)
            return qr_img
        except Exception as e:
            print(f"Logo embedding failed: {str(e)}")
            return qr_img
    
    @staticmethod
    def _round_corners(img, radius):
        """Create rounded corners on an image"""
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
        
        output = Image.new('RGBA', img.size, (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        return output
    
    @staticmethod
    def generate_vcard(fn="", ln="", email="", phone="", org="", title="", website="",
                      street="", city="", state="", zip_code="", country="", bday="", note=""):
        """Generate a vCard 4.0 string"""
        vcard = "BEGIN:VCARD\nVERSION:4.0\n"
        
        if fn or ln:
            n_parts = [ln or "", fn or "", "", "", ""]
            vcard += f"N:{';'.join(n_parts)}\n"
            vcard += f"FN:{fn} {ln}".strip() + "\n"
        
        if email:
            vcard += f"EMAIL:{email}\n"
        if phone:
            vcard += f"TEL:{phone}\n"
        if org:
            vcard += f"ORG:{org}\n"
        if title:
            vcard += f"TITLE:{title}\n"
        if website:
            vcard += f"URL:{website}\n"
        if street or city or state or zip_code or country:
            adr_parts = ["", "", street or "", city or "", state or "", zip_code or "", country or ""]
            vcard += f"ADR:{';'.join(adr_parts)}\n"
        if bday:
            vcard += f"BDAY:{bday}\n"
        if note:
            vcard += f"NOTE:{note}\n"
        
        vcard += "END:VCARD"
        return vcard
    
    @staticmethod
    def generate_vcal(title="", description="", location="", organizer_name="", organizer_email="",
                     start_date="", start_time="", end_date="", end_time="", url="",
                     categories="", attendees=""):
        """Generate a vCalendar 2.0 string"""
        uid = f"uid-{int(datetime.now().timestamp())}"
        dtstamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        
        vcal = "BEGIN:VCALENDAR\nVERSION:2.0\n"
        vcal += "PRODID:-//QR Code Generator//EN\n"
        vcal += "BEGIN:VEVENT\n"
        vcal += f"UID:{uid}\n"
        vcal += f"DTSTAMP:{dtstamp}\n"
        
        if title:
            vcal += f"SUMMARY:{title}\n"
        if description:
            vcal += f"DESCRIPTION:{description}\n"
        if location:
            vcal += f"LOCATION:{location}\n"
        if organizer_name:
            organizer = f"ORGANIZER;CN={organizer_name}"
            if organizer_email:
                organizer += f":mailto:{organizer_email}"
            vcal += organizer + "\n"
        if start_date:
            st = f"{start_date.replace('-', '')}"
            if start_time:
                st += f"T{start_time.replace(':', '')}"
            vcal += f"DTSTART:{st}\n"
        if end_date:
            et = f"{end_date.replace('-', '')}"
            if end_time:
                et += f"T{end_time.replace(':', '')}"
            vcal += f"DTEND:{et}\n"
        if url:
            vcal += f"URL:{url}\n"
        if categories:
            vcal += f"CATEGORIES:{categories}\n"
        if attendees:
            for attendee in attendees.split(","):
                vcal += f"ATTENDEE:mailto:{attendee.strip()}\n"
        
        vcal += "END:VEVENT\n"
        vcal += "END:VCALENDAR"
        return vcal
    
    @staticmethod
    def get_base64_string(image):
        """Convert PIL Image to base64 string"""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_data = base64.b64encode(buffer.getvalue()).decode()
        return img_data
    
    @staticmethod
    def image_to_bytes(image, format="PNG"):
        """Convert PIL Image to bytes"""
        buffer = io.BytesIO()
        if format.upper() == "SVG":
            # For SVG, convert to SVG string and return as bytes
            svg_data = image.tobytes() if hasattr(image, 'tobytes') else str(image)
            return svg_data.encode() if isinstance(svg_data, str) else svg_data
        else:
            # Handle transparent PNG
            if format.upper() == "PNG" and image.mode == "RGBA":
                image.save(buffer, format="PNG")
            else:
                image.save(buffer, format=format or "PNG")
        return buffer.getvalue()
    
    @staticmethod
    def generate_circular_qr_image(
        data,
        box_size=14,  # ← Increased from 10 for bigger QR
        border=10,    # ← Reduced from 16 for tighter frame
        outer_buffer=0,
        error_correction="M",
        fg_color="#000000",
        bg_color="#FFFFFF",
        eye_style="rounded",
        logo_path=None,
        logo_size_percent=30,
        logo_border=5,
        logo_corner_radius=0
    ):
        """Generate a circular QR code using Brenton Mallen's method with proper drawer separation.
        - CircleModuleDrawer for data blocks (smooth circles)
        - RoundedEyeDrawer only for finder patterns (rounded corners on eyes)
        - Tighter circular frame with minimal gap"""
        
        # Handle transparent background
        is_transparent = bg_color.lower() == 'transparent'
        if is_transparent:
            bg_color = "#FFFFFF"
        
        # Convert hex colors to RGB tuples and PIL color strings
        bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
        fg_rgb = tuple(int(fg_color[i:i+2], 16) for i in (1, 3, 5))
        
        # Generate base QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{error_correction}"),
            box_size=box_size,
            border=border
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Try to use styled drawers if available
        try:
            # Use CircleModuleDrawer for smooth circular modules
            module_drawer = CircleModuleDrawer()
            
            # Use RoundedEyeDrawer only for finder patterns
            eye_drawer = None
            if eye_style == "rounded" and RoundedEyeDrawer:
                eye_drawer = RoundedEyeDrawer(radius_ratio=0.5)
            
            # Create styled QR image with separate module and eye styling
            qr_img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=module_drawer,
                eye_drawer=eye_drawer,
                color_mask=SolidFillColorMask(front_color=fg_color, back_color=bg_color)
            )
        except Exception as e:
            # Fallback to standard QR if styled drawers fail
            qr_img = qr.make_image(fill_color=fg_color, back_color=bg_color)
        
        if qr_img.mode != 'RGBA':
            qr_img = qr_img.convert('RGBA')
        
        qr_width, qr_height = qr_img.size
        
        # Create tighter circular frame with minimal gap
        # Frame expansion is smaller now for tighter fit
        frame_expansion = max(30, qr_width // 6)  # ← Reduced from 1/4 to 1/6 for tighter frame
        canvas_size = qr_width + 2 * frame_expansion
        
        # Create background with transparency
        if is_transparent:
            bg_img = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 0))
        else:
            bg_img = Image.new("RGBA", (canvas_size, canvas_size), (*bg_rgb, 255))
        
        # Create circular mask with smooth edges
        mask = Image.new('L', (canvas_size, canvas_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, canvas_size-1, canvas_size-1], fill=255)
        
        # Apply circular mask to background
        bg_img.putalpha(mask)
        
        # Paste QR code centered in the circular frame
        qr_x = (canvas_size - qr_width) // 2
        qr_y = (canvas_size - qr_height) // 2
        bg_img.paste(qr_img, (qr_x, qr_y), qr_img)
        
        # Convert to appropriate final format
        if is_transparent:
            final_img = bg_img
        else:
            # Composite onto RGB background with circular mask
            final_rgb = Image.new("RGB", (canvas_size, canvas_size), bg_rgb)
            final_rgb.paste(bg_img, (0, 0), bg_img)
            final_img = final_rgb.convert('RGBA')
            final_img.putalpha(mask)
        
        # Add outer buffer if needed
        if outer_buffer > 0:
            final_size = final_img.size[0] + 2 * outer_buffer
            if is_transparent:
                buffered_img = Image.new("RGBA", (final_size, final_size), (255, 255, 255, 0))
            else:
                buffered_img = Image.new("RGBA", (final_size, final_size), (*bg_rgb, 255))
            offset = (outer_buffer, outer_buffer)
            buffered_img.paste(final_img, offset, final_img)
            final_img = buffered_img
        
        # Add logo if provided
        if logo_path:
            final_img = QRGeneratorCore._add_logo_to_qr(
                final_img, logo_path, logo_size_percent, logo_border,
                logo_corner_radius, fg_color
            )
        
        return final_img
    
    @staticmethod
    def _create_circular_pattern_from_qr(qr_pattern, pattern_size, fg_color, bg_color, is_transparent):
        """Create a circular QR code by masking the standard QR in a circle shape"""
        
        # Create circular mask
        mask = Image.new('L', (pattern_size, pattern_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, pattern_size-1, pattern_size-1], fill=255)
        
        # Convert QR pattern to RGBA if needed
        if qr_pattern.mode != 'RGBA':
            qr_rgba = qr_pattern.convert('RGBA')
        else:
            qr_rgba = qr_pattern
        
        # Apply circular mask
        qr_rgba.putalpha(mask)
        
        if is_transparent:
            return qr_rgba
        else:
            # Create background and paste masked QR on top
            bg_rgb_tuple = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
            background = Image.new('RGB', (pattern_size, pattern_size), bg_rgb_tuple)
            background.paste(qr_rgba, (0, 0), qr_rgba)
            return background
    
    @staticmethod
    def _round_finder_patterns(img, qr_modules, box_size, fg_color, bg_color, is_transparent):
        """Round the corners of the three finder (position detection) patterns"""
        
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        draw = ImageDraw.Draw(img)
        radius = (box_size * 3) // 2  # Radius for rounding
        
        # Three finder patterns are at corners:
        # Top-left: (0, 0) to (7*box_size, 7*box_size)
        # Top-right: (qr_width-7*box_size, 0) to (qr_width, 7*box_size)
        # Bottom-left: (0, qr_height-7*box_size) to (7*box_size, qr_height)
        
        qr_size = qr_modules * box_size
        finder_size = 7 * box_size  # Standard finder pattern size
        
        # Round each of the 3 finder corners
        finder_positions = [
            (0, 0),  # Top-left
            (qr_size - finder_size, 0),  # Top-right
            (0, qr_size - finder_size),  # Bottom-left
        ]
        
        for fx, fy in finder_positions:
            # Create rounded mask for this corner
            x0, y0 = fx, fy
            x1, y1 = fx + finder_size, fy + finder_size
            
            # Create a layer for this finder pattern with rounded corners
            temp = Image.new('RGBA', (finder_size, finder_size), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp)
            
            # Draw white rounded rectangle as mask
            temp_draw.rounded_rectangle([0, 0, finder_size-1, finder_size-1], 
                                       radius=radius, fill=(255, 255, 255, 255))
            
            # Extract the finder pattern region from main image
            finder_region = img.crop((x0, y0, x1, y1))
            
            # Create result with rounded corners
            result = Image.new('RGBA', (finder_size, finder_size), (0, 0, 0, 0))
            result.paste(finder_region, (0, 0))
            result.paste(temp, (0, 0), temp)
            
            # Paste back
            img.paste(result, (x0, y0), result)
        
        return img
    
    @staticmethod
    def generate_qr_svg(data, error_correction="M", fg_color="#000000", bg_color="#FFFFFF"):
        """Generate QR code as SVG"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{error_correction}"),
            box_size=1,
            border=4
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Generate SVG
        svg_factory = qrcode.image.svg.SvgPathImage
        img = qr.make_image(image_factory=svg_factory, fill_color=fg_color, back_color=bg_color)
        buffer = io.BytesIO()
        img.save(buffer, format="SVG")
        return buffer.getvalue()
