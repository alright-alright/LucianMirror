import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const spriteApi = {
  // Character endpoints
  initializeCharacter: async (characterData: any) => {
    const response = await api.post('/api/characters/initialize', characterData)
    return response.data
  },
  
  // Sprite generation
  generateSprites: async (data: {
    character_id: string
    character_data: any
    poses?: string[]
    emotions?: string[]
    generation_api?: string
  }) => {
    const response = await api.post('/api/sprites/generate', data)
    return response.data
  },
  
  getCharacterSprites: async (characterId: string) => {
    const response = await api.get(`/api/sprites/${characterId}`)
    return response.data
  },
  
  uploadCustomSprite: async (characterId: string, pose: string, emotion: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post(
      `/api/sprites/upload?character_id=${characterId}&pose=${pose}&emotion=${emotion}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },
  
  createSpriteSheet: async (characterId: string, format: string = 'unity') => {
    const response = await api.post('/api/sprites/sheet', {
      character_id: characterId,
      output_format: format
    })
    return response.data
  },
  
  deleteCharacterSprites: async (characterId: string) => {
    const response = await api.delete(`/api/sprites/${characterId}`)
    return response.data
  },
  
  // Scene composition
  composeScene: async (data: {
    scene_text: string
    character_mappings: Record<string, string>
    background_style?: string
    generation_api?: string
    auto_compose?: boolean
  }) => {
    const response = await api.post('/api/scenes/compose', data)
    return response.data
  },
  
  manualCompose: async (data: {
    background_url: string
    sprites: any[]
    output_format?: string
  }) => {
    const response = await api.post('/api/compose/manual', data)
    return response.data
  },
  
  // Story processing
  processStory: async (data: {
    story_text: string
    character_mappings: Record<string, string>
    background_style?: string
    generation_api?: string
  }) => {
    const response = await api.post('/api/stories/process', data)
    return response.data
  },
  
  // Learning/HASR
  provideFeedback: async (data: {
    story_id: string
    scene_index: number
    success_score: number
    context: any
    sprite_choice: any
  }) => {
    const response = await api.post('/api/learning/feedback', data)
    return response.data
  },
  
  getSuggestions: async (characterId: string, scene: string, emotion: string) => {
    const response = await api.get('/api/learning/suggestions', {
      params: { character_id: characterId, scene, emotion }
    })
    return response.data
  },
  
  // Background removal
  removeBackground: async (imageUrl: string) => {
    const response = await api.post('/api/background/remove', { image_url: imageUrl })
    return response.data
  },
  
  // Video generation
  generateVideo: async (data: {
    story_id: string
    sprites: any[]
    background_url: string
    duration?: number
    transitions?: string[]
  }) => {
    const response = await api.post('/api/video/generate', data)
    return response.data
  }
}

export default api
