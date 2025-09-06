import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

interface Character {
  id: string
  name: string
  age?: number
  gender?: string
  physicalFeatures?: {
    hair?: string
    eyes?: string
    skin?: string
  }
  referencePhotos: string[]
  style: string
  createdAt: string
}

interface Sprite {
  id: string
  characterId: string
  pose: string
  emotion: string
  url: string
  thumbnailUrl?: string
  type: 'character' | 'action' | 'custom'
}

interface Scene {
  id: string
  text: string
  backgroundUrl?: string
  sprites: {
    spriteId: string
    position: {
      x: number
      y: number
      scale: number
      rotation: number
    }
  }[]
  composedUrl?: string
}

interface SpriteStore {
  // Character state
  currentCharacter: Character | null
  characters: Character[]
  
  // Sprite state
  sprites: Sprite[]
  selectedSprite: Sprite | null
  
  // Scene state
  scenes: Scene[]
  currentScene: Scene | null
  
  // Generation state
  isGenerating: boolean
  generationProgress: number
  generationApi: 'dalle' | 'stable_diffusion' | 'local'
  
  // Actions
  setCurrentCharacter: (character: Character) => void
  addCharacter: (character: Character) => void
  removeCharacter: (id: string) => void
  
  addSprite: (sprite: Sprite) => void
  addSprites: (sprites: Sprite[]) => void
  selectSprite: (sprite: Sprite | null) => void
  removeSprite: (id: string) => void
  clearSprites: () => void
  
  addScene: (scene: Scene) => void
  updateScene: (id: string, updates: Partial<Scene>) => void
  setCurrentScene: (scene: Scene | null) => void
  removeScene: (id: string) => void
  
  setGenerating: (isGenerating: boolean) => void
  setGenerationProgress: (progress: number) => void
  setGenerationApi: (api: 'dalle' | 'stable_diffusion' | 'local') => void
  
  reset: () => void
}

export const useSpriteStore = create<SpriteStore>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        currentCharacter: null,
        characters: [],
        sprites: [],
        selectedSprite: null,
        scenes: [],
        currentScene: null,
        isGenerating: false,
        generationProgress: 0,
        generationApi: 'dalle',
        
        // Character actions
        setCurrentCharacter: (character) => set({ currentCharacter: character }),
        
        addCharacter: (character) => set((state) => ({
          characters: [...state.characters, character],
          currentCharacter: character
        })),
        
        removeCharacter: (id) => set((state) => ({
          characters: state.characters.filter(c => c.id !== id),
          currentCharacter: state.currentCharacter?.id === id ? null : state.currentCharacter
        })),
        
        // Sprite actions
        addSprite: (sprite) => set((state) => ({
          sprites: [...state.sprites, sprite]
        })),
        
        addSprites: (sprites) => set((state) => ({
          sprites: [...state.sprites, ...sprites]
        })),
        
        selectSprite: (sprite) => set({ selectedSprite: sprite }),
        
        removeSprite: (id) => set((state) => ({
          sprites: state.sprites.filter(s => s.id !== id),
          selectedSprite: state.selectedSprite?.id === id ? null : state.selectedSprite
        })),
        
        clearSprites: () => set({ sprites: [], selectedSprite: null }),
        
        // Scene actions
        addScene: (scene) => set((state) => ({
          scenes: [...state.scenes, scene]
        })),
        
        updateScene: (id, updates) => set((state) => ({
          scenes: state.scenes.map(s => s.id === id ? { ...s, ...updates } : s),
          currentScene: state.currentScene?.id === id 
            ? { ...state.currentScene, ...updates } 
            : state.currentScene
        })),
        
        setCurrentScene: (scene) => set({ currentScene: scene }),
        
        removeScene: (id) => set((state) => ({
          scenes: state.scenes.filter(s => s.id !== id),
          currentScene: state.currentScene?.id === id ? null : state.currentScene
        })),
        
        // Generation actions
        setGenerating: (isGenerating) => set({ isGenerating }),
        setGenerationProgress: (progress) => set({ generationProgress: progress }),
        setGenerationApi: (api) => set({ generationApi: api }),
        
        // Reset
        reset: () => set({
          currentCharacter: null,
          characters: [],
          sprites: [],
          selectedSprite: null,
          scenes: [],
          currentScene: null,
          isGenerating: false,
          generationProgress: 0,
          generationApi: 'dalle'
        })
      }),
      {
        name: 'lucianmirror-storage',
        partialize: (state) => ({
          characters: state.characters,
          sprites: state.sprites,
          scenes: state.scenes,
          generationApi: state.generationApi
        })
      }
    )
  )
)
