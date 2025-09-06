"""
Main Sprite Generation Service
Orchestrates the complete sprite generation pipeline
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from PIL import Image
import io
import httpx

# Import core components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.mpu import MPU, SpriteData
from core.ssp import SSP
from core.hasr import HASR

# Import services
from adapters.generation_adapters import AdapterFactory
from services.composition_service import composition_service
from services.storage_service import sprite_storage


class SpriteGenerationService:
    """Main service for sprite generation and management"""
    
    def __init__(self):
        # Initialize core components
        self.mpu = MPU(['character', 'pose', 'emotion', 'scene'])
        self.ssp = SSP()
        self.hasr = HASR()
        
        # Default generation settings
        self.default_poses = [
            "standing", "sitting", "walking", "running", 
            "jumping", "sleeping", "reading", "eating"
        ]
        
        self.default_emotions = [
            "neutral", "happy", "sad", "worried", 
            "excited", "angry", "surprised", "confused"
        ]
        
        self.default_actions = [
            "waving", "hugging", "playing", "drawing",
            "brushing_teeth", "riding_bike", "swimming"
        ]
    
    async def generate_character_sprites(
        self,
        character_id: str,
        character_data: Dict[str, Any],
        generation_api: str = "dalle",
        custom_poses: Optional[List[str]] = None,
        custom_emotions: Optional[List[str]] = None,
        include_actions: bool = True
    ) -> Dict[str, Any]:
        """
        Generate complete sprite set for a character
        
        Args:
            character_id: Unique character identifier
            character_data: Character information including reference photos
            generation_api: Which API to use (dalle, stable_diffusion, local_sd)
            custom_poses: Custom pose list (uses defaults if None)
            custom_emotions: Custom emotion list (uses defaults if None)
            include_actions: Whether to generate action sprites
            
        Returns:
            Dictionary with sprite manifest and URLs
        """
        
        # Get generation adapter
        adapter = AdapterFactory.create_adapter(generation_api)
        
        # Determine poses and emotions to generate
        poses = custom_poses or self.default_poses
        emotions = custom_emotions or self.default_emotions
        actions = self.default_actions if include_actions else []
        
        # Build character description for consistency
        character_description = self._build_character_description(character_data)
        
        generated_sprites = []
        total_combinations = len(poses) * len(emotions) + len(actions)
        current_progress = 0
        
        # Generate pose + emotion combinations
        for pose in poses:
            for emotion in emotions:
                prompt = self._build_sprite_prompt(
                    character_description,
                    pose,
                    emotion
                )
                
                # Generate sprite
                sprite_url = await adapter.generate_sprite(
                    prompt,
                    reference_image=character_data.get("reference_photo"),
                    style=character_data.get("style", "consistent_character")
                )
                
                # Download and process sprite
                sprite_image = await self._download_image(sprite_url)
                
                # Remove background if needed
                if generation_api == "dalle":
                    sprite_image = await self._remove_background(sprite_image)
                
                # Save sprite
                sprite_info = await sprite_storage.save_sprite(
                    sprite_image,
                    character_id,
                    "character",
                    pose,
                    emotion
                )
                
                # Store in MPU
                sprite_data = SpriteData(
                    sprite_id=sprite_info["sprite_id"],
                    character_id=character_id,
                    sprite_type="character",
                    pose=pose,
                    emotion=emotion,
                    url=sprite_info["url"],
                    thumbnail_url=sprite_info["thumbnail_url"]
                )
                
                self.mpu.store(sprite_data)
                generated_sprites.append(sprite_info)
                
                current_progress += 1
                print(f"Progress: {current_progress}/{total_combinations}")
        
        # Generate action sprites
        for action in actions:
            prompt = self._build_action_prompt(
                character_description,
                action
            )
            
            sprite_url = await adapter.generate_sprite(
                prompt,
                reference_image=character_data.get("reference_photo")
            )
            
            sprite_image = await self._download_image(sprite_url)
            
            if generation_api == "dalle":
                sprite_image = await self._remove_background(sprite_image)
            
            sprite_info = await sprite_storage.save_sprite(
                sprite_image,
                character_id,
                "action",
                action,
                "neutral"
            )
            
            sprite_data = SpriteData(
                sprite_id=sprite_info["sprite_id"],
                character_id=character_id,
                sprite_type="action",
                pose=action,
                emotion="neutral",
                url=sprite_info["url"],
                thumbnail_url=sprite_info["thumbnail_url"]
            )
            
            self.mpu.store(sprite_data)
            generated_sprites.append(sprite_info)
            
            current_progress += 1
            print(f"Progress: {current_progress}/{total_combinations}")
        
        # Save manifest
        manifest_url = await sprite_storage.save_sprite_manifest(
            character_id,
            generated_sprites
        )
        
        return {
            "character_id": character_id,
            "sprites_generated": len(generated_sprites),
            "manifest_url": manifest_url,
            "sprites": generated_sprites,
            "generation_api": generation_api,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def process_story_scene(
        self,
        scene_text: str,
        character_mappings: Dict[str, str],
        background_style: str = "watercolor",
        generation_api: str = "dalle",
        auto_compose: bool = True
    ) -> Dict[str, Any]:
        """
        Process a single story scene
        
        Args:
            scene_text: Text of the scene
            character_mappings: Map of character names to IDs
            background_style: Style for background generation
            generation_api: Which API to use for backgrounds
            auto_compose: Whether to automatically compose the scene
            
        Returns:
            Dictionary with composed scene or components
        """
        
        # Parse scene with SSP
        self.ssp.set_character_mapping(character_mappings)
        scene_binding = self.ssp.bind(scene_text)
        
        # Get sprite requirements
        requirements = scene_binding.get_sprite_requirements()
        
        # Find best matching sprite using HASR
        character_id = requirements['character_id']
        
        if not character_id:
            raise ValueError("No character found in scene")
        
        # Get available sprites from MPU
        available_sprites = self.mpu.query(character_id=character_id)
        
        # Use HASR to find best sprite
        best_sprite = self.hasr.suggest_sprite(
            context={
                'scene': requirements['background']['setting'],
                'emotion': requirements['emotion'],
                'action': scene_binding.actions[0] if scene_binding.actions else None,
                'character_id': character_id
            },
            available_sprites=[{
                'pose': s.pose,
                'emotion': s.emotion,
                'id': s.sprite_id,
                'url': s.url
            } for s in available_sprites]
        )
        
        if not best_sprite:
            # Fallback to best match from MPU
            sprite_data = self.mpu.find_best_match(
                character_id,
                requirements['pose'],
                requirements['emotion']
            )
            
            if sprite_data:
                best_sprite = {
                    'id': sprite_data.sprite_id,
                    'url': sprite_data.url
                }
        
        # Generate background
        adapter = AdapterFactory.create_adapter(generation_api)
        background_url = await adapter.generate_background(
            requirements['background']['setting'],
            requirements['background']['time'],
            background_style
        )
        
        # Compose if requested
        if auto_compose and best_sprite:
            composed_url = await composition_service.auto_compose_story_scene(
                background_url,
                best_sprite['url'],
                additional_sprites=None,  # TODO: Add family/pet sprites
                scene_type=requirements['background']['setting']
            )
        else:
            composed_url = None
        
        # Record success for HASR learning
        if best_sprite:
            self.hasr.reinforce(
                context={
                    'scene': requirements['background']['setting'],
                    'emotion': requirements['emotion'],
                    'character_id': character_id
                },
                sprite_choice={
                    'pose': requirements['pose'],
                    'emotion': requirements['emotion'],
                    'sprite_id': best_sprite['id']
                },
                success_score=0.8  # Base score, will be updated with user feedback
            )
        
        return {
            "scene_text": scene_text,
            "background_url": background_url,
            "sprite": best_sprite,
            "composed_url": composed_url,
            "requirements": requirements,
            "auto_composed": auto_compose
        }
    
    async def process_full_story(
        self,
        story_text: str,
        character_mappings: Dict[str, str],
        background_style: str = "watercolor",
        generation_api: str = "dalle"
    ) -> Dict[str, Any]:
        """
        Process a complete story into composed scenes
        
        Args:
            story_text: Complete story text
            character_mappings: Map of character names to IDs
            background_style: Style for backgrounds
            generation_api: Which API to use
            
        Returns:
            Dictionary with all processed scenes
        """
        
        # Parse story into scenes
        self.ssp.set_character_mapping(character_mappings)
        scene_bindings = self.ssp.parse_story(story_text)
        
        processed_scenes = []
        
        # Process each scene
        for i, scene_binding in enumerate(scene_bindings):
            scene_result = await self.process_story_scene(
                scene_binding.text,
                character_mappings,
                background_style,
                generation_api,
                auto_compose=True
            )
            
            scene_result['index'] = i
            processed_scenes.append(scene_result)
        
        # Generate story ID
        story_id = f"story_{uuid.uuid4().hex[:8]}"
        
        return {
            "story_id": story_id,
            "total_scenes": len(processed_scenes),
            "scenes": processed_scenes,
            "character_mappings": character_mappings,
            "background_style": background_style,
            "created_at": datetime.utcnow().isoformat()
        }
    
    def _build_character_description(self, character_data: Dict[str, Any]) -> str:
        """Build consistent character description for prompts"""
        
        parts = []
        
        # Name and age
        if "name" in character_data:
            parts.append(character_data["name"])
        
        if "age" in character_data:
            parts.append(f"{character_data['age']}-year-old")
        
        # Gender
        if "gender" in character_data:
            parts.append(character_data["gender"])
        
        # Physical features
        if "physical_features" in character_data:
            features = character_data["physical_features"]
            if "hair" in features:
                parts.append(f"{features['hair']} hair")
            if "eyes" in features:
                parts.append(f"{features['eyes']} eyes")
            if "skin" in features:
                parts.append(f"{features['skin']} skin")
        
        # Clothing
        if "clothing" in character_data:
            parts.append(f"wearing {character_data['clothing']}")
        
        return "child" if not parts else " ".join(parts)
    
    def _build_sprite_prompt(
        self,
        character_description: str,
        pose: str,
        emotion: str
    ) -> str:
        """Build prompt for sprite generation"""
        
        pose_descriptions = {
            "standing": "standing upright, full body",
            "sitting": "sitting down, full body",
            "walking": "walking, mid-stride, full body",
            "running": "running, dynamic pose, full body",
            "jumping": "jumping in the air, full body",
            "sleeping": "lying down sleeping, full body",
            "reading": "sitting and reading a book",
            "eating": "sitting at table eating"
        }
        
        emotion_descriptions = {
            "neutral": "neutral expression",
            "happy": "smiling happily",
            "sad": "sad expression with downturned mouth",
            "worried": "worried or anxious expression",
            "excited": "excited expression with wide eyes",
            "angry": "angry or frustrated expression",
            "surprised": "surprised expression with raised eyebrows",
            "confused": "confused or puzzled expression"
        }
        
        pose_desc = pose_descriptions.get(pose, f"{pose} pose")
        emotion_desc = emotion_descriptions.get(emotion, f"{emotion} expression")
        
        return f"{character_description}, {pose_desc}, {emotion_desc}, transparent background, children's book illustration style"
    
    def _build_action_prompt(
        self,
        character_description: str,
        action: str
    ) -> str:
        """Build prompt for action sprite"""
        
        action_descriptions = {
            "waving": "waving hello with one hand",
            "hugging": "arms open for a hug",
            "playing": "playing with toys",
            "drawing": "drawing with crayons",
            "brushing_teeth": "brushing teeth",
            "riding_bike": "riding a bicycle",
            "swimming": "swimming motion"
        }
        
        action_desc = action_descriptions.get(action, f"{action} action")
        
        return f"{character_description}, {action_desc}, transparent background, children's book illustration style"
    
    async def _download_image(self, url: str) -> Image.Image:
        """Download image from URL"""
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
            image_data = io.BytesIO(response.content)
            return Image.open(image_data)
    
    async def _remove_background(self, image: Image.Image) -> Image.Image:
        """Remove background from image"""
        
        try:
            from rembg import remove
            return remove(image)
        except ImportError:
            # Fallback to simple white removal
            import numpy as np
            
            image = image.convert("RGBA")
            data = np.array(image)
            red, green, blue, alpha = data.T
            
            # Remove white/near-white pixels
            white_areas = (red > 240) & (blue > 240) & (green > 240)
            data[..., 3][white_areas.T] = 0
            
            return Image.fromarray(data)


# Global instance
sprite_generation_service = SpriteGenerationService()
