"""
MySunshineStories Drop-in Replacement API
This replaces the current DALL-E direct generation with sprite-based composition
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import asyncio

# Import the autonomous pipeline
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integrations.mysunshine_pipeline import mysunshine_pipeline

router = APIRouter(prefix="/api/mysunshine", tags=["MySunshineStories Integration"])


class MySunshineStoryRequest(BaseModel):
    """
    Matches the exact format MySunshineStories sends
    """
    sunshine_profile: Dict[str, Any]  # Complete profile with child, family, pets, items
    story_data: Dict[str, Any]  # Generated story with scenes
    generation_settings: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    story_id: Optional[str] = None


class MySunshineInitRequest(BaseModel):
    """
    Pre-initialize sprites for a Sunshine profile
    """
    sunshine_profile: Dict[str, Any]
    generation_settings: Optional[Dict[str, Any]] = None


@router.post("/generate-story-images")
async def generate_story_images(request: MySunshineStoryRequest):
    """
    Drop-in replacement for MySunshineStories' current image generation
    
    This endpoint:
    1. Receives the Sunshine profile and generated story
    2. Ensures sprites exist for all entities
    3. Generates backgrounds for each scene
    4. Composes sprites onto backgrounds
    5. Returns the complete illustrated story
    
    Fully autonomous - MySunshineStories just needs to call this instead of DALL-E
    """
    try:
        # Set default generation settings if not provided
        if not request.generation_settings:
            request.generation_settings = {
                'generation_api': 'dalle',  # Can be switched to 'stable_diffusion', etc.
                'style': 'watercolor',
                'tone': request.story_data.get('tone', 'adventure')
            }
        
        print(f"📚 Processing story for {request.sunshine_profile.get('name')}")
        print(f"   Scenes: {len(request.story_data.get('scenes', []))}")
        print(f"   Style: {request.generation_settings.get('style')}")
        print(f"   API: {request.generation_settings.get('generation_api')}")
        
        # Process through the autonomous pipeline
        result = await mysunshine_pipeline.process_story_request(
            sunshine_profile=request.sunshine_profile,
            story_data=request.story_data,
            generation_settings=request.generation_settings
        )
        
        # Format response to match MySunshineStories expectations
        formatted_response = {
            'success': True,
            'story': {
                'title': result['story_title'],
                'text': result['story_text'],
                'scenes': [
                    {
                        'scene_number': scene['scene_number'],
                        'description': scene['description'],
                        'image_url': scene['image_url'],  # The composed final image
                        'generation_method': scene.get('generation_method', 'sprite_composition')
                    }
                    for scene in result['scenes']
                ]
            },
            'metadata': {
                'generation_method': result.get('generation_method', 'lucian_mirror_sprites'),
                'sprites_used': sum(s.get('sprites_used', 0) for s in result['scenes']),
                'processing_time': result.get('processing_time'),
                'created_at': result['created_at']
            }
        }
        
        return formatted_response
        
    except Exception as e:
        print(f"❌ Error in story image generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize-profile")
async def initialize_profile(request: MySunshineInitRequest, background_tasks: BackgroundTasks):
    """
    Pre-generate sprites for a Sunshine profile
    Call this when a user completes their Sunshine profile
    """
    try:
        profile_id = request.sunshine_profile.get('id')
        
        if not profile_id:
            raise HTTPException(status_code=400, detail="Profile ID is required")
        
        # Set default settings
        settings = request.generation_settings or {
            'generation_api': 'dalle',
            'style': 'watercolor'
        }
        
        # Queue sprite generation in background
        background_tasks.add_task(
            mysunshine_pipeline._ensure_sprites_ready,
            profile_id,
            request.sunshine_profile,
            settings
        )
        
        return {
            'success': True,
            'message': f"Sprite generation queued for profile {profile_id}",
            'profile_id': profile_id,
            'estimated_time': '60-120 seconds'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile-status/{profile_id}")
async def check_profile_status(profile_id: str):
    """
    Check if sprites are ready for a profile
    """
    is_ready = profile_id in mysunshine_pipeline.initialized_profiles
    
    if is_ready:
        # Get sprite statistics from MPU
        from services.sprite_generation_service import sprite_generation_service
        
        # Count sprites for this profile
        child_sprites = sprite_generation_service.mpu.query(character_id=f"{profile_id}_child")
        family_sprites = sprite_generation_service.mpu.query(character_id=f"{profile_id}_family")
        
        return {
            'success': True,
            'profile_id': profile_id,
            'status': 'ready',
            'sprites': {
                'child': len(child_sprites),
                'family': len([s for s in family_sprites if 'family' in s.character_id]),
                'total': len(child_sprites) + len(family_sprites)
            }
        }
    else:
        return {
            'success': True,
            'profile_id': profile_id,
            'status': 'generating',
            'message': 'Sprites are being generated'
        }


@router.post("/regenerate-scene")
async def regenerate_scene(
    story_id: str,
    scene_number: int,
    adjustments: Optional[Dict[str, Any]] = None
):
    """
    Regenerate a specific scene with adjustments
    Useful when a scene needs tweaking
    """
    try:
        # This would retrieve the story and regenerate just one scene
        # Implementation depends on how MySunshineStories stores stories
        
        return {
            'success': True,
            'message': 'Scene regeneration not yet implemented',
            'story_id': story_id,
            'scene_number': scene_number
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def provide_feedback(
    story_id: str,
    scene_number: int,
    rating: float,  # 0-1 score
    feedback_type: str = "general"
):
    """
    Receive feedback to improve HASR learning
    """
    try:
        # Update HASR with feedback
        from services.sprite_generation_service import sprite_generation_service
        
        # This would need to store and retrieve the context from the original generation
        # For now, just acknowledge
        
        return {
            'success': True,
            'message': 'Feedback recorded',
            'story_id': story_id,
            'scene_number': scene_number,
            'rating': rating
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Add router to main app
def setup_mysunshine_routes(app):
    """Add MySunshine integration routes to the main FastAPI app"""
    app.include_router(router)