"""
ngrok tunnel manager for exposing the QR generator to the internet
"""
import subprocess
import time
import requests
import json
import os
import sys
from pathlib import Path

try:
    from pyngrok import ngrok, conf
    PYNGROK_AVAILABLE = True
except ImportError:
    PYNGROK_AVAILABLE = False


class NgrokTunnelManager:
    """Manages ngrok tunnels for the QR code generator"""
    
    def __init__(self, port=8000, auth_token=None):
        self.port = port
        self.auth_token = auth_token
        self.process = None
        self.public_url = None
        self.ngrok_api_url = "http://127.0.0.1:4040/api"
    
    def start(self):
        """Start ngrok tunnel"""
        try:
            # Try pyngrok first if available
            if PYNGROK_AVAILABLE:
                try:
                    return self._start_with_pyngrok()
                except Exception as e:
                    print(f"pyngrok failed: {e}, trying subprocess method...")
            
            return self._start_with_subprocess()
        except Exception as e:
            print(f"Error starting ngrok: {str(e)}")
            return False
    
    def _start_with_pyngrok(self):
        """Start ngrok using pyngrok library"""
        if self.auth_token:
            ngrok.set_auth_token(self.auth_token)
        
        print(f"Starting ngrok tunnel on port {self.port}...")
        self.public_url = ngrok.connect(self.port, "http")
        
        if self.public_url:
            print(f"\n{'='*60}")
            print(f"✓ ngrok tunnel established!")
            print(f"Public URL: {self.public_url}")
            print(f"Local URL:  http://localhost:{self.port}")
            print(f"{'='*60}\n")
            return True
        else:
            print("Failed to establish ngrok tunnel")
            return False
    
    def _start_with_subprocess(self):
        """Start ngrok using subprocess"""
        if not self._is_ngrok_installed():
            print("ngrok not found. Please install from https://ngrok.com/download")
            print("Or on Windows: choco install ngrok")
            print("\nRunning in local-only mode (localhost:8000)")
            return False
        
        # Build ngrok command
        cmd = ["ngrok", "http", str(self.port)]
        
        if self.auth_token:
            cmd.insert(1, f"--authtoken={self.auth_token}")
        
        print(f"Starting ngrok tunnel on port {self.port}...")
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            # Wait for tunnel to establish
            time.sleep(3)
            
            # Get the public URL
            self.public_url = self._get_public_url()
            
            if self.public_url:
                print(f"\n{'='*60}")
                print(f"✓ ngrok tunnel established!")
                print(f"Public URL: {self.public_url}")
                print(f"Local URL:  http://localhost:{self.port}")
                print(f"{'='*60}\n")
                return True
            else:
                print("ngrok started but public URL not available yet")
                print("Running in local mode (localhost:8000)")
                return False
        except Exception as e:
            print(f"Error starting ngrok subprocess: {str(e)}")
            print("Running in local-only mode (localhost:8000)")
            return False
    
    def stop(self):
        """Stop the ngrok tunnel"""
        try:
            if self.process:
                if sys.platform == "win32":
                    self.process.terminate()
                else:
                    self.process.send_signal(15)
                time.sleep(1)
                print("ngrok tunnel stopped")
        except Exception as e:
            print(f"Error stopping ngrok: {str(e)}")
    
    def _get_public_url(self):
        """Get the public ngrok URL from the API"""
        try:
            response = requests.get(f"{self.ngrok_api_url}/tunnels", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("tunnels"):
                    for tunnel in data["tunnels"]:
                        if tunnel.get("proto") == "https":
                            return tunnel.get("public_url")
                    # If no HTTPS, return first HTTP
                    if data["tunnels"]:
                        return data["tunnels"][0].get("public_url")
        except Exception as e:
            print(f"Error getting public URL: {str(e)}")
        return None
    
    def _is_ngrok_installed(self):
        """Check if ngrok is installed"""
        try:
            subprocess.run(["ngrok", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _install_ngrok(self):
        """Install ngrok using system package manager or download"""
        try:
            if sys.platform == "win32":
                print("Please install ngrok from https://ngrok.com/download")
                print("Or use: choco install ngrok (if you have Chocolatey)")
            elif sys.platform == "darwin":
                subprocess.run(["brew", "install", "ngrok"], check=True)
            elif sys.platform == "linux":
                subprocess.run(["sudo", "apt-get", "install", "ngrok"], check=True)
        except Exception as e:
            print(f"Could not auto-install ngrok: {str(e)}")
            print("Please install ngrok manually from https://ngrok.com/download")
    
    def get_status(self):
        """Get current tunnel status"""
        return {
            "running": self.process is not None and self.process.poll() is None,
            "public_url": self.public_url,
            "local_port": self.port
        }


def create_tunnel_info_file(public_url, port):
    """Create a file with tunnel information for the web interface"""
    tunnel_info = {
        "public_url": public_url,
        "local_url": f"http://localhost:{port}",
        "timestamp": time.time()
    }
    
    # Save to a file that the web interface can read
    info_file = Path(__file__).parent / "tunnel_info.json"
    with open(info_file, "w") as f:
        json.dump(tunnel_info, f)
    
    return tunnel_info
