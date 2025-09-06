import React, { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import Sidebar from './components/layout/Sidebar'
import TopBar from './components/layout/TopBar'
import SpriteDashboard from './pages/SpriteDashboard'
import SpriteEditor from './pages/SpriteEditor'
import SceneComposer from './pages/SceneComposer'
import StoryMode from './pages/StoryMode'
import Settings from './pages/Settings'

function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [currentMode, setCurrentMode] = useState<'sprites' | 'editor' | 'composer' | 'story'>('sprites')

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex">
      {/* Sidebar */}
      <Sidebar 
        collapsed={sidebarCollapsed} 
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        currentMode={currentMode}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <TopBar currentMode={currentMode} setCurrentMode={setCurrentMode} />

        {/* Content Area */}
        <main className="flex-1 overflow-hidden">
          <Routes>
            <Route path="/" element={<SpriteDashboard />} />
            <Route path="/editor" element={<SpriteEditor />} />
            <Route path="/composer" element={<SceneComposer />} />
            <Route path="/story" element={<StoryMode />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
