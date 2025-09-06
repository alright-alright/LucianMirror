# LucianMirror Architecture Documentation

## 🎯 Overview

LucianMirror is a revolutionary entertainment platform that creates personalized content starring YOU and your chosen ones. It's the foundation for the Netflix/Disney of custom entertainment.

## 🔄 Swappable Components (Plug & Play)

### Image Generation Adapters

All image generation is abstracted through adapters, making it trivial to swap providers:

```python
# Current implementation in adapters/generation_adapters.py
class GenerationAdapter(ABC):
    """Base class for all generation providers"""
    
    @abstractmethod
    async def generate_sprite(self, prompt: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    async def generate_background(self, setting: str, **kwargs) -> str:
        pass
```

#### Supported Providers:
- **DALL-E 3** (OpenAI) - Currently implemented
- **Stable Diffusion** (Multiple backends)
  - Replicate
  - HuggingFace
  - Local (ComfyUI/A1111)
- **Midjourney** (Via API wrapper)
- **Leonardo.ai**
- **Custom/Self-hosted models**

#### How to Add a New Provider:

1. Create adapter in `adapters/generation_adapters.py`:
```python
class YourProviderAdapter(GenerationAdapter):
    async def generate_sprite(self, prompt: str, **kwargs):
        # Your implementation
        return sprite_url
```

2. Register in AdapterFactory:
```python
AdapterFactory.register('your_provider', YourProviderAdapter)
```

3. Use anywhere:
```python
adapter = AdapterFactory.create_adapter('your_provider')
sprite_url = await adapter.generate_sprite(prompt)
```

### Video Generation Tools

Video generation is similarly abstracted:

```python
# In services/video_generation_service.py
class VideoGenerationService:
    async def _compile_video(self, frames, width, height, fps, format='mp4'):
        # Try multiple backends in order of preference
        if OPENCV_AVAILABLE:
            return await self._compile_with_opencv(frames, ...)
        elif MOVIEPY_AVAILABLE:
            return await self._compile_with_moviepy(frames, ...)
        elif FFMPEG_AVAILABLE:
            return await self._compile_with_ffmpeg(frames, ...)
        else:
            return await self._save_as_gif(frames)  # Fallback
```

#### Supported Video Tools:
- **OpenCV** - Fast, lightweight
- **MoviePy** - High quality, more features
- **FFmpeg** - Professional grade
- **ImageIO** - Simple fallback
- **Cloud Services** (Runway, Replicate)

### Storage Backends

Storage is abstracted for easy swapping:

```python
# In services/storage_service.py
class StorageAdapter(ABC):
    async def save(self, data: bytes, key: str) -> str:
        pass
    
    async def load(self, key: str) -> bytes:
        pass
```

#### Supported Storage:
- **Cloudflare R2** (S3 compatible)
- **AWS S3**
- **Google Cloud Storage**
- **Azure Blob Storage**
- **Local filesystem**
- **IPFS** (for decentralized storage)

## 🧠 Core Components

### 1. LucianOS Cognitive Components

#### MPU (Memory Processing Unit)
- **Purpose**: Multi-dimensional sprite indexing and retrieval
- **Location**: `core/mpu.py`
- **Key Features**:
  - O(1) lookups by character, pose, emotion
  - Automatic caching
  - Similarity scoring

#### SSP (Scene-to-Sprite Parser)
- **Purpose**: Natural language to sprite requirements
- **Location**: `core/ssp.py`
- **Key Features**:
  - Scene text analysis
  - Character detection
  - Emotion extraction
  - Action parsing

#### HASR (Hebbian Adaptive Sprite Recommendation)
- **Purpose**: Learning from user preferences
- **Location**: `core/hasr.py`
- **Key Features**:
  - Reinforcement learning
  - Pattern recognition
  - Predictive suggestions

### 2. Service Layer

#### Sprite Generation Service
- **Location**: `services/sprite_generation_service.py`
- **Responsibilities**:
  - Character sprite generation
  - Pose/emotion matrix creation
  - Background removal
  - Quality consistency

#### Video Generation Service
- **Location**: `services/video_generation_service.py`
- **Responsibilities**:
  - TikTok/Shorts creation
  - Episode generation
  - Animation effects
  - Genre-specific styling

#### Entertainment Platform Service
- **Location**: `services/entertainment_platform_service.py`
- **Responsibilities**:
  - Series management
  - Content scheduling
  - Crossover events
  - Recommendation engine

#### Game Asset Service
- **Location**: `services/game_asset_service.py`
- **Responsibilities**:
  - RPG sprite sheets
  - Game engine exports
  - Character stats
  - Equipment systems

### 3. Integration Layer

#### MySunshineStories Pipeline
- **Location**: `integrations/mysunshine_pipeline.py`
- **Purpose**: Drop-in replacement for DALL-E direct generation
- **Features**:
  - Autonomous sprite generation
  - Scene composition
  - Video generation
  - Fallback handling

## 📡 API Architecture

### Core Endpoints

#### Character Management
```
POST /api/characters/initialize
GET  /api/sprites/{character_id}
POST /api/sprites/generate
```

#### Story Processing
```
POST /api/stories/process
POST /api/scenes/compose
```

