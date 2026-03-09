import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, scrolledtext
from PIL import Image, ImageTk
import qrcode
import qrcode.image.svg
import base64
import io
import os
from pathlib import Path
from datetime import datetime
from qr_core import QRGeneratorCore

class QRCodeGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator - Advanced")
        self.root.geometry("1400x800")
        self.root.resizable(True, True)
        
        # Shared Variables
        self.box_size = tk.IntVar(value=10)
        self.border = tk.IntVar(value=4)
        self.outer_buffer = tk.IntVar(value=0)
        self.error_correction = tk.StringVar(value="M")
        self.fg_color = "#000000"
        self.bg_color = "#FFFFFF"
        self.logo_path = tk.StringVar()
        self.logo_size_percent = tk.IntVar(value=30)
        self.logo_border = tk.IntVar(value=5)
        self.logo_corner_radius = tk.IntVar(value=0)
        self.module_style = tk.StringVar(value="square")
        self.corner_style = tk.StringVar(value="standard")
        self.bg_pattern = tk.StringVar(value="solid")
        self.fg_gradient = tk.BooleanVar(value=False)
        self.fg_gradient_color2 = "#FFFFFF"
        self.glow_enabled = tk.BooleanVar(value=False)
        self.glow_radius = tk.IntVar(value=2)
        self.glow_intensity = tk.IntVar(value=50)
        
        self.current_qr_image = None
        self.current_pil_image = None
        self.current_qr_mode = "text"
        self.preview_window = None
        self.preview_label = None
        
        # Initialize field dictionaries
        self.vcard_fields = {}
        self.vcal_fields = {}
        self.text_var = tk.StringVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ===== LEFT COLUMN (75% width) =====
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # TOP LEFT - Type tabs with entry fields (50% vertical)
        input_frame = ttk.LabelFrame(left_frame, text="QR Code Input", padding=10)
        input_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        
        notebook = ttk.Notebook(input_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        self.text_tab = ttk.Frame(notebook)
        self.vcard_tab = ttk.Frame(notebook)
        self.vcal_tab = ttk.Frame(notebook)
        
        notebook.add(self.text_tab, text="Text/URL")
        notebook.add(self.vcard_tab, text="vCard 4")
        notebook.add(self.vcal_tab, text="vCalendar")
        
        self.setup_text_tab()
        self.setup_vcard_tab()
        self.setup_vcal_tab()
        
        notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # BOTTOM LEFT - Preview window (50% vertical) with gray background
        preview_frame = ttk.Frame(left_frame)
        preview_frame.grid(row=1, column=0, sticky="nsew")
        
        # Create gray background for preview
        preview_canvas = tk.Canvas(preview_frame, bg="#e0e0e0", highlightthickness=1, highlightbackground="#cccccc")
        preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add preview label inside canvas
        self.preview_label = tk.Label(preview_canvas, text="QR Code Preview", 
                                      bg="#e0e0e0", fg="#999999", font=("Arial", 10))
        preview_canvas.create_window(0.5, 0.5, window=self.preview_label, anchor="center", tags="preview")
        preview_canvas.pack_propagate(False)
        self.preview_canvas = preview_canvas
        
        # ===== RIGHT COLUMN (25% width) =====
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Create scrollable settings frame
        settings_frame = ttk.LabelFrame(right_frame, text="Design & Style", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        settings_canvas = tk.Canvas(settings_frame, highlightthickness=0)
        settings_scrollbar = ttk.Scrollbar(settings_frame, orient="vertical", command=settings_canvas.yview)
        self.settings_scrollable = ttk.Frame(settings_canvas)
        
        self.settings_scrollable.bind("<Configure>", lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all")))
        settings_canvas.create_window((0, 0), window=self.settings_scrollable, anchor="nw")
        settings_canvas.configure(yscrollcommand=settings_scrollbar.set)
        
        settings_canvas.pack(side="left", fill="both", expand=True)
        settings_scrollbar.pack(side="right", fill="y")
        
        self.setup_qr_settings(self.settings_scrollable)
        
        # Add buttons below the preview
        button_frame = ttk.Frame(preview_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(button_frame, text="Save QR", command=self.save_qr).pack(side=tk.LEFT, padx=5, expand=True)
        ttk.Button(button_frame, text="Base64 Export", command=self.show_base64_options).pack(side=tk.LEFT, padx=5, expand=True)
        
        # Configure grid weights for proper sizing
        # Left column: 75% width
        main_frame.columnconfigure(0, weight=3)
        # Right column: 25% width
        main_frame.columnconfigure(1, weight=1)
        # Make rows expand
        main_frame.rowconfigure(0, weight=1)
        
        # Left frame row weights: 50/50 split
        left_frame.rowconfigure(0, weight=1)  # Input section
        left_frame.rowconfigure(1, weight=1)  # Preview section
        left_frame.columnconfigure(0, weight=1)
        
    def setup_text_tab(self):
        frame = ttk.Frame(self.text_tab)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(frame, text="Text or URL:", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=2)
        text_entry = ttk.Entry(frame, textvariable=self.text_var, width=60)
        text_entry.grid(row=0, column=1, sticky="ew", pady=2)
        text_entry.bind("<KeyRelease>", lambda e: self.generate_qr())
        frame.columnconfigure(1, weight=1)
        
    def setup_vcard_tab(self):
        frame = ttk.Frame(self.vcard_tab)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        fields = [("First Name", "fn"), ("Last Name", "ln"), ("Email", "email"), ("Phone", "phone"),
                  ("Organization", "org"), ("Job Title", "title"), ("Website", "website"),
                  ("Street Address", "street"), ("City", "city"), ("State/Province", "state"),
                  ("ZIP Code", "zip"), ("Country", "country"), ("Date of Birth (YYYY-MM-DD)", "bday"), ("Note", "note")]
        
        row = 0
        for label, key in fields:
            ttk.Label(frame, text=label + ":", font=("Arial", 9)).grid(row=row, column=0, sticky="w", pady=3, padx=5)
            if key == "note":
                entry = tk.Text(frame, height=2, width=35)
                entry.grid(row=row, column=1, sticky="ew", pady=3, padx=5)
                entry.bind("<KeyRelease>", lambda e: self.generate_qr())
                self.vcard_fields[key] = entry
            else:
                var = tk.StringVar()
                entry = ttk.Entry(frame, textvariable=var, width=30)
                entry.grid(row=row, column=1, sticky="ew", pady=3, padx=5)
                entry.bind("<KeyRelease>", lambda e: self.generate_qr())
                self.vcard_fields[key] = var
            row += 1
        
        frame.columnconfigure(1, weight=1)
        
    def setup_vcal_tab(self):
        frame = ttk.Frame(self.vcal_tab)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        fields = [("Event Title", "title"), ("Description", "description"), ("Location", "location"),
                  ("Organizer Name", "organizer_name"), ("Organizer Email", "organizer_email"),
                  ("Start Date (YYYY-MM-DD)", "start_date"), ("Start Time (HH:MM)", "start_time"),
                  ("End Date (YYYY-MM-DD)", "end_date"), ("End Time (HH:MM)", "end_time"),
                  ("URL", "url"), ("Categories", "categories"), ("Attendees (comma-separated)", "attendees")]
        
        row = 0
        for label, key in fields:
            ttk.Label(frame, text=label + ":", font=("Arial", 9)).grid(row=row, column=0, sticky="w", pady=2, padx=5)
            if key in ["description", "attendees"]:
                entry = tk.Text(frame, height=2, width=30)
                entry.grid(row=row, column=1, sticky="ew", pady=2, padx=5)
                entry.bind("<KeyRelease>", lambda e: self.generate_qr())
                self.vcal_fields[key] = entry
            else:
                var = tk.StringVar()
                entry = ttk.Entry(frame, textvariable=var, width=30)
                entry.grid(row=row, column=1, sticky="ew", pady=2, padx=5)
                entry.bind("<KeyRelease>", lambda e: self.generate_qr())
                self.vcal_fields[key] = var
            row += 1
        
        frame.columnconfigure(1, weight=1)
    
    def on_tab_changed(self, event):
        selected_tab = event.widget.select()
        tab_index = event.widget.index("current")
        if tab_index == 0:
            self.current_qr_mode = "text"
        elif tab_index == 1:
            self.current_qr_mode = "vcard"
        else:
            self.current_qr_mode = "vcal"
        self.generate_qr()
        
    def on_value_changed(self):
        self.generate_qr()
    
    def setup_qr_settings(self, parent):
        ttk.Label(parent, text="Box Size (1-40):", font=("Arial", 9)).pack(anchor="w", pady=2)
        box_frame = ttk.Frame(parent)
        box_frame.pack(fill=tk.X, pady=2)
        ttk.Spinbox(box_frame, from_=1, to=40, textvariable=self.box_size, width=5, command=self.on_value_changed).pack(side=tk.LEFT)
        ttk.Label(box_frame, textvariable=self.box_size).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(parent, text="Border (0-20 modules):", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        border_frame = ttk.Frame(parent)
        border_frame.pack(fill=tk.X, pady=2)
        ttk.Spinbox(border_frame, from_=0, to=20, textvariable=self.border, width=5, command=self.on_value_changed).pack(side=tk.LEFT)
        ttk.Label(border_frame, textvariable=self.border).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(parent, text="Outer Buffer (0-100 pixels):", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        outer_buffer_frame = ttk.Frame(parent)
        outer_buffer_frame.pack(fill=tk.X, pady=2)
        ttk.Spinbox(outer_buffer_frame, from_=0, to=100, textvariable=self.outer_buffer, width=5, command=self.on_value_changed).pack(side=tk.LEFT)
        ttk.Label(outer_buffer_frame, textvariable=self.outer_buffer).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(parent, text="Error Correction:", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        error_combo = ttk.Combobox(parent, textvariable=self.error_correction, values=["L", "M", "Q", "H"], state="readonly", width=5)
        error_combo.pack(anchor="w", pady=2)
        error_combo.bind("<<ComboboxSelected>>", lambda e: self.on_value_changed())
        
        ttk.Label(parent, text="Module Style:", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        style_combo = ttk.Combobox(parent, textvariable=self.module_style, values=["square", "circle", "gapped"], state="readonly", width=15)
        style_combo.pack(anchor="w", pady=2)
        style_combo.bind("<<ComboboxSelected>>", lambda e: self.on_value_changed())
        
        ttk.Label(parent, text="Corner Markers:", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        corner_combo = ttk.Combobox(parent, textvariable=self.corner_style, values=["standard", "rounded", "beveled", "circular"], state="readonly", width=15)
        corner_combo.pack(anchor="w", pady=2)
        corner_combo.bind("<<ComboboxSelected>>", lambda e: self.on_value_changed())
        
        ttk.Label(parent, text="Background Pattern:", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        pattern_combo = ttk.Combobox(parent, textvariable=self.bg_pattern, values=["solid", "stripes", "dots", "grid"], state="readonly", width=15)
        pattern_combo.pack(anchor="w", pady=2)
        pattern_combo.bind("<<ComboboxSelected>>", lambda e: self.on_value_changed())
        
        ttk.Label(parent, text="Foreground Gradient:", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        gradient_frame = ttk.Frame(parent)
        gradient_frame.pack(fill=tk.X, pady=2)
        ttk.Checkbutton(gradient_frame, text="Enable Gradient", variable=self.fg_gradient, command=self.on_value_changed).pack(side=tk.LEFT)
        ttk.Button(gradient_frame, text="Color 2", command=self.pick_gradient_color2).pack(side=tk.LEFT, padx=5)
        self.gradient_color2_label = ttk.Label(gradient_frame, text=self.fg_gradient_color2, foreground="gray")
        self.gradient_color2_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(parent, text="Glow Effect:", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        glow_frame = ttk.Frame(parent)
        glow_frame.pack(fill=tk.X, pady=2)
        ttk.Checkbutton(glow_frame, text="Enable Glow", variable=self.glow_enabled, command=self.on_value_changed).pack(side=tk.LEFT)
        
        ttk.Label(parent, text="Glow Radius (1-5):", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        glow_radius_frame = ttk.Frame(parent)
        glow_radius_frame.pack(fill=tk.X, pady=2)
        ttk.Spinbox(glow_radius_frame, from_=1, to=5, textvariable=self.glow_radius, width=5, command=self.on_value_changed).pack(side=tk.LEFT)
        ttk.Label(glow_radius_frame, textvariable=self.glow_radius).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(parent, text="Glow Intensity (10-100%):", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        glow_intensity_frame = ttk.Frame(parent)
        glow_intensity_frame.pack(fill=tk.X, pady=2)
        ttk.Spinbox(glow_intensity_frame, from_=10, to=100, textvariable=self.glow_intensity, width=5, command=self.on_value_changed).pack(side=tk.LEFT)
        ttk.Label(glow_intensity_frame, textvariable=self.glow_intensity).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(parent, text="Foreground Color:", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        fg_color_frame = ttk.Frame(parent)
        fg_color_frame.pack(fill=tk.X, pady=2)
        self.fg_color_button = tk.Button(fg_color_frame, bg=self.fg_color, width=3, command=self.pick_fg_color)
        self.fg_color_button.pack(side=tk.LEFT)
        self.fg_color_label = ttk.Label(fg_color_frame, text=self.fg_color, foreground="gray")
        self.fg_color_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(parent, text="Background Color:", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        bg_color_frame = ttk.Frame(parent)
        bg_color_frame.pack(fill=tk.X, pady=2)
        self.bg_color_button = tk.Button(bg_color_frame, bg=self.bg_color, width=3, command=self.pick_bg_color)
        self.bg_color_button.pack(side=tk.LEFT)
        self.bg_color_label = ttk.Label(bg_color_frame, text=self.bg_color, foreground="gray")
        self.bg_color_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(parent, text="Logo (optional):", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        logo_frame = ttk.Frame(parent)
        logo_frame.pack(fill=tk.X, pady=2)
        ttk.Button(logo_frame, text="Select Logo", command=self.select_logo).pack(side=tk.LEFT, padx=5)
        ttk.Label(logo_frame, textvariable=self.logo_path, foreground="blue").pack(side=tk.LEFT)
        
        ttk.Label(parent, text="Logo Size (10-50%):", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        logo_size_frame = ttk.Frame(parent)
        logo_size_frame.pack(fill=tk.X, pady=2)
        ttk.Spinbox(logo_size_frame, from_=10, to=50, textvariable=self.logo_size_percent, width=5, command=self.on_value_changed).pack(side=tk.LEFT)
        ttk.Label(logo_size_frame, textvariable=self.logo_size_percent).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(parent, text="Logo Border (0-20 pixels):", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        logo_border_frame = ttk.Frame(parent)
        logo_border_frame.pack(fill=tk.X, pady=2)
        ttk.Spinbox(logo_border_frame, from_=0, to=20, textvariable=self.logo_border, width=5, command=self.on_value_changed).pack(side=tk.LEFT)
        ttk.Label(logo_border_frame, textvariable=self.logo_border).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(parent, text="Logo Corner Radius (0-20 pixels):", font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        logo_corner_frame = ttk.Frame(parent)
        logo_corner_frame.pack(fill=tk.X, pady=2)
        ttk.Spinbox(logo_corner_frame, from_=0, to=20, textvariable=self.logo_corner_radius, width=5, command=self.on_value_changed).pack(side=tk.LEFT)
        ttk.Label(logo_corner_frame, textvariable=self.logo_corner_radius).pack(side=tk.LEFT, padx=10)
        
    def generate_qr(self):
        try:
            if self.current_qr_mode == "text":
                data = self.text_var.get()
            elif self.current_qr_mode == "vcard":
                data = self.generate_vcard()
            else:
                data = self.generate_vcal()
            
            if not data:
                return
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{self.error_correction.get()}"),
                box_size=int(self.box_size.get()),
                border=int(self.border.get())
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            self.current_qr_image = qr
            self.render_qr()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR: {str(e)}")
    
    def render_qr(self):
        try:
            if not self.current_qr_image:
                return
            
            # Use the core module to generate the final image
            data = None
            if self.current_qr_mode == "text":
                data = self.text_var.get()
            elif self.current_qr_mode == "vcard":
                data = self.generate_vcard()
            else:
                data = self.generate_vcal()
            
            if not data:
                return
            
            self.current_pil_image = QRGeneratorCore.generate_qr_image(
                data=data,
                box_size=int(self.box_size.get()),
                border=int(self.border.get()),
                outer_buffer=int(self.outer_buffer.get()),
                error_correction=self.error_correction.get(),
                fg_color=self.fg_color,
                bg_color=self.bg_color,
                module_style=self.module_style.get(),
                corner_style=self.corner_style.get(),
                bg_pattern=self.bg_pattern.get(),
                fg_gradient=self.fg_gradient.get(),
                fg_gradient_color2=self.fg_gradient_color2,
                glow_enabled=self.glow_enabled.get(),
                glow_radius=int(self.glow_radius.get()),
                glow_intensity=int(self.glow_intensity.get()),
                logo_path=self.logo_path.get() if self.logo_path.get() else None,
                logo_size_percent=int(self.logo_size_percent.get()),
                logo_border=int(self.logo_border.get()),
                logo_corner_radius=int(self.logo_corner_radius.get())
            )
            
            self.display_preview(self.current_pil_image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to render QR: {str(e)}")
    
    def display_preview(self, img):
        try:
            preview_size = 250
            img_copy = img.copy()
            img_copy.thumbnail((preview_size, preview_size), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img_copy)
            
            # Update the canvas with the image
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo
            
            # Reposition in canvas center
            self.preview_canvas.coords("preview", 
                                       self.preview_canvas.winfo_width()/2,
                                       self.preview_canvas.winfo_height()/2)
        except Exception as e:
            messagebox.showerror("Error", f"Display failed: {str(e)}")
    
    def generate_vcard(self):
        try:
            fn = self.get_vcard_field("fn")
            ln = self.get_vcard_field("ln")
            email = self.get_vcard_field("email")
            phone = self.get_vcard_field("phone")
            org = self.get_vcard_field("org")
            title = self.get_vcard_field("title")
            website = self.get_vcard_field("website")
            street = self.get_vcard_field("street")
            city = self.get_vcard_field("city")
            state = self.get_vcard_field("state")
            zip_code = self.get_vcard_field("zip")
            country = self.get_vcard_field("country")
            bday = self.get_vcard_field("bday")
            note = self.get_vcard_field("note")
            
            return QRGeneratorCore.generate_vcard(
                fn=fn, ln=ln, email=email, phone=phone, org=org, title=title,
                website=website, street=street, city=city, state=state,
                zip_code=zip_code, country=country, bday=bday, note=note
            )
        except Exception as e:
            messagebox.showerror("Error", f"vCard generation failed: {str(e)}")
            return ""
    
    def generate_vcal(self):
        try:
            title = self.get_vcal_field("title")
            description = self.get_vcal_field("description")
            location = self.get_vcal_field("location")
            org_name = self.get_vcal_field("organizer_name")
            org_email = self.get_vcal_field("organizer_email")
            start_date = self.get_vcal_field("start_date")
            start_time = self.get_vcal_field("start_time")
            end_date = self.get_vcal_field("end_date")
            end_time = self.get_vcal_field("end_time")
            url = self.get_vcal_field("url")
            categories = self.get_vcal_field("categories")
            attendees = self.get_vcal_field("attendees")
            
            return QRGeneratorCore.generate_vcal(
                title=title, description=description, location=location,
                organizer_name=org_name, organizer_email=org_email,
                start_date=start_date, start_time=start_time,
                end_date=end_date, end_time=end_time, url=url,
                categories=categories, attendees=attendees
            )
        except Exception as e:
            messagebox.showerror("Error", f"vCalendar generation failed: {str(e)}")
            return ""
    
    def get_vcard_field(self, key):
        if key not in self.vcard_fields:
            return ""
        field = self.vcard_fields[key]
        if isinstance(field, tk.Text):
            return field.get("1.0", tk.END).strip()
        return field.get()
    
    def get_vcal_field(self, key):
        if key not in self.vcal_fields:
            return ""
        field = self.vcal_fields[key]
        if isinstance(field, tk.Text):
            return field.get("1.0", tk.END).strip()
        return field.get()
    
    def pick_fg_color(self):
        color = colorchooser.askcolor(self.fg_color, title="Choose Foreground Color")
        if color[1]:
            self.fg_color = color[1]
            self.fg_color_button.config(bg=self.fg_color)
            self.fg_color_label.config(text=self.fg_color)
            self.generate_qr()
    
    def pick_bg_color(self):
        color = colorchooser.askcolor(self.bg_color, title="Choose Background Color")
        if color[1]:
            self.bg_color = color[1]
            self.bg_color_button.config(bg=self.bg_color)
            self.bg_color_label.config(text=self.bg_color)
            self.generate_qr()
    
    def pick_gradient_color2(self):
        color = colorchooser.askcolor(self.fg_gradient_color2, title="Choose Gradient End Color")
        if color[1]:
            self.fg_gradient_color2 = color[1]
            self.gradient_color2_label.config(text=self.fg_gradient_color2)
            self.generate_qr()
    
    def select_logo(self):
        file = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if file:
            self.logo_path.set(file)
            self.generate_qr()
    
    def save_qr(self):
        if not self.current_pil_image:
            messagebox.showwarning("Warning", "Generate a QR code first")
            return
        
        file = filedialog.asksaveasfilename(defaultextension=".png", 
                                           filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("SVG", "*.svg")])
        if file:
            try:
                ext = file.lower().split('.')[-1]
                if ext == "svg":
                    # Generate SVG from scratch
                    qr = qrcode.QRCode(
                        box_size=int(self.box_size.get()),
                        border=int(self.border.get()),
                        error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{self.error_correction.get()}")
                    )
                    if self.current_qr_mode == "text":
                        data = self.text_var.get()
                    elif self.current_qr_mode == "vcard":
                        data = self.generate_vcard()
                    else:
                        data = self.generate_vcal()
                    qr.add_data(data)
                    qr.make(fit=True)
                    img = qr.make_image(image_factory=qrcode.image.svg.SvgImage)
                    with open(file, "w", encoding="utf-8") as f:
                        img.save(f)
                else:
                    self.current_pil_image.save(file)
                messagebox.showinfo("Success", f"QR code saved to {file}")
            except Exception as e:
                messagebox.showerror("Error", f"Save failed: {str(e)}")
    
    def get_base64_string(self):
        if not self.current_pil_image:
            return None
        
        return QRGeneratorCore.get_base64_string(self.current_pil_image)
    
    def show_base64_options(self):
        if not self.current_pil_image:
            messagebox.showwarning("Warning", "Generate a QR code first")
            return
        
        b64_data = self.get_base64_string()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Base64 Export Options")
        dialog.geometry("600x400")
        
        ttk.Label(dialog, text="Base64 String:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=5)
        
        text_widget = scrolledtext.ScrolledText(dialog, height=12, width=70)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        text_widget.insert("1.0", b64_data)
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(b64_data)
            messagebox.showinfo("Success", "Base64 copied to clipboard")
        
        def save_as_text():
            file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")])
            if file:
                with open(file, "w") as f:
                    f.write(b64_data)
                messagebox.showinfo("Success", f"Saved to {file}")
        
        def save_html_embed():
            file = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML", "*.html")])
            if file:
                html = f'<img src="data:image/png;base64,{b64_data}" alt="QR Code" />'
                with open(file, "w") as f:
                    f.write(html)
                messagebox.showinfo("Success", f"HTML saved to {file}")
        
        ttk.Button(button_frame, text="Copy to Clipboard", command=copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save as Text", command=save_as_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save HTML Embed", command=save_html_embed).pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeGenerator(root)
    root.mainloop()
