# 🔌 LucianMirror API Integration Guide for MySunshineStories

## Overview

LucianMirror provides a complete REST API that can be used without any frontend. This guide shows how to integrate it into MySunshineStories or any other application.

## 🚀 Quick Start

### 1. Start the API Server Only

```bash
cd backend
python -m uvicorn main:app --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 2. Test API Connection

```python
import requests

response = requests.get("http://localhost:8000/")
print(response.json())
# Output: {"status": "operational", "service": "LucianMirror Sprite Engine", ...}
```

## 📊 Complete API Workflow

### Step 1: Initialize Character

When a MySunshineStories user creates a Sunshine profile:

```python
import requests
import base64

# Convert uploaded photos to base64 or URLs
def prepare_photos(photo_files):
    photo_urls = []
    for photo in photo_files:
        # Option 1: Upload to your CDN and get URLs
        # photo_url = upload_to_cdn(photo)
        # photo_urls.append(photo_url)
        
        # Option 2: Convert to base64
        with open(photo, 'rb') as f:
            photo_base64 = base64.b64encode(f.read()).decode()
            photo_urls.append(f"data:image/jpeg;base64,{photo_base64}")
    return photo_urls

# Initialize character
character_data = {
    "character_id": "sunshine_123",  # Your internal ID
    "name": "Lucy",
    "reference_photos": prepare_photos(["photo1.jpg", "photo2.jpg"]),
    "physical_features": {
        "hair": "brown curly",
        "eyes": "blue",
        "skin": "fair"
    },
    "age": 6,
    "gender": "girl",
    "clothing": "blue dress",
    "style": "watercolor"
}

response = requests.post(
    "http://localhost:8000/api/characters/initialize",
    json=character_data
)

print(response.json())
# Output: {"status": "success", "character_id": "sunshine_123", "message": "Character initialized, sprite generation queued"}
```

### Step 2: Generate Sprites (Automatic or Manual)

#### Option A: Automatic Generation (Recommended)
The initialize endpoint automatically queues sprite generation. Check status:

```python
import time

# Wait for generation to complete
time.sleep(30)  # Generation takes 20-60 seconds typically

# Get generated sprites
response = requests.get(f"http://localhost:8000/api/sprites/sunshine_123")
sprites = response.json()

print(f"Generated {len(sprites['sprites']['by_pose'])} poses")
print(f"Generated {len(sprites['sprites']['by_emotion'])} emotions")
```

#### Option B: Manual Generation with Custom Settings

```python
generation_request = {
    "character_id": "sunshine_123",
    "character_data": {
        "name": "Lucy",
        "reference_photo": "https://your-cdn.com/photo.jpg",
        "style": "watercolor"
    },
    "poses": ["standing", "sitting", "walking", "sleeping"],  # Custom pose list
    "emotions": ["happy", "sad", "worried", "excited"],  # Custom emotion list
    "include_actions": True,  # Generate action sprites too
    "generation_api": "dalle"  # or "stable_diffusion", "replicate"
}

response = requests.post(
    "http://localhost:8000/api/sprites/generate",
    json=generation_request
)

result = response.json()
print(f"Generated {result['sprites_generated']} sprites")
print(f"Manifest URL: {result['manifest_url']}")
```

### Step 3: Process Story Scenes

When a user requests a story:

```python
# Your story text (from GPT-4 or your story generator)
story_text = """
Lucy was afraid of the dark. Every night when bedtime came, 
she would hide under her blanket feeling worried.

One evening, her mom gave her a special star nightlight.
Lucy felt happy as the soft glow filled her room.

That night, Lucy slept peacefully with a smile on her face.
"""

# Map character names in the story to character IDs
story_request = {
    "story_text": story_text,
    "character_mappings": {
        "Lucy": "sunshine_123",
        "mom": "parent_456"  # If you have parent sprites
    },
    "background_style": "watercolor",
    "generation_api": "dalle"
}

response = requests.post(
    "http://localhost:8000/api/stories/process",
    json=story_request
)

story_result = response.json()
```

### Step 4: Get Composed Scenes

The response contains fully composed scenes:

```python
for scene in story_result['scenes']:
    print(f"Scene {scene['index']}:")
    print(f"  Text: {scene['scene_text']}")
    print(f"  Background: {scene['background_url']}")
    print(f"  Sprite Used: {scene['sprite']}")
    print(f"  Composed Image: {scene['composed_url']}")  # Final image with sprite on background
```

## 🎯 Individual Operations

### Get Specific Sprite

```python
# Get all sprites for a character
response = requests.get("http://localhost:8000/api/sprites/sunshine_123")
sprites_data = response.json()

# Find specific sprite
happy_standing = None
for sprite in sprites_data['sprites']['by_pose'].get('standing', []):
    if sprite['emotion'] == 'happy':
        happy_standing = sprite
        break

print(f"Happy standing sprite: {happy_standing['url']}")
```

### Compose Single Scene

```python
scene_request = {
    "scene_text": "Lucy was happy playing in the park",
    "character_mappings": {"Lucy": "sunshine_123"},
    "background_style": "watercolor",
    "generation_api": "dalle",
    "auto_compose": True  # Automatically compose sprite onto background
}

response = requests.post(
    "http://localhost:8000/api/scenes/compose",
    json=scene_request
)

