# Provider Setup Guide

## Quick Start

LucianMirror supports multiple AI providers for image and video generation. This guide helps you set up and swap between providers.

## Image Generation Providers

### DALL-E 3 (OpenAI)

**Setup:**
```bash
export OPENAI_API_KEY="sk-..."
export GENERATION_API="dalle"
```

**Config:**
```python
{
    'model': 'dall-e-3',
    'quality': 'hd',  # or 'standard'
    'size': '1024x1024'  # or '1792x1024', '1024x1792'
}
```

**Pros:**
- Highest quality
- Best prompt adherence
- No setup required

**Cons:**
- Costs per image
- Rate limits
- No fine-tuning

---

### Stable Diffusion (Multiple Backends)

#### Option 1: Replicate (Cloud)

**Setup:**
```bash
export REPLICATE_API_TOKEN="r8_..."
export GENERATION_API="stable_diffusion"
export SD_BACKEND="replicate"
```

**Config:**
```python
{
    'model': 'stability-ai/sdxl',
    'num_inference_steps': 50,
    'guidance_scale': 7.5
}
```

**Pros:**
- No GPU required
- Multiple models
- Pay per use

#### Option 2: Local (Automatic1111)

**Setup:**
```bash
# Install Automatic1111
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
cd stable-diffusion-webui
./webui.sh --api

# Configure LucianMirror
export GENERATION_API="stable_diffusion"
export SD_BACKEND="local"
export SD_API_URL="http://localhost:7860"
```

**Config:**
```python
{
    'model': 'your_model.safetensors',
    'sampler': 'DPM++ 2M Karras',
    'steps': 30,
    'cfg_scale': 7
}
```

**Pros:**
- Free after GPU cost
- Full control
- Custom models
- No limits

**Cons:**
- Requires GPU
- Setup complexity

#### Option 3: ComfyUI (Local Advanced)

**Setup:**
```bash
# Install ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
python main.py --listen

# Configure LucianMirror
export GENERATION_API="stable_diffusion"
export SD_BACKEND="comfyui"
export COMFYUI_API_URL="http://localhost:8188"
```

**Workflow File:** `workflows/sprite_generation.json`

**Pros:**
- Advanced workflows
- Node-based control
- Best quality possible

---

### Midjourney

**Setup:**
```bash
export MJ_PROXY_URL="https://your-proxy.com"
export MJ_TOKEN="your_discord_token"
export GENERATION_API="midjourney"
```

**Config:**
```python
{
    'version': '6',
    'stylize': 100,
    'quality': 2
}
```

**Pros:**
- Artistic style
- Consistent characters
- High quality

**Cons:**
- Requires proxy
- Discord dependency
- Slower generation

---

### Leonardo.ai

**Setup:**
```bash
export LEONARDO_API_KEY="..."
export GENERATION_API="leonardo"
```

**Config:**
```python
{
    'model_id': 'leonardo-diffusion-xl',
    'num_images': 1,
    'guidance_scale': 7
}
```

**Pros:**
- Good pricing
- Multiple styles
- Built-in upscaling

---

## Video Generation Tools

### OpenCV (Default)

**Setup:**
```bash
pip install opencv-python
```

**When to use:**
- Quick processing
- Basic animations
- Low resource usage

### MoviePy (High Quality)

**Setup:**
```bash
pip install moviepy
```

**Config:**
```python
VIDEO_BACKEND="moviepy"
VIDEO_QUALITY="high"
VIDEO_CODEC="libx264"
VIDEO_BITRATE="5000k"
```

**When to use:**
- Professional quality
- Complex transitions
- Audio support needed

### FFmpeg (Professional)

**Setup:**
```bash
# Ubuntu/Debian
apt-get install ffmpeg

# MacOS
brew install ffmpeg

# Configure
export VIDEO_BACKEND="ffmpeg"
export FFMPEG_PATH="/usr/local/bin/ffmpeg"
```

**When to use:**
- Broadcast quality
- Specific codecs
- Streaming output

---

## Storage Providers

### Cloudflare R2 (Recommended)

**Setup:**
```bash
export STORAGE_BACKEND="r2"
export R2_ACCOUNT_ID="..."
export R2_ACCESS_KEY="..."
export R2_SECRET_KEY="..."
export R2_BUCKET="lucianmirror"
```

**Pros:**
- No egress fees
- S3 compatible
- Global CDN

### AWS S3

**Setup:**
```bash
export STORAGE_BACKEND="s3"
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export S3_BUCKET="lucianmirror"
export AWS_REGION="us-east-1"
```

### Local Storage (Development)

**Setup:**
```bash
export STORAGE_BACKEND="local"
export STORAGE_PATH="/var/lucianmirror/storage"
```

---

## Switching Providers at Runtime

### Method 1: Environment Variables

```bash
# Switch to Stable Diffusion
export GENERATION_API="stable_diffusion"

# Switch to MoviePy for video
export VIDEO_BACKEND="moviepy"

# Restart application
python backend/main.py
```

### Method 2: API Parameter

```python
# In your API call
response = requests.post('/api/sprites/generate', json={
    'character_id': 'hero_123',
    'generation_api': 'stable_diffusion',  # Override default
    'character_data': {...}
})
```

### Method 3: Configuration File

