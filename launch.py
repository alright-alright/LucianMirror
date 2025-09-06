#!/usr/bin/env python3
"""
Smart launcher for LucianMirror that finds available ports and starts both servers
"""

import os
import sys
import subprocess
import time
import socket
import signal
import json
from pathlib import Path
import requests
from typing import Tuple, Optional
import platform

# Add backend to path for port finder
sys.path.append(str(Path(__file__).parent / "backend"))
from backend.utils.port_finder import find_free_port, get_process_on_port, suggest_port_pairs

class LucianMirrorLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.backend_port = None
        self.frontend_port = None
        self.root_dir = Path(__file__).parent
        
        # Register signal handlers for cleanup
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        # Check Python version
        if sys.version_info < (3, 10):
            print("❌ Python 3.10+ is required")
            return False
        
        # Check if pip packages are installed
        try:
            import fastapi
            import uvicorn
            print("✅ Backend dependencies found")
        except ImportError:
            print("❌ Backend dependencies not installed. Run: pip install -r backend/requirements.txt")
            return False
        
        # Check if npm is available
        try:
            subprocess.run(["npm", "--version"], capture_output=True, check=True)
            print("✅ npm found")
        except:
            print("❌ npm not found. Please install Node.js")
            return False
        
        # Check if frontend dependencies are installed
        frontend_modules = self.root_dir / "frontend" / "node_modules"
        if not frontend_modules.exists():
            print("⚠️  Frontend dependencies not installed. Installing now...")
            subprocess.run(["npm", "install"], cwd=self.root_dir / "frontend", check=True)
        else:
            print("✅ Frontend dependencies found")
        
        return True
    
    def find_ports(self) -> Tuple[int, int]:
        """Find available ports for backend and frontend"""
        print("\n🔍 Finding available ports...")
        
        # Try to get preferred ports from env
        backend_pref = int(os.environ.get("BACKEND_PORT", 8000))
        frontend_pref = int(os.environ.get("FRONTEND_PORT", 5173))
        
        # Check if preferred ports are free
        backend_port = find_free_port(backend_pref, (8000, 9000))
        frontend_port = find_free_port(frontend_pref, (5000, 6000), exclude_ports=[backend_port])
        
        # If defaults aren't available, suggest alternatives
        if backend_port != backend_pref or frontend_port != frontend_pref:
            print(f"⚠️  Default ports in use, finding alternatives...")
            backend_port, frontend_port = suggest_port_pairs()
        
        print(f"✅ Backend port:  {backend_port}")
        print(f"✅ Frontend port: {frontend_port}")
        
        return backend_port, frontend_port
    
    def create_env_files(self):
        """Create .env files if they don't exist"""
        # Root .env
        root_env = self.root_dir / ".env"
        if not root_env.exists():
            print("📝 Creating .env file...")
            example_env = self.root_dir / ".env.example"
            if example_env.exists():
                root_env.write_text(example_env.read_text())
                print("   ⚠️  Please edit .env with your API keys!")
        
        # Backend .env
        backend_env = self.root_dir / "backend" / ".env"
        if not backend_env.exists():
            example_env = self.root_dir / "backend" / ".env.example"
            if example_env.exists():
                backend_env.write_text(example_env.read_text())
        
        # Frontend .env
        frontend_env = self.root_dir / "frontend" / ".env"
        if not frontend_env.exists():
            frontend_env.write_text(f"VITE_API_URL=http://localhost:{self.backend_port}\n")
    
    def start_backend(self) -> bool:
        """Start the FastAPI backend server"""
        print(f"\n🚀 Starting backend on port {self.backend_port}...")
        
        env = os.environ.copy()
        env["BACKEND_PORT"] = str(self.backend_port)
        env["FRONTEND_PORT"] = str(self.frontend_port)
        
        # Command to start backend
        if platform.system() == "Windows":
            cmd = [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", str(self.backend_port)]
        else:
            cmd = ["python3", "-m", "uvicorn", "main:app", "--reload", "--port", str(self.backend_port)]
        
        try:
            self.backend_process = subprocess.Popen(
                cmd,
                cwd=self.root_dir / "backend",
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Wait for backend to start
            for i in range(30):  # 30 second timeout
                try:
                    response = requests.get(f"http://localhost:{self.backend_port}/")
                    if response.status_code == 200:
                        print("✅ Backend started successfully")
                        return True
                except:
                    pass
                time.sleep(1)
            
            print("❌ Backend failed to start in time")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self) -> bool:
        """Start the Vite frontend server"""
        print(f"\n🎨 Starting frontend on port {self.frontend_port}...")
        
        env = os.environ.copy()
        env["BACKEND_PORT"] = str(self.backend_port)
        env["FRONTEND_PORT"] = str(self.frontend_port)
        env["VITE_API_URL"] = f"http://localhost:{self.backend_port}"
        
        try:
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev", "--", "--port", str(self.frontend_port)],
                cwd=self.root_dir / "frontend",
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Wait a bit for frontend to start
            time.sleep(3)
            
            if self.frontend_process.poll() is None:
                print("✅ Frontend started successfully")
                return True
            else:
                print("❌ Frontend process exited unexpectedly")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def monitor_processes(self):
        """Monitor both processes and restart if needed"""
        print("\n" + "="*60)
        print("🎉 LucianMirror is running!")
        print("="*60)
        print(f"\n📍 Backend API:  http://localhost:{self.backend_port}")
        print(f"📝 API Docs:     http://localhost:{self.backend_port}/docs")
        print(f"🎨 Frontend UI:  http://localhost:{self.frontend_port}")
        print("\n💡 Press Ctrl+C to stop both servers")
        print("="*60 + "\n")
        
        try:
            while True:
                # Check if processes are still running
                if self.backend_process and self.backend_process.poll() is not None:
                    print("⚠️  Backend stopped unexpectedly, restarting...")
                    self.start_backend()
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("⚠️  Frontend stopped unexpectedly, restarting...")
                    self.start_frontend()
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down...")
    
    def cleanup(self, signum=None, frame=None):
        """Clean up processes on exit"""
        print("\n🧹 Cleaning up...")
        
        if self.backend_process:
            print("   Stopping backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            print("   Stopping frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        print("✅ Shutdown complete")
        sys.exit(0)
    
    def run(self):
        """Main launch sequence"""
        print("🚀 LucianMirror Launcher")
        print("=" * 60)
        
        # Check dependencies
        if not self.check_dependencies():
            print("\n❌ Please install missing dependencies and try again")
            sys.exit(1)
        
        # Find available ports
        self.backend_port, self.frontend_port = self.find_ports()
        
        # Create env files if needed
        self.create_env_files()
        
        # Start backend
        if not self.start_backend():
            print("❌ Failed to start backend")
            self.cleanup()
            sys.exit(1)
        
        # Start frontend
        if not self.start_frontend():
            print("❌ Failed to start frontend")
            self.cleanup()
            sys.exit(1)
        
        # Monitor processes
        self.monitor_processes()


if __name__ == "__main__":
    launcher = LucianMirrorLauncher()
    launcher.run()