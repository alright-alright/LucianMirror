import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { spawn } from 'child_process'
import fs from 'fs'
import path from 'path'

// Function to check if port is in use
function checkPort(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    const net = require('net')
    const server = net.createServer()
    
    server.once('error', () => {
      resolve(false) // Port is in use
    })
    
    server.once('listening', () => {
      server.close()
      resolve(true) // Port is free
    })
    
    server.listen(port, '127.0.0.1')
  })
}

// Find a free port
async function findFreePort(startPort: number, endPort: number): Promise<number> {
  for (let port = startPort; port <= endPort; port++) {
    if (await checkPort(port)) {
      return port
    }
  }
  
  // If no port found in range, let system assign
  return 0
}

// Get backend URL from environment or find it
function getBackendUrl(): string {
  // Check if backend port is specified
  const backendPort = process.env.BACKEND_PORT || '8000'
  
  // Check common backend ports to see if one is running
  const commonBackendPorts = [8000, 8001, 8100, 8200, 9000]
  
  // Try to detect running backend
  for (const port of commonBackendPorts) {
    try {
      const response = fetch(`http://localhost:${port}/`)
        .then(res => res.json())
        .then(data => {
          if (data.service === 'LucianMirror Sprite Engine') {
            console.log(`✅ Found LucianMirror backend on port ${port}`)
            return port
          }
        })
        .catch(() => null)
    } catch {}
  }
  
  return `http://localhost:${backendPort}`
}

export default defineConfig(async ({ command, mode }) => {
  // Find a free port for the frontend
  const preferredPort = parseInt(process.env.FRONTEND_PORT || '5173')
  const port = await findFreePort(preferredPort, preferredPort + 100)
  
  if (port !== preferredPort) {
    console.log(`⚠️  Port ${preferredPort} is in use`)
    console.log(`✅ Using port ${port} instead`)
  }
  
  // Write port info to a temp file for the launch script
  const portInfo = {
    frontend: port,
    backend: parseInt(process.env.BACKEND_PORT || '8000'),
    timestamp: new Date().toISOString()
  }
  
  try {
    fs.writeFileSync(
      path.join(__dirname, '.port-info.json'),
      JSON.stringify(portInfo, null, 2)
    )
  } catch {}
  
  return {
    plugins: [react()],
    server: {
      port: port,
      host: true,
      open: false, // Don't auto-open browser
      cors: true,
      proxy: {
        '/api': {
          target: getBackendUrl(),
          changeOrigin: true,
          secure: false,
          ws: true,
          configure: (proxy, _options) => {
            proxy.on('error', (err, _req, _res) => {
              console.log('❌ Proxy error:', err)
            })
            proxy.on('proxyReq', (proxyReq, req, _res) => {
              console.log('📤 Proxying:', req.method, req.url)
            })
          }
        }
      }
    },
    define: {
      'import.meta.env.VITE_BACKEND_PORT': JSON.stringify(process.env.BACKEND_PORT || '8000'),
      'import.meta.env.VITE_FRONTEND_PORT': JSON.stringify(port)
    },
    build: {
      outDir: 'dist',
      sourcemap: true,
      rollupOptions: {
        output: {
          manualChunks: {
            'react-vendor': ['react', 'react-dom', 'react-router-dom'],
            'ui-vendor': ['framer-motion', 'lucide-react', 'clsx'],
            'data-vendor': ['axios', '@tanstack/react-query', 'zustand'],
            'canvas-vendor': ['fabric']
          }
        }
      }
    }
  }
})