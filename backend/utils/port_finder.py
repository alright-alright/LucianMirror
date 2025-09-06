"""
Smart port finder utility for avoiding conflicts on dev machines
"""

import socket
import random
from typing import Optional, List
import psutil


def is_port_free(port: int, host: str = '127.0.0.1') -> bool:
    """
    Check if a port is free to use
    
    Args:
        port: Port number to check
        host: Host to check on
        
    Returns:
        True if port is free, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result != 0
    except:
        return False


def get_process_on_port(port: int) -> Optional[str]:
    """
    Get the name of the process using a port
    
    Args:
        port: Port number to check
        
    Returns:
        Process name or None
    """
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                try:
                    process = psutil.Process(conn.pid)
                    return process.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    return "Unknown Process"
    except:
        pass
    return None


def find_free_port(
    preferred_port: int = 8000,
    fallback_range: tuple = (8001, 9000),
    exclude_ports: Optional[List[int]] = None
) -> int:
    """
    Find a free port, starting with preferred port
    
    Args:
        preferred_port: Try this port first
        fallback_range: Range to search if preferred is taken
        exclude_ports: Ports to never use
        
    Returns:
        Available port number
    """
    exclude_ports = exclude_ports or []
    
    # Try preferred port first
    if preferred_port not in exclude_ports and is_port_free(preferred_port):
        return preferred_port
    
    # Log what's using the preferred port
    process = get_process_on_port(preferred_port)
    if process:
        print(f"⚠️  Port {preferred_port} is in use by: {process}")
    
    # Try random ports in fallback range
    attempts = 0
    max_attempts = 100
    
    while attempts < max_attempts:
        port = random.randint(fallback_range[0], fallback_range[1])
        
        if port not in exclude_ports and is_port_free(port):
            print(f"✅ Found free port: {port}")
            return port
        
        attempts += 1
    
    # Last resort: let OS assign
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        port = s.getsockname()[1]
        print(f"✅ OS assigned port: {port}")
        return port


def get_common_ports_status() -> dict:
    """
    Check status of commonly used development ports
    
    Returns:
        Dictionary of port statuses
    """
    common_ports = {
        3000: "React/Node.js",
        3001: "React/Node.js",
        4200: "Angular",
        5000: "Flask",
        5173: "Vite",
        5174: "Vite",
        8000: "Django/FastAPI",
        8001: "FastAPI",
        8080: "Various",
        8888: "Jupyter",
        9000: "PHP"
    }
    
    status = {}
    for port, typical_use in common_ports.items():
        if is_port_free(port):
            status[port] = {"free": True, "typical_use": typical_use}
        else:
            process = get_process_on_port(port)
            status[port] = {
                "free": False,
                "typical_use": typical_use,
                "used_by": process or "Unknown"
            }
    
    return status


def suggest_port_pairs() -> tuple:
    """
    Suggest port pairs for backend and frontend that don't conflict
    
    Returns:
        Tuple of (backend_port, frontend_port)
    """
    # Common pairs to try
    pairs = [
        (8000, 5173),  # FastAPI + Vite defaults
        (8001, 5174),  # Alternative defaults
        (8100, 5273),  # Custom range
        (8200, 5373),  # Another custom range
        (9000, 4173),  # Different range
    ]
    
    for backend_port, frontend_port in pairs:
        if is_port_free(backend_port) and is_port_free(frontend_port):
            return (backend_port, frontend_port)
    
    # If no pairs work, find two random free ports
    backend_port = find_free_port(8000, (8000, 9000))
    frontend_port = find_free_port(5173, (5000, 6000), exclude_ports=[backend_port])
    
    return (backend_port, frontend_port)


if __name__ == "__main__":
    # Test the port finder
    print("🔍 Checking common development ports...")
    print("-" * 50)
    
    status = get_common_ports_status()
    for port, info in sorted(status.items()):
        if info["free"]:
            print(f"✅ Port {port:5} - FREE ({info['typical_use']})")
        else:
            print(f"❌ Port {port:5} - IN USE by {info['used_by']} (typically {info['typical_use']})")
    
    print("\n" + "-" * 50)
    backend_port, frontend_port = suggest_port_pairs()
    print(f"\n🎯 Suggested ports:")
    print(f"   Backend:  {backend_port}")
    print(f"   Frontend: {frontend_port}")