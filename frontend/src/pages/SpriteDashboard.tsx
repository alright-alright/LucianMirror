import React, { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, Sparkles, Grid3x3, Download, Play, Settings, Plus, Trash2, RefreshCw } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import SpriteGrid from '../components/sprites/SpriteGrid'
import GenerationPanel from '../components/sprites/GenerationPanel'
import CharacterSetup from '../components/sprites/CharacterSetup'
import ProgressIndicator from '../components/ui/ProgressIndicator'
import { useSpriteStore } from '../store/spriteStore'

const SpriteDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'setup' | 'generate' | 'library'>('setup')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  
  const { 
    currentCharacter, 
    sprites, 
    addSprite, 
    clearSprites 
  } = useSpriteStore()

  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Handle file uploads for reference photos
    console.log('Files uploaded:', acceptedFiles)
    toast.success(`${acceptedFiles.length} files uploaded`)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    },
    multiple: true
  })

  const handleGenerateSprites = async () => {
    setIsGenerating(true)
    setGenerationProgress(0)
    
    // Simulate generation progress
    const interval = setInterval(() => {
      setGenerationProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsGenerating(false)
          toast.success('Sprites generated successfully!')
          return 100
        }
        return prev + 10
      })
    }, 500)
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-950 via-purple-950/20 to-gray-950">
      {/* Header */}
      <div className="border-b border-white/10 backdrop-blur-xl bg-black/20">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Sprite Dashboard
              </h1>
              <p className="text-sm text-gray-400 mt-1">
                Create and manage character sprites with AI
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <button className="px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 transition-all">
                <Download className="w-4 h-4" />
              </button>
              <button 
                onClick={handleGenerateSprites}
                disabled={isGenerating}
                className="px-6 py-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isGenerating ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate Sprites
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-1 mt-6">
            {['setup', 'generate', 'library'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`px-4 py-2 rounded-t-lg transition-all ${
                  activeTab === tab
                    ? 'bg-white/10 text-white border-b-2 border-purple-500'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <AnimatePresence>
        {isGenerating && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-b border-white/10"
          >
            <ProgressIndicator progress={generationProgress} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        <AnimatePresence mode="wait">
          {activeTab === 'setup' && (
            <motion.div
              key="setup"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="h-full p-6"
            >
              <CharacterSetup />
            </motion.div>
          )}

          {activeTab === 'generate' && (
            <motion.div
              key="generate"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="h-full p-6"
            >
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
                {/* Upload Area */}
                <div className="bg-white/5 rounded-xl border border-white/10 p-6">
                  <h3 className="text-lg font-semibold mb-4">Reference Photos</h3>
                  
                  <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all ${
                      isDragActive
                        ? 'border-purple-500 bg-purple-500/10'
                        : 'border-white/20 hover:border-white/40'
                    }`}
                  >
                    <input {...getInputProps()} />
                    <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <p className="text-gray-300">
                      {isDragActive
                        ? 'Drop the files here...'
                        : 'Drag & drop reference photos here, or click to select'}
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      PNG, JPG, GIF up to 10MB each
                    </p>
                  </div>

                  {/* Uploaded Files Preview */}
                  <div className="mt-4 grid grid-cols-3 gap-2">
                    {/* Preview thumbnails would go here */}
                  </div>
                </div>

                {/* Generation Settings */}
                <GenerationPanel onGenerate={handleGenerateSprites} />
              </div>
            </motion.div>
          )}

          {activeTab === 'library' && (
            <motion.div
              key="library"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="h-full p-6"
            >
              <SpriteGrid sprites={sprites} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Status Bar */}
      <div className="border-t border-white/10 bg-black/20 backdrop-blur-xl px-6 py-3">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-4">
            <span className="text-gray-400">
              Character: <span className="text-white font-medium">
                {currentCharacter?.name || 'None'}
              </span>
            </span>
            <span className="text-gray-400">
              Sprites: <span className="text-white font-medium">{sprites.length}</span>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-gray-400">API Connected</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SpriteDashboard