Create `config/providers.json`:
```json
{
    "default_image_provider": "stable_diffusion",
    "default_video_backend": "moviepy",
    "fallback_chain": [
        "dalle",
        "stable_diffusion",
        "leonardo"
    ],
    "provider_weights": {
        "quality": {
            "dalle": 0.9,
            "stable_diffusion": 0.7,
            "leonardo": 0.6
        },
        "speed": {
            "stable_diffusion": 0.9,
            "leonardo": 0.8,
            "dalle": 0.5
        }
    }
}
```

---

## Provider Fallback Chain

Configure automatic fallback when providers fail:

```python
# In config/fallback.py
FALLBACK_CHAIN = [
    {
        'provider': 'dalle',
        'max_retries': 2,
        'timeout': 30
    },
    {
        'provider': 'stable_diffusion',
        'max_retries': 3,
        'timeout': 60
    },
    {
        'provider': 'leonardo',
        'max_retries': 2,
        'timeout': 45
    }
]
```

---

## Cost Optimization

### Provider Costs (as of 2024)

| Provider | Cost per Image | Speed | Quality |
|----------|---------------|-------|---------|
| DALL-E 3 HD | $0.08 | Fast | Excellent |
| DALL-E 3 Standard | $0.04 | Fast | Very Good |
| Stable Diffusion (Replicate) | $0.002 | Medium | Good |
| Stable Diffusion (Local) | $0 | Varies | Good |
| Leonardo.ai | $0.005 | Fast | Good |
| Midjourney | ~$0.01 | Slow | Excellent |

### Optimization Strategies

1. **Development**: Use local Stable Diffusion
2. **Testing**: Use Replicate or Leonardo
3. **Production**: Mix based on importance
   - Hero sprites: DALL-E 3
   - Background characters: Stable Diffusion
   - Backgrounds: Leonardo

---

## Custom Provider Implementation

### Step 1: Create Adapter

```python
# adapters/custom_provider.py
from adapters.generation_adapters import GenerationAdapter

class CustomProviderAdapter(GenerationAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.custom.com"
    
    async def generate_sprite(self, prompt: str, **kwargs) -> str:
        # Your implementation
        response = await self._call_api(prompt, **kwargs)
        return response['image_url']
    
    async def generate_background(self, setting: str, **kwargs) -> str:
        prompt = f"Background scene: {setting}, no people"
        return await self.generate_sprite(prompt, **kwargs)
```

### Step 2: Register Provider

```python
# adapters/__init__.py
from adapters.custom_provider import CustomProviderAdapter

AdapterFactory.register('custom', CustomProviderAdapter)
```

### Step 3: Configure

```bash
export GENERATION_API="custom"
export CUSTOM_API_KEY="..."
```

---

## Testing Providers

### Test Script

```python
# test_provider.py
import asyncio
from adapters.generation_adapters import AdapterFactory

async def test_provider(provider_name):
    adapter = AdapterFactory.create_adapter(provider_name)
    
    # Test sprite generation
    sprite_url = await adapter.generate_sprite(
        "A happy child character, watercolor style"
    )
    print(f"✅ {provider_name} sprite: {sprite_url}")
    
    # Test background
    bg_url = await adapter.generate_background(
        "Magical forest", "day", "watercolor"
    )
    print(f"✅ {provider_name} background: {bg_url}")

# Test all providers
asyncio.run(test_provider('dalle'))
asyncio.run(test_provider('stable_diffusion'))
```

---

## Troubleshooting

### Common Issues

#### DALL-E Rate Limits
```python
# Add retry logic
DALLE_CONFIG = {
    'max_retries': 3,
    'retry_delay': 5,
    'rate_limit_per_minute': 50
}
```

#### Stable Diffusion Memory Issues
```bash
# Reduce batch size
export SD_BATCH_SIZE=1
export SD_MAX_RESOLUTION=512
```

#### Video Generation Failures
```bash
# Check ffmpeg installation
ffmpeg -version

# Use fallback
export VIDEO_FALLBACK="gif"
```

---

## Performance Benchmarks

| Task | DALL-E 3 | SD (Local) | SD (Cloud) | Leonardo |
|------|----------|------------|------------|----------|
| Single Sprite | 2-3s | 5-10s | 3-5s | 2-4s |
| Background | 2-3s | 8-15s | 4-6s | 3-5s |
| Batch (10) | 20-30s | 50-100s | 30-50s | 20-40s |
| Memory Usage | Low | High | Low | Low |
| GPU Required | No | Yes | No | No |

---

## Recommended Setups

### For Development
```bash
# Use local SD for free unlimited generation
export GENERATION_API="stable_diffusion"
export SD_BACKEND="local"
export VIDEO_BACKEND="opencv"
export STORAGE_BACKEND="local"
```

### For Production
```bash
# Balance quality and cost
export GENERATION_API="dalle"  # Primary
export FALLBACK_PROVIDER="stable_diffusion"
export VIDEO_BACKEND="moviepy"
export STORAGE_BACKEND="r2"
```

### For Enterprise
```bash
# Maximum quality and reliability
export GENERATION_API="dalle"
export VIDEO_BACKEND="ffmpeg"
export STORAGE_BACKEND="s3"
export ENABLE_FALLBACK="true"
export ENABLE_CACHING="true"
```