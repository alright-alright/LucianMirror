"""
Game Asset Generation Service
Creates sprite sheets and game-ready assets for RPG games
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from PIL import Image, ImageDraw
import json
import math
from datetime import datetime


class GameAssetService:
    """
    Generates RPG game assets from sprite libraries
    Creates Unity/Godot/Phaser compatible sprite sheets
    """
    
    def __init__(self):
        self.sprite_sheet_configs = {
            'unity': {
                'format': 'png',
                'grid_size': (8, 8),
                'sprite_size': (128, 128),
                'metadata': 'json'
            },
            'godot': {
                'format': 'png',
                'grid_size': (8, 8),
                'sprite_size': (128, 128),
                'metadata': 'tres'
            },
            'phaser': {
                'format': 'png',
                'grid_size': (8, 8),
                'sprite_size': (128, 128),
                'metadata': 'json'
            },
            'rpg_maker': {
                'format': 'png',
                'grid_size': (3, 4),  # Standard RPG Maker layout
                'sprite_size': (48, 48),
                'metadata': None
            }
        }
    
    async def create_hero_package(
        self,
        character_id: str,
        character_data: Dict[str, Any],
        game_engine: str = 'unity',
        include_equipment: bool = True
    ) -> Dict[str, Any]:
        """
        Create a complete hero package for RPG games
        
        Args:
            character_id: Unique character identifier
            character_data: Character details (name, appearance, etc.)
            game_engine: Target game engine (unity, godot, phaser, rpg_maker)
            include_equipment: Generate equipment variants
            
        Returns:
            Package with sprite sheets, animations, and metadata
        """
        
        print(f"🎮 Creating RPG hero package for {character_data.get('name')}")
        
        # Generate base character sprites with RPG-specific poses
        rpg_poses = [
            'idle_down', 'idle_up', 'idle_left', 'idle_right',
            'walk_down', 'walk_up', 'walk_left', 'walk_right',
            'attack_down', 'attack_up', 'attack_left', 'attack_right',
            'cast_spell', 'defend', 'hurt', 'victory', 'defeat',
            'item_use', 'interact', 'sleep'
        ]
        
        # Import sprite generation service
        from services.sprite_generation_service import sprite_generation_service
        
        # Generate all RPG poses
        sprites = {}
        for pose in rpg_poses:
            sprite_result = await sprite_generation_service.generate_single_sprite(
                character_id=character_id,
                character_data=character_data,
                pose=pose,
                emotion='determined',  # Default RPG emotion
                generation_api='dalle'
            )
            sprites[pose] = sprite_result
        
        # Create sprite sheets
        sprite_sheets = await self._create_sprite_sheets(
            sprites,
            game_engine,
            character_id
        )
        
        # Generate equipment overlays if requested
        equipment_sheets = {}
        if include_equipment:
            equipment_sheets = await self._generate_equipment_overlays(
                character_id,
                character_data,
                game_engine
            )
        
        # Create animation metadata
        animations = self._create_animation_metadata(
            sprites,
            game_engine
        )
        
        # Create character stats template
        character_stats = self._create_character_stats(character_data)
        
        return {
            'character_id': character_id,
            'character_name': character_data.get('name'),
            'sprite_sheets': sprite_sheets,
            'equipment_sheets': equipment_sheets,
            'animations': animations,
            'character_stats': character_stats,
            'game_engine': game_engine,
            'created_at': datetime.utcnow().isoformat()
        }
    
    async def _create_sprite_sheets(
        self,
        sprites: Dict[str, Any],
        game_engine: str,
        character_id: str
    ) -> Dict[str, str]:
        """
        Organize sprites into game engine-specific sprite sheets
        """
        
        config = self.sprite_sheet_configs.get(game_engine, self.sprite_sheet_configs['unity'])
        grid_width, grid_height = config['grid_size']
        sprite_width, sprite_height = config['sprite_size']
        
        # Create main sprite sheet
        sheet_width = sprite_width * grid_width
        sheet_height = sprite_height * grid_height
        sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
        
        # Organize sprites by action type
        movement_sprites = {}
        combat_sprites = {}
        special_sprites = {}
        
        for pose_name, sprite_data in sprites.items():
            if any(x in pose_name for x in ['idle', 'walk']):
                movement_sprites[pose_name] = sprite_data
            elif any(x in pose_name for x in ['attack', 'defend', 'hurt']):
                combat_sprites[pose_name] = sprite_data
            else:
                special_sprites[pose_name] = sprite_data
        
        # Place sprites on sheet
        sprite_metadata = []
        current_row = 0
        current_col = 0
        
        # Movement sprites first (for RPG Maker compatibility)
        for pose_name, sprite_data in movement_sprites.items():
            if current_col >= grid_width:
                current_col = 0
                current_row += 1
            
            x = current_col * sprite_width
            y = current_row * sprite_height
            
            # Load and resize sprite
            sprite_img = await self._load_sprite_image(sprite_data['url'])
            sprite_img = sprite_img.resize((sprite_width, sprite_height), Image.Resampling.LANCZOS)
            
            # Paste onto sheet
            sprite_sheet.paste(sprite_img, (x, y), sprite_img)
            
            # Add to metadata
            sprite_metadata.append({
                'name': pose_name,
                'x': x,
                'y': y,
                'width': sprite_width,
                'height': sprite_height,
                'row': current_row,
                'col': current_col
            })
            
            current_col += 1
        
        # Save sprite sheet
        sheet_url = await self._save_sprite_sheet(
            sprite_sheet,
            f"{character_id}_sprites_{game_engine}.png"
        )
        
        # Save metadata
        metadata_url = await self._save_metadata(
            sprite_metadata,
            game_engine,
            character_id
        )
        
        return {
            'sprite_sheet': sheet_url,
            'metadata': metadata_url,
            'grid_size': config['grid_size'],
            'sprite_size': config['sprite_size']
        }
    
    async def _generate_equipment_overlays(
        self,
        character_id: str,
        character_data: Dict,
        game_engine: str
    ) -> Dict[str, Any]:
        """
        Generate equipment overlay sprites (weapons, armor, accessories)
        """
        
        equipment_types = {
            'weapons': ['sword', 'staff', 'bow', 'dagger', 'shield'],
            'armor': ['leather', 'chainmail', 'plate', 'robe'],
            'accessories': ['helmet', 'cape', 'boots', 'gloves']
        }
        
        equipment_sheets = {}
        
        for category, items in equipment_types.items():
            # Create equipment sprite sheet
            category_sprites = {}
            
            for item in items:
                # Generate equipment sprite
                # This would use the generation adapter to create equipment
                sprite_url = f"https://storage.example.com/equipment/{character_id}_{item}.png"
                category_sprites[item] = sprite_url
            
            equipment_sheets[category] = category_sprites
        
        return equipment_sheets
    
    def _create_animation_metadata(
        self,
        sprites: Dict[str, Any],
        game_engine: str
    ) -> Dict[str, Any]:
        """
        Create animation sequences and timing data
        """
        
        animations = {
            'idle': {
                'frames': ['idle_down', 'idle_up', 'idle_left', 'idle_right'],
                'duration': 1.0,
                'loop': True
            },
            'walk': {
                'frames': ['walk_down', 'walk_up', 'walk_left', 'walk_right'],
                'duration': 0.5,
                'loop': True,
                'frame_rate': 8
            },
            'attack': {
                'frames': ['attack_down', 'attack_up', 'attack_left', 'attack_right'],
                'duration': 0.3,
                'loop': False,
                'frame_rate': 12
            },
            'cast_spell': {
                'frames': ['cast_spell'],
                'duration': 0.8,
                'loop': False,
                'particles': True
            },
            'hurt': {
                'frames': ['hurt'],
                'duration': 0.2,
                'loop': False,
                'flash': True
            },
            'victory': {
                'frames': ['victory'],
                'duration': 1.5,
                'loop': False,
                'celebration_effect': True
            }
        }
        
        # Add game engine specific formatting
        if game_engine == 'unity':
            # Unity AnimationClip format
            for anim_name, anim_data in animations.items():
                anim_data['unity_controller'] = f"{anim_name}_controller"
                anim_data['transition_time'] = 0.1
        
        elif game_engine == 'godot':
            # Godot AnimationPlayer format
            for anim_name, anim_data in animations.items():
                anim_data['godot_resource'] = f"res://animations/{anim_name}.tres"
        
        return animations
    
    def _create_character_stats(self, character_data: Dict) -> Dict[str, Any]:
        """
        Create RPG character stats based on personality
        """
        
        # Base stats
        stats = {
            'level': 1,
            'hp': 100,
            'mp': 50,
            'strength': 10,
            'defense': 10,
            'magic': 10,
            'speed': 10,
            'luck': 10
        }
        
        # Adjust based on character traits
        personality = character_data.get('personality_traits', [])
        
        if 'brave' in personality:
            stats['strength'] += 3
            stats['hp'] += 20
        
        if 'intelligent' in personality:
            stats['magic'] += 3
            stats['mp'] += 20
        
        if 'agile' in personality:
            stats['speed'] += 3
            stats['luck'] += 2
        
        if 'caring' in personality:
            stats['defense'] += 2
            stats['mp'] += 10
        
        # Add character class suggestions
        stats['suggested_classes'] = self._suggest_classes(stats)
        
        # Add abilities
        stats['starting_abilities'] = [
            {'name': 'Basic Attack', 'type': 'physical', 'power': 10},
            {'name': 'Defend', 'type': 'defensive', 'power': 5}
        ]
        
        return stats
    
    def _suggest_classes(self, stats: Dict) -> List[str]:
        """
        Suggest RPG classes based on stats
        """
        
        classes = []
        
        if stats['strength'] > stats['magic']:
            classes.append('Warrior')
            if stats['speed'] > 12:
                classes.append('Rogue')
        
        if stats['magic'] > stats['strength']:
            classes.append('Mage')
            if stats['mp'] > 60:
                classes.append('Healer')
        
        if stats['defense'] > 11:
            classes.append('Paladin')
        
        if not classes:
            classes.append('Adventurer')  # Default balanced class
        
        return classes
    
    async def create_npc_pack(
        self,
        npcs: List[Dict[str, Any]],
        game_engine: str = 'unity'
    ) -> Dict[str, Any]:
        """
        Create a pack of NPC sprites for populating game worlds
        """
        
        npc_sheets = []
        
        for npc in npcs:
            # Simplified sprite set for NPCs
            npc_poses = ['idle_down', 'idle_up', 'walk_down', 'walk_up']
            
            npc_sprites = {}
            for pose in npc_poses:
                # Generate NPC sprite
                sprite_url = f"https://storage.example.com/npcs/{npc['id']}_{pose}.png"
                npc_sprites[pose] = sprite_url
            
            # Create mini sprite sheet for NPC
            npc_sheet = await self._create_npc_sheet(
                npc_sprites,
                npc['id'],
                game_engine
            )
            
            npc_sheets.append({
                'npc_id': npc['id'],
                'npc_name': npc.get('name'),
                'npc_type': npc.get('type', 'villager'),
                'sprite_sheet': npc_sheet,
                'dialogue': npc.get('dialogue', [])
            })
        
        return {
            'npc_count': len(npcs),
            'npc_sheets': npc_sheets,
            'game_engine': game_engine
        }
    
    async def export_for_game_engine(
        self,
        character_id: str,
        game_engine: str,
        export_format: str = 'package'
    ) -> str:
        """
        Export sprites in game engine specific format
        """
        
        if game_engine == 'unity':
            return await self._export_unity_package(character_id)
        elif game_engine == 'godot':
            return await self._export_godot_resource(character_id)
        elif game_engine == 'phaser':
            return await self._export_phaser_atlas(character_id)
        elif game_engine == 'rpg_maker':
            return await self._export_rpg_maker_charset(character_id)
        else:
            raise ValueError(f"Unsupported game engine: {game_engine}")
    
    async def _load_sprite_image(self, url: str) -> Image.Image:
        """Load sprite image from URL"""
        import httpx
        import io
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return Image.open(io.BytesIO(response.content)).convert('RGBA')
    
    async def _save_sprite_sheet(self, image: Image.Image, filename: str) -> str:
        """Save sprite sheet and return URL"""
        # This would upload to storage
        return f"https://storage.example.com/sprite_sheets/{filename}"
    
    async def _save_metadata(self, metadata: List[Dict], game_engine: str, character_id: str) -> str:
        """Save metadata in appropriate format"""
        
        if game_engine in ['unity', 'phaser']:
            # Save as JSON
            filename = f"{character_id}_metadata.json"
            # Upload JSON to storage
            return f"https://storage.example.com/metadata/{filename}"
        
        elif game_engine == 'godot':
            # Save as Godot resource file
            filename = f"{character_id}_metadata.tres"
            # Convert to Godot format and upload
            return f"https://storage.example.com/metadata/{filename}"
        
        return None
    
    async def _create_npc_sheet(self, sprites: Dict, npc_id: str, game_engine: str) -> str:
        """Create simplified NPC sprite sheet"""
        # Implementation for NPC sheet creation
        return f"https://storage.example.com/npcs/{npc_id}_sheet.png"
    
    async def _export_unity_package(self, character_id: str) -> str:
        """Export as Unity package"""
        # Create .unitypackage file
        return f"https://storage.example.com/exports/{character_id}.unitypackage"
    
    async def _export_godot_resource(self, character_id: str) -> str:
        """Export as Godot resource"""
        # Create .pck file
        return f"https://storage.example.com/exports/{character_id}.pck"
    
    async def _export_phaser_atlas(self, character_id: str) -> str:
        """Export as Phaser atlas"""
        # Create atlas JSON
        return f"https://storage.example.com/exports/{character_id}_atlas.json"
    
    async def _export_rpg_maker_charset(self, character_id: str) -> str:
        """Export as RPG Maker charset"""
        # Create RPG Maker compatible charset
        return f"https://storage.example.com/exports/{character_id}_charset.png"


# Global instance
game_asset_service = GameAssetService()