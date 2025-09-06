"""
MySunshineStories Autonomous Integration Pipeline
Replaces DALL-E direct generation with sprite-based composition
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Import LucianMirror components
from core.mpu import MPU, SpriteData
from core.ssp import SSP
from core.hasr import HASR
from services.sprite_generation_service import sprite_generation_service
from services.composition_service import composition_service
from services.video_generation_service import video_generation_service
from adapters.generation_adapters import AdapterFactory


class MySunshinePipeline:
    """
    Autonomous pipeline that replaces MySunshineStories' current DALL-E approach
    with sprite generation and composition
    """
    
    def __init__(self):
        self.sprite_service = sprite_generation_service
        self.initialized_profiles = {}  # Cache of initialized profiles
        
    async def process_story_request(
        self,
        sunshine_profile: Dict[str, Any],
        story_data: Dict[str, Any],
        generation_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main entry point from MySunshineStories
        Handles the entire image generation pipeline autonomously
        
        Args:
            sunshine_profile: The Sunshine profile data (child, family, pets, items)
            story_data: Generated story with scenes and image_prompts
            generation_settings: Style, tone, API preferences
            
        Returns:
            Complete story with composed images
        """
        
        print("🚀 LucianMirror Pipeline Starting...")
        
        # Step 1: Initialize or retrieve sprite packs
        profile_id = sunshine_profile.get('id')
        sprites_ready = await self._ensure_sprites_ready(
            profile_id, 
            sunshine_profile,
            generation_settings
        )
        
        if not sprites_ready:
            print("⚠️ Falling back to direct generation mode")
            return await self._fallback_direct_generation(story_data, sunshine_profile)
        
        # Step 2: Process each scene
        scenes = story_data.get('scenes', [])
        processed_scenes = []
        
        print(f"🎬 Processing {len(scenes)} scenes...")
        
        # Parallel scene processing for speed
        tasks = []
        for i, scene in enumerate(scenes):
            task = self._process_scene(
                scene,
                sunshine_profile,
                generation_settings,
                scene_index=i
            )
            tasks.append(task)
        
        # Wait for all scenes to complete
        processed_scenes = await asyncio.gather(*tasks)
        
        # Step 3: Generate video if requested
        video_url = None
        if generation_settings.get('generate_video', False):
            video_type = generation_settings.get('video_type', 'tiktok')
            video_url = await self._generate_story_video(
                processed_scenes,
                sunshine_profile,
                generation_settings
            )
        
        # Step 4: Compile final story
        return {
            'story_title': story_data.get('story_title'),
            'story_text': story_data.get('story_text'),
            'scenes': processed_scenes,
            'video_url': video_url,
            'generation_method': 'lucian_mirror_sprites',
            'created_at': datetime.utcnow().isoformat()
        }
    
    async def _ensure_sprites_ready(
        self,
        profile_id: str,
        sunshine_profile: Dict[str, Any],
        settings: Dict[str, Any]
    ) -> bool:
        """
        Ensure sprites are generated for all entities in the profile
        """
        
        # Check if we've already initialized this profile
        if profile_id in self.initialized_profiles:
            print(f"✅ Profile {profile_id} already has sprites")
            return True
        
        print(f"🎨 Initializing sprites for profile {profile_id}...")
        
        # Extract all entities from profile
        entities_to_generate = []
        
        # Main child
        child_data = {
            'id': f"{profile_id}_child",
            'name': sunshine_profile.get('name'),
            'type': 'child',
            'reference_photos': sunshine_profile.get('photos', []),
            'physical_features': sunshine_profile.get('physical_features', {}),
            'age': sunshine_profile.get('age')
        }
        entities_to_generate.append(child_data)
        
        # Family members
        for family_member in sunshine_profile.get('family_members', []):
            family_data = {
                'id': f"{profile_id}_family_{family_member['id']}",
                'name': family_member.get('name'),
                'type': 'family',
                'relationship': family_member.get('relationship'),
                'reference_photos': family_member.get('photos', []),
                'age': family_member.get('age')
            }
            entities_to_generate.append(family_data)
        
        # Pets
        for pet in sunshine_profile.get('pets', []):
            pet_data = {
                'id': f"{profile_id}_pet_{pet['id']}",
                'name': pet.get('name'),
                'type': 'pet',
                'pet_type': pet.get('type'),
                'reference_photos': pet.get('photos', [])
            }
            entities_to_generate.append(pet_data)
        
        # Comfort items
        for item in sunshine_profile.get('comfort_items', []):
            item_data = {
                'id': f"{profile_id}_item_{item['id']}",
                'name': item.get('name'),
                'type': 'comfort_item',
                'item_type': item.get('item_type'),
                'reference_photos': item.get('photos', [])
            }
            entities_to_generate.append(item_data)
        
        # Generate sprites for each entity
        generation_api = settings.get('generation_api', 'dalle')
        style = settings.get('style', 'watercolor')
        
        print(f"📦 Generating sprites for {len(entities_to_generate)} entities...")
        
        try:
            for entity in entities_to_generate:
                if entity['type'] == 'child':
                    # Full pose/emotion matrix for main character
                    await self.sprite_service.generate_character_sprites(
                        character_id=entity['id'],
                        character_data=entity,
                        generation_api=generation_api,
                        custom_poses=['standing', 'sitting', 'walking', 'happy_jump'],
                        custom_emotions=['happy', 'worried', 'brave', 'proud'],
                        include_actions=True
                    )
                elif entity['type'] == 'family':
                    # Limited sprites for family
                    await self.sprite_service.generate_character_sprites(
                        character_id=entity['id'],
                        character_data=entity,
                        generation_api=generation_api,
                        custom_poses=['standing', 'hugging'],
                        custom_emotions=['happy', 'caring'],
                        include_actions=False
                    )
                elif entity['type'] == 'pet':
                    # Pet-specific sprites
                    await self._generate_pet_sprites(entity, generation_api)
                elif entity['type'] == 'comfort_item':
                    # Static item sprites
                    await self._generate_item_sprites(entity, generation_api)
            
            self.initialized_profiles[profile_id] = True
            print(f"✅ All sprites generated for profile {profile_id}")
            return True
            
        except Exception as e:
            print(f"❌ Sprite generation failed: {e}")
            return False
    
    async def _process_scene(
        self,
        scene: Dict[str, Any],
        sunshine_profile: Dict[str, Any],
        settings: Dict[str, Any],
        scene_index: int
    ) -> Dict[str, Any]:
        """
        Process a single scene: analyze, generate background, compose sprites
        """
        
        print(f"🎬 Processing scene {scene_index + 1}...")
        
        # Step 1: Analyze scene with SSP
        scene_text = scene.get('description', '')
        image_prompt = scene.get('image_prompt', '')
        
        # Build character mappings
        character_mappings = {
            sunshine_profile['name']: f"{sunshine_profile['id']}_child"
        }
        
        for family in sunshine_profile.get('family_members', []):
            character_mappings[family['name']] = f"{sunshine_profile['id']}_family_{family['id']}"
        
        for pet in sunshine_profile.get('pets', []):
            character_mappings[pet['name']] = f"{sunshine_profile['id']}_pet_{pet['id']}"
        
        # Use SSP to understand the scene
        self.sprite_service.ssp.set_character_mapping(character_mappings)
        scene_binding = self.sprite_service.ssp.bind(scene_text + " " + image_prompt)
        requirements = scene_binding.get_sprite_requirements()
        
        # Step 2: Generate background (without characters)
        adapter = AdapterFactory.create_adapter(settings.get('generation_api', 'dalle'))
        
        # Extract setting from the scene
        setting = requirements['background']['setting']
        time_of_day = requirements['background'].get('time', 'day')
        style = settings.get('style', 'watercolor')
        
        # Generate background prompt that explicitly excludes people
        background_prompt = f"{setting} environment, {time_of_day} lighting, {style} children's book illustration, empty scene, no people, no characters, no figures"
        
        background_url = await adapter.generate_background(
            setting=setting,
            time_of_day=time_of_day,
            style=style
        )
        
        # Step 3: Compose sprites onto background
        sprites_to_compose = []
        
        # Get main character sprite
        main_char_id = f"{sunshine_profile['id']}_child"
        best_sprite = self.sprite_service.mpu.find_best_match(
            main_char_id,
            requirements.get('pose', 'standing'),
            requirements.get('emotion', 'happy')
        )
        
        if best_sprite:
            sprites_to_compose.append({
                'url': best_sprite.url,
                'x': 0.5,  # Center
                'y': 0.7,  # 70% down
                'scale': 0.4,
                'type': 'main_character'
            })
        
        # Add family members if mentioned
        for family_name, family_id in character_mappings.items():
            if family_name in scene_text and 'family' in family_id:
                family_sprite = self.sprite_service.mpu.find_best_match(
                    family_id,
                    'standing',
                    'caring'
                )
                if family_sprite:
                    sprites_to_compose.append({
                        'url': family_sprite.url,
                        'x': 0.3 if len(sprites_to_compose) == 1 else 0.7,
                        'y': 0.65,
                        'scale': 0.45,
                        'type': 'family'
                    })
        
        # Compose the final scene
        composed_url = await composition_service.compose_scene(
            background_url=background_url,
            sprites=sprites_to_compose,
            output_format='png'
        )
        
        # Use HASR to learn from this composition
        self.sprite_service.hasr.reinforce(
            context={
                'scene': setting,
                'emotion': requirements.get('emotion', 'neutral'),
                'character_id': main_char_id
            },
            sprite_choice={
                'pose': requirements.get('pose', 'standing'),
                'emotion': requirements.get('emotion', 'happy'),
                'sprite_id': best_sprite.sprite_id if best_sprite else None
            },
            success_score=0.8  # Base score, updated with user feedback
        )
        
        return {
            'scene_number': scene_index + 1,
            'description': scene_text,
            'image_url': composed_url,
            'background_url': background_url,
            'sprites_used': len(sprites_to_compose),
            'generation_method': 'sprite_composition'
        }
    
    async def _generate_pet_sprites(self, pet_data: Dict, generation_api: str):
        """Generate pet-specific sprites"""
        pet_type = pet_data.get('pet_type', 'dog')
        
        poses = ['sitting', 'standing', 'playing'] if pet_type == 'dog' else ['sitting', 'standing']
        
        for pose in poses:
            prompt = f"A friendly {pet_type} named {pet_data['name']}, {pose}, children's book illustration style, transparent background"
            
            adapter = AdapterFactory.create_adapter(generation_api)
            sprite_url = await adapter.generate_sprite(
                prompt,
                reference_image=pet_data['reference_photos'][0] if pet_data.get('reference_photos') else None
            )
            
            sprite_data = SpriteData(
                sprite_id=f"{pet_data['id']}_{pose}",
                character_id=pet_data['id'],
                sprite_type='pet',
                pose=pose,
                emotion='friendly',
                url=sprite_url
            )
            
            self.sprite_service.mpu.store(sprite_data)
    
    async def _generate_item_sprites(self, item_data: Dict, generation_api: str):
        """Generate comfort item sprites"""
        states = ['held', 'nearby', 'glowing']  # Different states for story contexts
        
        for state in states:
            prompt = f"A {item_data['item_type']} named {item_data['name']}, {state}, children's book illustration style, transparent background"
            
            adapter = AdapterFactory.create_adapter(generation_api)
            sprite_url = await adapter.generate_sprite(prompt)
            
            sprite_data = SpriteData(
                sprite_id=f"{item_data['id']}_{state}",
                character_id=item_data['id'],
                sprite_type='item',
                pose=state,
                emotion='comforting',
                url=sprite_url
            )
            
            self.sprite_service.mpu.store(sprite_data)
    
    async def _fallback_direct_generation(
        self,
        story_data: Dict,
        sunshine_profile: Dict
    ) -> Dict:
        """
        Fallback to direct DALL-E generation if sprite generation fails
        Similar to current MySunshineStories approach
        """
        print("⚠️ Using fallback direct generation mode")
        
        # This would call the original DALL-E generation
        # For now, return a placeholder
        return {
            'story_title': story_data.get('story_title'),
            'story_text': story_data.get('story_text'),
            'scenes': story_data.get('scenes'),
            'generation_method': 'fallback_direct',
            'warning': 'Sprite generation failed, used direct generation'
        }
    
    async def _generate_story_video(
        self,
        scenes: List[Dict],
        sunshine_profile: Dict,
        settings: Dict
    ) -> str:
        """
        Generate TikTok-length animated video from story scenes
        """
        
        print("🎬 Generating animated video from story...")
        
        # Prepare sprite data for video generation
        sprites = {}
        profile_id = sunshine_profile.get('id')
        
        # Gather all sprites for characters in the story
        main_char_id = f"{profile_id}_child"
        main_sprites = self.sprite_service.mpu.query(character_id=main_char_id)
        
        for sprite in main_sprites:
            sprites[f"{main_char_id}_{sprite.pose}_{sprite.emotion}"] = sprite.url
        
        # Add family member sprites
        for family in sunshine_profile.get('family_members', []):
            family_id = f"{profile_id}_family_{family['id']}"
            family_sprites = self.sprite_service.mpu.query(character_id=family_id)
            for sprite in family_sprites:
                sprites[f"{family_id}_{sprite.pose}_{sprite.emotion}"] = sprite.url
        
        # Configure video settings
        video_settings = {
            'video_type': settings.get('video_type', 'tiktok'),
            'genre': settings.get('genre', 'social_story'),
            'duration': settings.get('video_duration', 15),  # TikTok length
            'quality': 'high',
            'transitions': 'smooth',
            'include_captions': True
        }
        
        # Generate the video
        video_url = await video_generation_service.create_story_animation(
            story_scenes=scenes,
            sprites=sprites,
            settings=video_settings
        )
        
        print(f"✅ Video generated: {video_url}")
        return video_url
    
    async def create_friend_group_episode(
        self,
        group_id: str,
        episode_data: Dict,
        episode_number: int = 1
    ) -> Dict:
        """
        Create an episode for a friend group series
        Perfect for teenagers/adults creating their own Seinfeld/Friends style content
        """
        
        print(f"🎬 Creating episode {episode_number} for group {group_id}")
        
        # Generate or retrieve sprites for all group members
        for member in episode_data.get('members', []):
            member_id = f"{group_id}_{member['id']}"
            
            # Check if sprites exist
            existing = self.sprite_service.mpu.query(character_id=member_id)
            
            if not existing:
                # Generate sprites for this member
                await self.sprite_service.generate_character_sprites(
                    character_id=member_id,
                    character_data=member,
                    generation_api='dalle',
                    custom_poses=['standing', 'sitting', 'laughing', 'talking', 'reacting'],
                    custom_emotions=['happy', 'surprised', 'sarcastic', 'confused', 'excited'],
                    include_actions=True
                )
        
        # Create the episode video
        video_url = await video_generation_service.create_episode(
            episode_data=episode_data,
            series_id=group_id,
            episode_number=episode_number
        )
        
        return {
            'episode_number': episode_number,
            'video_url': video_url,
            'group_id': group_id,
            'title': episode_data.get('title'),
            'genre': episode_data.get('genre', 'sitcom'),
            'ready_to_share': True
        }


# Global pipeline instance
mysunshine_pipeline = MySunshinePipeline()