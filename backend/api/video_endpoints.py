"""
Video Generation API Endpoints
Supports episodic content, friend group sitcoms, social stories
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from services.video_generation_service import video_generation_service
from services.sprite_generation_service import sprite_generation_service

router = APIRouter(prefix="/api/video", tags=["Video Generation"])


class EpisodeRequest(BaseModel):
    """Request for creating an episode"""
    series_id: Optional[str] = None  # None for first episode
    episode_number: int = 1
    title: str
    genre: str = "sitcom"  # sitcom, sci_fi, romance, old_style, social_story
    characters: List[Dict[str, Any]]  # Friend group with names, personalities
    story_beats: List[Dict[str, Any]]  # Plot points for the episode
    target_issue: Optional[str] = None  # For social stories
    has_cliffhanger: bool = False
    duration: str = "short"  # short (15s), medium (60s), full (3min)


class VideoGenerationRequest(BaseModel):
    """Standard video generation request"""
    scenes: List[Dict[str, Any]]
    sprites: Dict[str, Any]
    settings: Dict[str, Any]
    video_type: str = "tiktok"


class FriendGroupRequest(BaseModel):
    """Initialize a friend group for episodic content"""
    group_name: str
    members: List[Dict[str, Any]]  # Each friend's details
    setting: str  # School, neighborhood, space station, etc.
    genre: str = "sitcom"
    age_group: str = "teen"  # teen, young_adult, adult


@router.post("/create-episode")
async def create_episode(request: EpisodeRequest):
    """
    Create an episode for a series (sitcom, drama, etc.)
    Perfect for teenagers creating their own shows with friends
    """
    try:
        # Generate series ID if first episode
        if not request.series_id:
            request.series_id = f"series_{uuid.uuid4().hex[:8]}"
            print(f"🎬 Starting new series: {request.series_id}")
        
        print(f"📺 Creating episode {request.episode_number} of {request.title}")
        print(f"   Genre: {request.genre}")
        print(f"   Characters: {len(request.characters)}")
        
        # Ensure sprites exist for all characters
        for character in request.characters:
            await sprite_generation_service.generate_character_sprites(
                character_id=f"{request.series_id}_{character['id']}",
                character_data=character,
                generation_api='dalle',  # Can be configurable
                custom_poses=['standing', 'sitting', 'walking', 'gesturing', 'reacting'],
                custom_emotions=['happy', 'surprised', 'annoyed', 'laughing', 'thinking'],
                include_actions=True
            )
        
        # Create the episode
        episode_data = {
            'title': request.title,
            'genre': request.genre,
            'characters': request.characters,
            'story_beats': request.story_beats,
            'has_cliffhanger': request.has_cliffhanger,
            'settings': {
                'genre': request.genre,
                'duration': request.duration,
                'video_type': 'episode'
            }
        }
        
        video_url = await video_generation_service.create_episode(
            episode_data=episode_data,
            series_id=request.series_id,
            episode_number=request.episode_number
        )
        
        return {
            'success': True,
            'series_id': request.series_id,
            'episode_number': request.episode_number,
            'video_url': video_url,
            'title': request.title,
            'next_episode_hint': 'Use the same series_id for episode continuity'
        }
        
    except Exception as e:
        print(f"❌ Episode creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-social-story")
async def create_social_story(
    target_issue: str,
    story_data: Dict[str, Any],
    audience_age: str = "teen"
):
    """
    Create educational videos addressing real-world issues
    Helps teenagers process and solve social challenges
    """
    try:
        print(f"🎓 Creating social story for issue: {target_issue}")
        print(f"   Target audience: {audience_age}")
        
        video_url = await video_generation_service.create_social_story_video(
            story_data=story_data,
            target_issue=target_issue,
            audience_age=audience_age
        )
        
        return {
            'success': True,
            'video_url': video_url,
            'target_issue': target_issue,
            'educational_value': 'high',
            'share_ready': True
        }
        
    except Exception as e:
        print(f"❌ Social story creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize-friend-group")
async def initialize_friend_group(request: FriendGroupRequest, background_tasks: BackgroundTasks):
    """
    Set up a friend group for creating episodic content
    Pre-generates all character sprites for consistency
    """
    try:
        group_id = f"group_{uuid.uuid4().hex[:8]}"
        
        print(f"👥 Initializing friend group: {request.group_name}")
        print(f"   Members: {len(request.members)}")
        print(f"   Setting: {request.setting}")
        print(f"   Genre: {request.genre}")
        
        # Queue sprite generation for all friends
        for member in request.members:
            background_tasks.add_task(
                sprite_generation_service.generate_character_sprites,
                character_id=f"{group_id}_{member['id']}",
                character_data=member,
                generation_api='dalle',
                custom_poses=['standing', 'sitting', 'walking', 'laughing', 'high_five'],
                custom_emotions=['happy', 'excited', 'cool', 'surprised', 'proud'],
                include_actions=True
            )
        
        return {
            'success': True,
            'group_id': group_id,
            'group_name': request.group_name,
            'members_count': len(request.members),
            'ready_in': '60-90 seconds',
            'tip': 'Use this group_id when creating episodes'
        }
        
    except Exception as e:
        print(f"❌ Friend group initialization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-video")
async def generate_standard_video(request: VideoGenerationRequest):
    """
    Standard video generation from scenes and sprites
    """
    try:
        video_url = await video_generation_service.create_story_animation(
            story_scenes=request.scenes,
            sprites=request.sprites,
            settings=request.settings
        )
        
        return {
            'success': True,
            'video_url': video_url,
            'video_type': request.video_type,
            'created_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Video generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/series/{series_id}/info")
async def get_series_info(series_id: str):
    """
    Get information about a series and its episodes
    """
    try:
        # Check if series exists in cache
        if series_id in video_generation_service.episode_cache:
            series_data = video_generation_service.episode_cache[series_id]
            
            return {
                'success': True,
                'series_id': series_id,
                'characters': series_data.get('characters', []),
                'sprites_ready': True,
                'settings': series_data.get('settings', {})
            }
        else:
            return {
                'success': False,
                'message': 'Series not found',
                'series_id': series_id
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-tiktok")
async def quick_tiktok_video(
    text: str,
    character_name: str,
    emotion: str = "happy",
    genre: str = "sitcom"
):
    """
    Quick TikTok video generation with minimal setup
    Perfect for viral content creation
    """
    try:
        # Simple scene generation
        scenes = [{
            'description': text,
            'character': character_name,
            'emotion': emotion
        }]
        
        settings = {
            'video_type': 'tiktok',
            'genre': genre,
            'duration': 15
        }
        
        # Quick sprite generation if needed
        sprites = await sprite_generation_service.quick_generate(
            character_name=character_name,
            emotion=emotion
        )
        
        video_url = await video_generation_service.create_story_animation(
            story_scenes=scenes,
            sprites=sprites,
            settings=settings
        )
        
        return {
            'success': True,
            'video_url': video_url,
            'ready_to_post': True,
            'platform': 'tiktok',
            'duration': 15
        }
        
    except Exception as e:
        print(f"❌ Quick TikTok generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-rpg-hero")
async def create_rpg_hero(
    character_name: str,
    character_data: Dict[str, Any],
    game_engine: str = "unity",
    include_equipment: bool = True
):
    """
    Create a complete RPG hero package with YOU as the main character
    Perfect for personal RPG games and adventures
    """
    try:
        from services.game_asset_service import game_asset_service
        
        character_id = f"hero_{uuid.uuid4().hex[:8]}"
        
        print(f"🗡️ Creating RPG hero: {character_name}")
        print(f"   Game Engine: {game_engine}")
        print(f"   Equipment: {'Yes' if include_equipment else 'No'}")
        
        # Create the hero package
        hero_package = await game_asset_service.create_hero_package(
            character_id=character_id,
            character_data={
                'name': character_name,
                **character_data
            },
            game_engine=game_engine,
            include_equipment=include_equipment
        )
        
        return {
            'success': True,
            'hero_id': character_id,
            'hero_name': character_name,
            'sprite_sheets': hero_package['sprite_sheets'],
            'equipment': hero_package.get('equipment_sheets', {}),
            'animations': hero_package['animations'],
            'character_stats': hero_package['character_stats'],
            'game_engine': game_engine,
            'download_url': hero_package.get('download_url'),
            'message': 'Your RPG hero is ready for adventure!'
        }
        
    except Exception as e:
        print(f"❌ RPG hero creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-game-world")
async def create_game_world(
    world_name: str,
    hero_id: str,
    npcs: List[Dict[str, Any]],
    world_style: str = "fantasy",
    game_engine: str = "unity"
):
    """
    Create a complete game world with your hero and NPCs
    """
    try:
        from services.game_asset_service import game_asset_service
        
        print(f"🌍 Creating game world: {world_name}")
        print(f"   Style: {world_style}")
        print(f"   NPCs: {len(npcs)}")
        
        # Create NPC pack
        npc_pack = await game_asset_service.create_npc_pack(
            npcs=npcs,
            game_engine=game_engine
        )
        
        # Generate world backgrounds/tilesets
        # This would integrate with the background generation
        
        return {
            'success': True,
            'world_name': world_name,
            'hero_id': hero_id,
            'npc_pack': npc_pack,
            'world_style': world_style,
            'game_engine': game_engine,
            'ready_to_play': True
        }
        
    except Exception as e:
        print(f"❌ Game world creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/game-assets/{character_id}/export")
async def export_game_assets(
    character_id: str,
    game_engine: str = "unity",
    format: str = "package"
):
    """
    Export character assets for specific game engine
    """
    try:
        from services.game_asset_service import game_asset_service
        
        export_url = await game_asset_service.export_for_game_engine(
            character_id=character_id,
            game_engine=game_engine,
            export_format=format
        )
        
        return {
            'success': True,
            'character_id': character_id,
            'export_url': export_url,
            'game_engine': game_engine,
            'format': format
        }
        
    except Exception as e:
        print(f"❌ Asset export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Add endpoints to main app
def setup_video_routes(app):
    """Add video generation routes to the main FastAPI app"""
    app.include_router(router)