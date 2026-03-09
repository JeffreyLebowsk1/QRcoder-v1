"""
Main launcher app - choose between desktop GUI and web interface
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import webbrowser
import time
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from ngrok_manager import NgrokTunnelManager, create_tunnel_info_file


class LauncherWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator - Mode Selector")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=20, pady=20)
        
        title = ttk.Label(header, text="QR Code Generator", font=("Arial", 20, "bold"))
        title.pack(anchor="w")
        
        subtitle = ttk.Label(header, text="Choose how you want to use the app", font=("Arial", 10), foreground="gray")
        subtitle.pack(anchor="w", pady=(5, 0))
        
        # Main content
        content = ttk.Frame(self.root)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Desktop option
        desktop_frame = self._create_option_frame(
            content,
            "🖥️  Desktop GUI",
            "Advanced tkinter interface\nwith real-time preview and\nlocal file management",
            self.launch_desktop
        )
        desktop_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Web option
        web_frame = self._create_option_frame(
            content,
            "🌐 Web Interface",
            "Beautiful web interface\naccessed from any device\nwith ngrok public tunnel",
            self.launch_web
        )
        web_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Both option
        both_frame = self._create_option_frame(
            content,
            "🔄 Both Desktop + Web",
            "Run both interfaces\nsimultaneously and access\nweb from any device",
            self.launch_both
        )
        both_frame.pack(fill=tk.BOTH, expand=True)
    
    def _create_option_frame(self, parent, title, description, callback):
        frame = tk.Frame(parent, relief=tk.RAISED, bd=2, bg="white")
        
        # Title and description
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.X, padx=20, pady=15)
        
        title_label = ttk.Label(text_frame, text=title, font=("Arial", 12, "bold"))
        title_label.pack(anchor="w")
        
        desc_label = ttk.Label(text_frame, text=description, font=("Arial", 9), foreground="gray")
        desc_label.pack(anchor="w", pady=(5, 0))
        
        # Button
        btn = ttk.Button(text_frame, text="Launch", command=callback)
        btn.pack(anchor="e", pady=(10, 0))
        
        return frame
    
    def launch_desktop(self):
        self.root.withdraw()
        from qr_generator import QRCodeGenerator
        new_root = tk.Tk()
        app = QRCodeGenerator(new_root)
        new_root.mainloop()
    
    def launch_web(self):
        self.root.withdraw()
        self._start_web_server(standalone=True)
    
    def launch_both(self):
        self.root.withdraw()
        
        # Start web server in background
        web_thread = threading.Thread(target=self._start_web_server, args=(False,), daemon=True)
        web_thread.start()
        
        # Wait a bit for server to start, then launch desktop
        time.sleep(2)
        from qr_generator import QRCodeGenerator
        new_root = tk.Tk()
        app = QRCodeGenerator(new_root)
        new_root.mainloop()
    
    def _start_web_server(self, standalone=False):
        try:
            import uvicorn
            from api_server import app
            
            # Start ngrok tunnel
            ngrok = NgrokTunnelManager(port=8000)
            ngrok_success = ngrok.start()
            
            if ngrok_success and ngrok.public_url:
                # Save tunnel info for the web interface
                create_tunnel_info_file(ngrok.public_url, 8000)
                
                if standalone:
                    # Open browser to ngrok URL
                    webbrowser.open(ngrok.public_url)
            else:
                # Still try to run locally if ngrok fails
                print("Warning: ngrok tunnel failed, running locally only")
                if standalone:
                    webbrowser.open("http://localhost:8000")
            
            # Run the server
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start web server: {str(e)}")
            if standalone:
                sys.exit(1)


def main():
    root = tk.Tk()
    app = LauncherWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
