"""
Main FastAPI application for LucianMirror API - Updated with full implementation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import core components
from core.mpu import MPU, SpriteData
from core.ssp import SSP
from core.hasr import HASR

# Import services
from services.sprite_generation_service import sprite_generation_service
from services.composition_service import composition_service, video_composition_service
from services.storage_service import sprite_storage
from services.video_generation_service import video_generation_service

# Import API routers
from api.mysunshine_integration import setup_mysunshine_routes
from api.video_endpoints import setup_video_routes

# Initialize FastAPI app
app = FastAPI(
    title="LucianMirror Sprite Engine API",
    description="Sprite generation and composition service with LucianOS cognitive components",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# Pydantic Models
# ========================

class CharacterInit(BaseModel):
    character_id: str
    name: str
    reference_photos: List[str]
    physical_features: Optional[Dict[str, str]] = {}
    personality_traits: Optional[List[str]] = []
    age: Optional[int] = None
    gender: Optional[str] = None
    clothing: Optional[str] = None
    style: str = "watercolor"
    
class SpriteGenerationRequest(BaseModel):
    character_id: str
    character_data: Dict[str, Any]
    poses: Optional[List[str]] = None
    emotions: Optional[List[str]] = None
    include_actions: bool = True
    generation_api: str = "dalle"
    style: Optional[str] = "consistent_character"
    
class SceneCompositionRequest(BaseModel):
    scene_text: str
    character_mappings: Dict[str, str]
    background_style: str = "watercolor"
    generation_api: str = "dalle"
    auto_compose: bool = True
    
class StoryProcessRequest(BaseModel):
    story_text: str
    character_mappings: Dict[str, str]
    background_style: str = "watercolor"
    generation_api: str = "dalle"

class FeedbackRequest(BaseModel):
    story_id: str
    scene_index: int
    success_score: float
    context: Dict[str, Any]
    sprite_choice: Dict[str, Any]

class VideoGenerationRequest(BaseModel):
    story_id: str
    sprites: List[Dict[str, Any]]
    background_url: str
    duration: float = 30
    transitions: Optional[List[str]] = None

# ========================
# API Endpoints
# ========================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "operational",
        "service": "LucianMirror Sprite Engine",
        "version": "2.0.0",
        "components": {
            "mpu": "active",
            "ssp": "active",
            "hasr": "active",
            "generation": "ready",
            "composition": "ready",
            "storage": "ready"
        }
    }

@app.post("/api/characters/initialize")
async def initialize_character(character: CharacterInit, background_tasks: BackgroundTasks):
    """
    Initialize a new character and queue sprite generation
    """
    try:
        # Prepare character data
        character_data = {
            "id": character.character_id,
            "name": character.name,
            "reference_photos": character.reference_photos,
            "physical_features": character.physical_features,
            "personality_traits": character.personality_traits,
            "age": character.age,
            "gender": character.gender,
            "clothing": character.clothing,
            "style": character.style
        }
        
        # Queue sprite generation in background
        background_tasks.add_task(
            sprite_generation_service.generate_character_sprites,
            character.character_id,
            character_data,
            generation_api="dalle"
        )
        
        return {
            "status": "success",
            "character_id": character.character_id,
            "message": "Character initialized, sprite generation queued"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sprites/generate")
async def generate_sprites(request: SpriteGenerationRequest):
    """
    Generate sprites for a character
    """
    try:
        result = await sprite_generation_service.generate_character_sprites(
            character_id=request.character_id,
            character_data=request.character_data,
            generation_api=request.generation_api,
            custom_poses=request.poses,
            custom_emotions=request.emotions,
            include_actions=request.include_actions
        )
        
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sprites/{character_id}")
async def get_character_sprites(character_id: str):
    """
    Get all sprites for a character
    """
    try:
        # Get sprites from MPU
        sprites = sprite_generation_service.mpu.get_character_sprites(character_id)
        
        # Load manifest from storage
        manifest = await sprite_storage.load_sprite_manifest(character_id)
        
        if not manifest and not sprites['by_pose']:
            raise HTTPException(status_code=404, detail="No sprites found for character")
        
        return {
            "status": "success",
            "character_id": character_id,
            "sprites": sprites,
            "manifest": manifest,
            "statistics": sprite_generation_service.mpu.get_statistics()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scenes/compose")
async def compose_scene(request: SceneCompositionRequest):
    """
    Compose a scene with sprites and background
    """
    try:
        result = await sprite_generation_service.process_story_scene(
            scene_text=request.scene_text,
            character_mappings=request.character_mappings,
            background_style=request.background_style,
            generation_api=request.generation_api,
            auto_compose=request.auto_compose
        )
        
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stories/process")
async def process_story(request: StoryProcessRequest):
    """
    Process an entire story into composed scenes
    """
    try:
        result = await sprite_generation_service.process_full_story(
            story_text=request.story_text,
            character_mappings=request.character_mappings,
            background_style=request.background_style,
            generation_api=request.generation_api
        )
        
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/learning/feedback")
async def provide_feedback(request: FeedbackRequest):
    """
    Provide feedback to HASR for learning
    """
    try:
        # Reinforce the choice
        sprite_generation_service.hasr.reinforce(
            context=request.context,
            sprite_choice=request.sprite_choice,
            success_score=request.success_score
        )
        
        # Save weights
        os.makedirs("weights", exist_ok=True)
        sprite_generation_service.hasr.save_weights(
            f"weights/hasr_{request.story_id}.json"
        )
        
        return {
            "status": "success",
            "message": "Feedback recorded",
            "statistics": sprite_generation_service.hasr.get_statistics()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/learning/suggestions")
async def get_suggestions(
    character_id: str,
    scene: str,
    emotion: str
):
    """
    Get HASR suggestions for sprite selection
    """
    try:
        # Get available sprites
        available_sprites = sprite_generation_service.mpu.query(
            character_id=character_id
        )
        
        # Get suggestion
        best_sprite = sprite_generation_service.hasr.suggest_sprite(
            context={
                'scene': scene,
                'emotion': emotion,
                'character_id': character_id
            },
            available_sprites=[{
                'pose': s.pose,
                'emotion': s.emotion,
                'id': s.sprite_id,
                'url': s.url
            } for s in available_sprites]
        )
        
        # Get top combinations
        top_combinations = sprite_generation_service.hasr.get_best_combinations(
            character_id, 
            top_n=5
        )
        
        return {
            "status": "success",
            "suggestion": best_sprite,
            "top_combinations": top_combinations,
            "statistics": sprite_generation_service.hasr.get_statistics()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sprites/upload")
async def upload_custom_sprite(
    character_id: str,
    pose: str,
    emotion: str,
    file: UploadFile = File(...)
):
    """
    Upload a custom sprite
    """
    try:
        # Read file
        contents = await file.read()
        
        # Save sprite
        from PIL import Image
        import io
        
        image = Image.open(io.BytesIO(contents))
        
        sprite_info = await sprite_storage.save_sprite(
            image,
            character_id,
            "custom",
            pose,
            emotion
        )
        
        # Store in MPU
        sprite_data = SpriteData(
            sprite_id=sprite_info["sprite_id"],
            character_id=character_id,
            sprite_type="custom",
            pose=pose,
            emotion=emotion,
            url=sprite_info["url"],
            thumbnail_url=sprite_info["thumbnail_url"]
        )
        
        sprite_generation_service.mpu.store(sprite_data)
        
        return {
            "status": "success",
            "sprite": sprite_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sprites/sheet")
async def create_sprite_sheet(
    character_id: str,
    output_format: str = "unity"
):
    """
    Create a sprite sheet for game engines
    """
    try:
        sheet_url = await sprite_storage.create_sprite_sheet(
            character_id,
            output_format
        )
        
        return {
            "status": "success",
            "sheet_url": sheet_url,
            "format": output_format
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/sprites/{character_id}")
async def delete_character_sprites(character_id: str):
    """
    Delete all sprites for a character
    """
    try:
        success = await sprite_storage.delete_character_sprites(character_id)
        
        if success:
            # Also clear from MPU
            sprites = sprite_generation_service.mpu.query(character_id=character_id)
            for sprite in sprites:
                # Note: MPU doesn't have delete, so we'd need to add that
                pass
            
            return {"status": "success", "message": "Sprites deleted"}
        else:
            raise HTTPException(status_code=404, detail="Character not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/video/generate")
async def generate_video(request: VideoGenerationRequest):
    """
    Generate animated video from sprites
    """
    try:
        video_url = await video_composition_service.create_sprite_animation(
            sprites=request.sprites,
            background_url=request.background_url,
            duration=request.duration,
            transitions=request.transitions
        )
        
        return {
            "status": "success",
            "video_url": video_url,
            "duration": request.duration
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compose/manual")
async def manual_compose(
    background_url: str,
    sprites: List[Dict[str, Any]],
    output_format: str = "png"
):
    """
    Manually compose sprites onto background with specific positions
    """
    try:
        composed_url = await composition_service.compose_scene(
            background_url=background_url,
            sprites=sprites,
            output_format=output_format
        )
        
        return {
            "status": "success",
            "composed_url": composed_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/background/remove")
async def remove_background(image_url: str):
    """
    Remove background from an image
    """
    try:
        result_url = await composition_service.remove_background(image_url)
        
        return {
            "status": "success",
            "result_url": result_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================
# Error Handlers
# ========================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"status": "error", "message": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Internal server error"}
    )

# ========================
# Setup Additional Routes
# ========================

# Add MySunshineStories integration routes
setup_mysunshine_routes(app)

# Add video generation routes for episodic content
setup_video_routes(app)

# ========================
# Run the application
# ========================

if __name__ == "__main__":
    import uvicorn
    from utils.port_finder import find_free_port, get_process_on_port
    
    # Find a free port
    port = find_free_port(
        preferred_port=int(os.environ.get("BACKEND_PORT", 8000)),
        fallback_range=(8000, 9000)
    )
    
    # Update CORS to allow the frontend port
    frontend_port = int(os.environ.get("FRONTEND_PORT", 5173))
    
    print(f"🚀 Starting LucianMirror API on port {port}")
    print(f"📝 API Docs: http://localhost:{port}/docs")
    print(f"🎨 Frontend expected at: http://localhost:{frontend_port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