#### Video Generation
```
POST /api/video/create-episode
POST /api/video/create-social-story
POST /api/video/quick-tiktok
```

#### Game Assets
```
POST /api/video/create-rpg-hero
POST /api/video/create-game-world
GET  /api/game-assets/{character_id}/export
```

#### Entertainment Platform
```
POST /api/platform/create-universe
POST /api/platform/generate-weekly-content
POST /api/platform/create-crossover
```

### MySunshineStories Integration
```
POST /api/mysunshine/generate-story-images
POST /api/mysunshine/initialize-profile
GET  /api/mysunshine/profile-status/{profile_id}
```

## 🔌 Configuration

### Environment Variables
```bash
# AI Providers
OPENAI_API_KEY=your_key
REPLICATE_API_TOKEN=your_token
STABILITY_API_KEY=your_key
MIDJOURNEY_TOKEN=your_token

# Storage
STORAGE_BACKEND=r2|s3|gcs|local
R2_ACCOUNT_ID=your_account
R2_ACCESS_KEY=your_key
R2_SECRET_KEY=your_secret

# Video Processing
VIDEO_BACKEND=opencv|moviepy|ffmpeg
VIDEO_QUALITY=standard|high|cinematic

# Platform
BACKEND_PORT=8000
FRONTEND_PORT=5173
```

### Provider Configuration
```python
# config/providers.py
PROVIDER_CONFIG = {
    'dalle': {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': 'dall-e-3',
        'quality': 'hd'
    },
    'stable_diffusion': {
        'backend': 'replicate',  # or 'local', 'huggingface'
        'model': 'stability-ai/sdxl',
        'token': os.getenv('REPLICATE_API_TOKEN')
    },
    'midjourney': {
        'proxy_url': os.getenv('MJ_PROXY_URL'),
        'token': os.getenv('MJ_TOKEN')
    }
}
```

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Run with smart port detection
CMD ["python", "backend/main.py"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lucianmirror
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lucianmirror
  template:
    spec:
      containers:
      - name: api
        image: lucianmirror:latest
        env:
        - name: PROVIDER
          value: "stable_diffusion"  # Easy to swap
        - name: VIDEO_BACKEND
          value: "moviepy"
```

## 🔄 Swapping Providers

### Example: Switching from DALL-E to Stable Diffusion

1. **Update environment**:
```bash
export GENERATION_API=stable_diffusion
export STABILITY_API_KEY=your_key
```

2. **No code changes needed!** The adapter pattern handles everything:
```python
# This code stays the same
adapter = AdapterFactory.create_adapter(
    os.getenv('GENERATION_API', 'dalle')
)
sprite_url = await adapter.generate_sprite(prompt)
```

### Example: Adding Local Stable Diffusion

1. **Create adapter**:
```python
class LocalSDAdapter(GenerationAdapter):
    def __init__(self):
        self.api_url = "http://localhost:7860"  # A1111 API
    
    async def generate_sprite(self, prompt: str, **kwargs):
        # Call local API
        response = await self._call_local_api(prompt)
        return response['image_url']
```

2. **Register**:
```python
AdapterFactory.register('local_sd', LocalSDAdapter)
```

3. **Use**:
```bash
export GENERATION_API=local_sd
```

## 📊 Performance Optimization

### Caching Strategy
- **MPU**: In-memory sprite cache
- **Redis**: Session state
- **CDN**: Generated videos
- **Local**: Temporary processing

### Parallel Processing
- Scene generation in parallel
- Sprite generation batching
- Video encoding pipeline
- Background pre-generation

## 🔒 Security

### API Security
- JWT authentication
- Rate limiting per user
- API key rotation
- Content moderation

### Data Privacy
- Local processing option
- Encrypted storage
- GDPR compliance
- User data ownership

## 📈 Scaling

### Horizontal Scaling
- Stateless API servers
- Queue-based job processing
- Distributed sprite generation
- CDN for content delivery

### Vertical Scaling
- GPU instances for generation
- High-memory for video processing
- SSD for sprite caching
- Dedicated encoding servers

## 🎮 Future Integrations

### Planned Providers
- **Flux** (Black Forest Labs)
- **SDXL Turbo** (Real-time generation)
- **Pika Labs** (Video generation)
- **RunwayML** (Advanced video)
- **ElevenLabs** (Voice generation)
- **Riffusion** (Music generation)

### Platform Integrations
- **Unity** (Direct import)
- **Unreal Engine** (MetaHuman compatible)
- **Roblox** (Avatar system)
- **VRChat** (Custom avatars)
- **Discord** (Bot integration)
- **Twitch** (Stream overlays)

## 🛠️ Development

### Adding New Features
1. Create service in `services/`
2. Add adapter if external provider
3. Create API endpoints
4. Update documentation
5. Add tests

### Testing
```bash
# Run tests
pytest tests/

# Test specific provider
GENERATION_API=stable_diffusion pytest tests/test_generation.py

# Test video backend
VIDEO_BACKEND=moviepy pytest tests/test_video.py
```

## 📚 Additional Resources

- [API Reference](./API_REFERENCE.md)
- [Provider Setup Guide](./PROVIDER_SETUP.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Contributing Guide](./CONTRIBUTING.md)