#!/usr/bin/env python3
"""
Combined launcher for FastAPI server + ngrok tunnel
Starts both services and displays the public ngrok URL
"""

import subprocess
import time
import requests
import sys
import os
import signal

# Track subprocesses
processes = []

def cleanup_handler(signum, frame):
    """Handle shutdown gracefully"""
    print("\n\n[LAUNCHER] Shutting down...")
    for proc in processes:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except:
                proc.kill()
    print("[LAUNCHER] All processes stopped")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, cleanup_handler)
signal.signal(signal.SIGTERM, cleanup_handler)

def start_server():
    """Start FastAPI server"""
    print("[LAUNCHER] Starting FastAPI server on port 8080...")
    proc = subprocess.Popen(
        ["python", "start_web.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    processes.append(proc)
    
    # Stream output
    def stream_output(p, prefix):
        for line in iter(p.stdout.readline, ''):
            if line:
                print(f"{prefix} {line.rstrip()}")
    
    import threading
    thread = threading.Thread(target=stream_output, args=(proc, "[SERVER]"))
    thread.daemon = True
    thread.start()
    
    return proc

def wait_for_server(max_retries=30):
    """Wait for server to be ready"""
    for attempt in range(max_retries):
        try:
            resp = requests.get("http://localhost:8080/", timeout=2)
            if resp.status_code == 200:
                print("[LAUNCHER] ✓ Server is ready!")
                return True
        except:
            pass
        if attempt > 0:
            print(f"[LAUNCHER] Waiting for server... ({attempt}/{max_retries})")
        time.sleep(1)
    return False

def start_ngrok():
    """Start ngrok tunnel"""
    print("[LAUNCHER] Starting ngrok tunnel...")
    
    # Get authtoken from environment or config file
    authtoken = os.environ.get("NGROK_AUTHTOKEN")
    if not authtoken:
        # Try to read from ngrok config
        ngrok_config = os.path.expanduser("~/.ngrok2/ngrok.yml")
        if os.path.exists(ngrok_config):
            try:
                with open(ngrok_config, 'r') as f:
                    content = f.read()
                    if 'authtoken:' in content:
                        for line in content.split('\n'):
                            if 'authtoken:' in line:
                                authtoken = line.split('authtoken:')[1].strip()
                                break
            except:
                pass
    
    # Build ngrok command
    cmd = ["./ngrok", "http", "8080", "--log=stdout"]
    if authtoken:
        cmd.insert(1, f"--authtoken={authtoken}")
        print(f"[LAUNCHER] ✓ Using authtoken from {'environment' if os.environ.get('NGROK_AUTHTOKEN') else 'config file'}")
    else:
        print(f"[LAUNCHER] ⚠ No authtoken found - ngrok may prompt for authentication")
    
    print(f"[LAUNCHER] Command: {' '.join(cmd[:3])} [authtoken] {' '.join(cmd[4:]) if len(cmd) > 4 else ''}")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    processes.append(proc)
    
    # Stream output
    def stream_output(p, prefix):
        for line in iter(p.stdout.readline, ''):
            if line:
                print(f"{prefix} {line.rstrip()}")
    
    import threading
    thread = threading.Thread(target=stream_output, args=(proc, "[NGROK]"))
    thread.daemon = True
    thread.start()
    
    return proc

def get_ngrok_url(max_retries=30):
    """Get ngrok public URL from API"""
    for attempt in range(max_retries):
        try:
            resp = requests.get("http://localhost:4040/api/tunnels", timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("tunnels"):
                    for tunnel in data["tunnels"]:
                        if tunnel.get("public_url") and tunnel.get("proto") == "https":
                            return tunnel["public_url"]
        except:
            pass
        if attempt > 0:
            print(f"[LAUNCHER] Waiting for ngrok tunnel... ({attempt}/{max_retries})")
        time.sleep(1)
    return None

def main():
    print("=" * 60)
    print("QR Code Generator - Combined Web Server + ngrok Launcher")
    print("=" * 60)
    
    # Check for authtoken
    authtoken = os.environ.get("NGROK_AUTHTOKEN")
    if not authtoken:
        ngrok_config = os.path.expanduser("~/.ngrok2/ngrok.yml")
        if os.path.exists(ngrok_config):
            with open(ngrok_config, 'r') as f:
                content = f.read()
                if 'authtoken:' in content:
                    authtoken = content.split('authtoken:')[1].strip().split()[0]
    
    if not authtoken:
        print("\n⚠️  WARNING: No ngrok authtoken found!")
        print("ngrok may prompt for authentication upon startup.")
        print("\nTo set up authentication (free):")
        print("1. Visit: https://dashboard.ngrok.com/signup")
        print("2. Create account and get your authtoken")
        print("3. Either:")
        print("   - Set environment: export NGROK_AUTHTOKEN='<your-token>'")
        print("   - Or run: ngrok config add-authtoken <your-token>")
        print("4. Then restart this launcher")
        print("=" * 60 + "\n")
    
    try:
        # Start server first
        server_proc = start_server()
        
        # Wait for server to be ready
        if not wait_for_server():
            print("[LAUNCHER] ✗ Server failed to start!")
            cleanup_handler(None, None)
            return
        
        # Give server a moment to fully initialize
        time.sleep(2)
        
        # Start ngrok
        ngrok_proc = start_ngrok()
        
        # Get and display ngrok URL
        ngrok_url = get_ngrok_url()
        if ngrok_url:
            print("\n" + "=" * 60)
            print("✓ SUCCESS! Your QR Code Generator is now public:")
            print(f"\n  Public URL: {ngrok_url}")
            print(f"  Local URL:  http://localhost:8080")
            print("\n  Share this URL with anyone to access your QR generator")
            print("=" * 60 + "\n")
        else:
            print("[LAUNCHER] ⚠ Could not retrieve ngrok URL")
        
        # Keep running
        print("[LAUNCHER] All services running. Press Ctrl+C to stop.\n")
        while True:
            # Check if processes are still alive
            if server_proc.poll() is not None:
                print("[LAUNCHER] ✗ Server crashed!")
                break
            if ngrok_proc.poll() is not None:
                print("[LAUNCHER] ✗ ngrok crashed!")
                break
            time.sleep(5)
            
    except KeyboardInterrupt:
        cleanup_handler(None, None)
    except Exception as e:
        print(f"[LAUNCHER] Error: {e}")
        cleanup_handler(None, None)

if __name__ == "__main__":
    main()
