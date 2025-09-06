# 🚀 LucianMirror Quick Start Guide

## Overview

LucianMirror is a dual-mode sprite generation system:
1. **API Service** - For integration with MySunshineStories
2. **Standalone React App** - Full-featured sprite editor with UI

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Redis (optional, for background jobs)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY (for DALL-E)
# - STABILITY_API_KEY (for Stable Diffusion)
# - R2_BUCKET_URL (for storage)

# Run the API server
uvicorn main:app --reload --port 8000
```

API will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## 🎮 Using the Standalone App

### 1. Character Setup
- Upload reference photos
- Enter character details
- Choose art style

### 2. Generate Sprites
- Select poses (standing, sitting, walking, etc.)
- Select emotions (happy, sad, worried, etc.)
- Choose generation API (DALL-E, Stable Diffusion)
- Click "Generate Sprites"

### 3. Edit & Refine
- Review generated sprites in grid
- Regenerate individual sprites
- Edit/crop as needed
- Export sprite sheet

### 4. Scene Composition
- Import or write story text
- System auto-detects scenes
- Drag sprites onto backgrounds
- Export composed scenes

## 🔌 API Integration (for MySunshineStories)

### Initialize Character
```python
import requests

# Initialize character with reference photos
response = requests.post('http://localhost:8000/api/characters/initialize', json={
    "character_id": "sunshine_123",
    "name": "Lucy",
    "reference_photos": ["url1", "url2"],
    "style": "watercolor"
})
```

### Generate Sprites
```python
# Generate sprite set
response = requests.post('http://localhost:8000/api/sprites/generate', json={
    "character_id": "sunshine_123",
    "poses": ["standing", "sitting", "walking"],
    "emotions": ["happy", "sad", "worried"],
    "generation_api": "dalle"
})
```

### Process Story
```python
# Process story into scenes
response = requests.post('http://localhost:8000/api/stories/process', json={
    "story_text": "Lucy was afraid of the dark...",
    "character_mappings": {"Lucy": "sunshine_123"},
    "generate_backgrounds": True
})

scenes = response.json()['scenes']
# Each scene has sprite + background composed
```

## 🎨 Generation Methods

### DALL-E (Default)
- Fast generation (5-10s per sprite)
- Good consistency
- No training required
- Cost: ~$0.04 per sprite

### Stable Diffusion + ControlNet
- Better consistency with reference
- No training required
- Cost: ~$0.01 per sprite (if self-hosted)

### Stable Diffusion + LoRA
- Best consistency
- Requires 30-60 min training
- Cost: ~$0.001 per sprite after training

## 📊 Architecture Components

### Core Components (from LucianOS)

#### MPU (Memory Processing Unit)
- Stores sprites in multi-dimensional space
- Instant retrieval by character/pose/emotion
- Handles temporal indexing for videos

#### SSP (Symbolic Sense Processor)  
- Parses story text into scene requirements
- Identifies characters, actions, emotions
- Maps narrative to visual elements

#### HASR (Hebbian Reinforcement)
- Learns optimal sprite combinations
- Improves selection over time
- Character-specific preferences

## 🎮 Workflow Examples

### Story to Sprites (Automatic)
1. Upload story text
2. SSP analyzes scenes
3. MPU retrieves best sprites
4. Backgrounds generated
5. Automatic composition

### Manual Scene Building
1. Select background
2. Drag sprites from library
3. Position and scale
4. Add effects/text
5. Export scene

### Video Creation (Coming Soon)
1. Import composed scenes
2. Set timing/transitions
3. Add audio/narration
4. Export as MP4/GIF

## 🐛 Troubleshooting

### API Connection Issues
```bash
# Check backend is running
curl http://localhost:8000/

# Check CORS settings in backend/main.py
```

### Sprite Generation Fails
- Verify API keys in .env
- Check image URLs are accessible
- Ensure reference photos are < 10MB

### Frontend Build Issues
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📚 Advanced Configuration

### Custom Generation Adapters
Create new adapter in `backend/adapters/`:
```python
class MyAdapter(GenerationAdapter):
    async def generate_sprite(self, prompt, reference_image=None):
        # Your implementation
        pass
```

### Custom UI Themes
Edit `frontend/tailwind.config.js` to customize colors

### Export Formats
- Sprite sheets (PNG)
- Individual sprites (PNG with transparency)
- JSON manifest (metadata)
- Unity/Godot packages

## 🚀 Production Deployment

### Backend
```bash
# Build Docker image
docker build -t lucianmirror-backend ./backend

# Run with Docker Compose
docker-compose up -d
```

### Frontend
```bash
# Build for production
npm run build

# Deploy to CDN (Vercel, Netlify, etc.)
vercel deploy ./dist
```

## 📝 API Reference

Full API documentation available at:
http://localhost:8000/docs

Key endpoints:
- `POST /api/characters/initialize` - Setup character
- `POST /api/sprites/generate` - Generate sprites
- `GET /api/sprites/{character_id}` - Get sprites
- `POST /api/scenes/compose` - Compose scene
- `POST /api/stories/process` - Process full story

## 🤝 Support

- GitHub Issues: [Report bugs](https://github.com/yourusername/LucianMirror/issues)
- Documentation: [Full docs](./docs/)
- Discord: [Join community](https://discord.gg/lucianmirror)

## 📄 License

MIT License - See LICENSE file

---

Built with ❤️ using LucianOS cognitive components