scene = response.json()
print(f"Composed scene URL: {scene['composed_url']}")
```

### Manual Composition

```python
# Manually specify sprite positions
composition_request = {
    "background_url": "https://your-cdn.com/park-background.jpg",
    "sprites": [
        {
            "url": "https://your-cdn.com/lucy-happy-standing.png",
            "x": 0.5,  # Center horizontally (0-1)
            "y": 0.7,  # 70% down vertically (0-1)
            "scale": 0.4  # 40% of canvas height
        }
    ],
    "output_format": "png"
}

response = requests.post(
    "http://localhost:8000/api/compose/manual",
    json=composition_request
)

result = response.json()
print(f"Manually composed image: {result['composed_url']}")
```

## 🧠 Learning & Feedback

The system learns from user interactions:

```python
# When a user likes/dislikes a scene
feedback = {
    "story_id": "story_abc123",
    "scene_index": 0,
    "success_score": 0.9,  # 0-1, higher is better
    "context": {
        "scene": "bedroom",
        "emotion": "worried",
        "character_id": "sunshine_123"
    },
    "sprite_choice": {
        "pose": "sitting",
        "emotion": "worried"
    }
}

response = requests.post(
    "http://localhost:8000/api/learning/feedback",
    json=feedback
)
```

## 🎮 Batch Processing

Process multiple stories efficiently:

```python
import asyncio
import aiohttp

async def process_story_batch(stories):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for story in stories:
            task = session.post(
                "http://localhost:8000/api/stories/process",
                json=story
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        return [await r.json() for r in responses]

# Process multiple stories
stories = [
    {"story_text": "...", "character_mappings": {...}},
    {"story_text": "...", "character_mappings": {...}},
]

results = asyncio.run(process_story_batch(stories))
```

## 📦 Sprite Export Options

### Get Sprite Sheet for Games

```python
response = requests.post(
    f"http://localhost:8000/api/sprites/sheet",
    json={
        "character_id": "sunshine_123",
        "output_format": "unity"  # or "godot", "web"
    }
)

sheet_data = response.json()
print(f"Sprite sheet URL: {sheet_data['sheet_url']}")
```

### Download All Sprites

```python
import os
import requests

def download_all_sprites(character_id, output_dir):
    response = requests.get(f"http://localhost:8000/api/sprites/{character_id}")
    sprites_data = response.json()
    
    os.makedirs(output_dir, exist_ok=True)
    
    for sprite_list in sprites_data['sprites']['by_pose'].values():
        for sprite in sprite_list:
            # Download sprite
            img_response = requests.get(sprite['url'])
            
            # Save to file
            filename = f"{sprite['pose']}_{sprite['emotion']}.png"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(img_response.content)
            
            print(f"Downloaded: {filename}")

download_all_sprites("sunshine_123", "./sprites_export")
```

## 🔄 WebSocket Support (Coming Soon)

For real-time generation updates:

```python
import websockets
import asyncio

async def monitor_generation(character_id):
    uri = f"ws://localhost:8000/ws/generation/{character_id}"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Progress: {data['progress']}% - {data['status']}")
            if data['complete']:
                break

asyncio.run(monitor_generation("sunshine_123"))
```

## 🛠 Error Handling

Always wrap API calls with proper error handling:

```python
def safe_api_call(url, method="GET", **kwargs):
    try:
        if method == "GET":
            response = requests.get(url, **kwargs)
        elif method == "POST":
            response = requests.post(url, **kwargs)
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to LucianMirror API")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Use the safe wrapper
result = safe_api_call(
    "http://localhost:8000/api/sprites/generate",
    method="POST",
    json=generation_request
)

if result:
    print("Generation successful!")
```

## 📊 API Rate Limits

Default limits (configurable):
- Sprite generation: 3 concurrent requests
- Story processing: 5 concurrent requests
- Composition: 10 concurrent requests

## 🔐 Authentication (Optional)

If you need to add authentication:

```python
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "X-Sunshine-User-ID": "user_123"
}

response = requests.post(
    "http://localhost:8000/api/sprites/generate",
    json=generation_request,
    headers=headers
)
```

## 🚀 Production Deployment

For MySunshineStories production:

1. Deploy backend to your infrastructure (AWS, GCP, etc.)
2. Set environment variables for API keys
3. Configure storage (R2 or S3)
4. Set up Redis for background jobs
5. Use a reverse proxy (nginx) for the API

## 📞 Support

- API Docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/

## Example Integration Code

Save this as `mysunshine_integration.py`:

```python
import requests
import time

class LucianMirrorClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def initialize_character(self, character_data):
        """Initialize a new character"""
        return self._post("/api/characters/initialize", character_data)
    
    def process_story(self, story_text, character_mappings):
        """Process a story into composed scenes"""
        return self._post("/api/stories/process", {
            "story_text": story_text,
            "character_mappings": character_mappings,
            "background_style": "watercolor",
            "generation_api": "dalle"
        })
    
    def get_sprites(self, character_id):
        """Get all sprites for a character"""
        return self._get(f"/api/sprites/{character_id}")
    
    def _get(self, endpoint):
        response = requests.get(f"{self.base_url}{endpoint}")
        response.raise_for_status()
        return response.json()
    
    def _post(self, endpoint, data):
        response = requests.post(f"{self.base_url}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()

# Use the client
client = LucianMirrorClient()

# Initialize character
result = client.initialize_character({
    "character_id": "test_123",
    "name": "Test Character",
    "reference_photos": ["photo_url_here"]
})

print(f"Character initialized: {result}")
```

That's it! The API is fully functional and ready for integration into MySunshineStories.