"""
MPU (Memory Processing Unit) - Adapted for Sprite Management
From LucianOS Core - Simplified for production use
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SpriteData:
    """Structured sprite data storage"""
    sprite_id: str
    character_id: str
    sprite_type: str  # 'character', 'family', 'pet', 'item'
    pose: str
    emotion: str
    url: str
    thumbnail_url: Optional[str] = None
    metadata: Dict[str, Any] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.metadata is None:
            self.metadata = {}

class MPU:
    """
    Memory Processing Unit for Sprite Storage
    
    Stores sprites in multi-dimensional space for instant retrieval.
    Adapted from LucianOS for production sprite management.
    
    Example usage:
        mpu = MPU(['character', 'pose', 'emotion', 'scene'])
        
        # Store a sprite
        sprite_data = SpriteData(
            sprite_id="sprite_001",
            character_id="sunshine_123",
            sprite_type="character",
            pose="standing",
            emotion="happy",
            url="https://r2.dev/sprites/001.png"
        )
        mpu.store(sprite_data)
        
        # Retrieve sprites
        sprites = mpu.query(character_id="sunshine_123", pose="standing")
    """
    
    def __init__(self, dimensions: List[str] = None):
        """
        Initialize MPU with specified dimensions
        
        Args:
            dimensions: List of dimension names for indexing
        """
        self.dimensions = dimensions or ['character', 'pose', 'emotion', 'type']
        self.memory = {}  # Main storage
        self.index = {dim: {} for dim in self.dimensions}  # Multi-dimensional index
        self.temporal_index = {}  # Time-based index for video frames
        self.cache = {}  # Fast access cache
        
    def store(self, sprite_data: SpriteData) -> str:
        """
        Store sprite data with multi-dimensional indexing
        
        Args:
            sprite_data: SpriteData object to store
            
        Returns:
            sprite_id of stored sprite
        """
        # Store in main memory
        self.memory[sprite_data.sprite_id] = sprite_data
        
        # Update dimensional indices
        self._update_indices(sprite_data)
        
        # Clear relevant cache entries
        self._invalidate_cache(sprite_data.character_id)
        
        return sprite_data.sprite_id
    
    def batch_store(self, sprites: List[SpriteData]) -> List[str]:
        """
        Store multiple sprites efficiently
        
        Args:
            sprites: List of SpriteData objects
            
        Returns:
            List of sprite_ids
        """
        sprite_ids = []
        for sprite in sprites:
            sprite_ids.append(self.store(sprite))
        return sprite_ids
    
    def retrieve(self, sprite_id: str) -> Optional[SpriteData]:
        """
        Retrieve a specific sprite by ID
        
        Args:
            sprite_id: Unique sprite identifier
            
        Returns:
            SpriteData object or None if not found
        """
        return self.memory.get(sprite_id)
    
    def query(self, **kwargs) -> List[SpriteData]:
        """
        Query sprites by dimensional attributes
        
        Args:
            **kwargs: Dimension-value pairs for filtering
            
        Returns:
            List of matching SpriteData objects
            
        Example:
            sprites = mpu.query(character_id="abc", pose="standing")
        """
        # Check cache first
        cache_key = self._make_cache_key(kwargs)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Find matching sprites
        results = list(self.memory.values())
        
        for key, value in kwargs.items():
            if key == 'character_id':
                results = [s for s in results if s.character_id == value]
            elif key == 'pose':
                results = [s for s in results if s.pose == value]
            elif key == 'emotion':
                results = [s for s in results if s.emotion == value]
            elif key == 'sprite_type':
                results = [s for s in results if s.sprite_type == value]
            elif key in self.dimensions:
                # Handle custom dimensions
                results = [s for s in results 
                          if s.metadata.get(key) == value]
        
        # Cache results
        self.cache[cache_key] = results
        
        return results
    
    def get_character_sprites(self, character_id: str) -> Dict[str, List[SpriteData]]:
        """
        Get all sprites for a character organized by type
        
        Args:
            character_id: Character identifier
            
        Returns:
            Dictionary organized by pose and emotion
        """
        sprites = self.query(character_id=character_id)
        
        organized = {
            'by_pose': {},
            'by_emotion': {},
            'by_type': {}
        }
        
        for sprite in sprites:
            # Organize by pose
            if sprite.pose not in organized['by_pose']:
                organized['by_pose'][sprite.pose] = []
            organized['by_pose'][sprite.pose].append(sprite)
            
            # Organize by emotion
            if sprite.emotion not in organized['by_emotion']:
                organized['by_emotion'][sprite.emotion] = []
            organized['by_emotion'][sprite.emotion].append(sprite)
            
            # Organize by type
            if sprite.sprite_type not in organized['by_type']:
                organized['by_type'][sprite.sprite_type] = []
            organized['by_type'][sprite.sprite_type].append(sprite)
        
        return organized
    
    def find_best_match(self, character_id: str, pose: str, emotion: str) -> Optional[SpriteData]:
        """
        Find the best matching sprite with fallbacks
        
        Args:
            character_id: Character identifier
            pose: Desired pose
            emotion: Desired emotion
            
        Returns:
            Best matching sprite or None
        """
        # Try exact match first
        exact_matches = self.query(
            character_id=character_id,
            pose=pose,
            emotion=emotion
        )
        if exact_matches:
            return exact_matches[0]
        
        # Try matching pose with neutral emotion
        pose_matches = self.query(
            character_id=character_id,
            pose=pose,
            emotion='neutral'
        )
        if pose_matches:
            return pose_matches[0]
        
        # Try matching emotion with standing pose
        emotion_matches = self.query(
            character_id=character_id,
            pose='standing',
            emotion=emotion
        )
        if emotion_matches:
            return emotion_matches[0]
        
        # Return any sprite for this character
        any_matches = self.query(character_id=character_id)
        if any_matches:
            return any_matches[0]
        
        return None
    
    def store_temporal(self, sprite_data: SpriteData, timestamp: float):
        """
        Store sprite with temporal indexing for video frames
        
        Args:
            sprite_data: Sprite data to store
            timestamp: Time in seconds for this sprite's appearance
        """
        sprite_id = self.store(sprite_data)
        
        if sprite_data.character_id not in self.temporal_index:
            self.temporal_index[sprite_data.character_id] = {}
        
        self.temporal_index[sprite_data.character_id][timestamp] = sprite_id
    
    def get_frame_sprites(self, character_id: str, timestamp: float) -> Optional[SpriteData]:
        """
        Get sprite for a specific video frame
        
        Args:
            character_id: Character identifier
            timestamp: Time in seconds
            
        Returns:
            Sprite for that timestamp or nearest
        """
        if character_id not in self.temporal_index:
            return None
        
        timeline = self.temporal_index[character_id]
        
        # Find exact or nearest timestamp
        if timestamp in timeline:
            return self.retrieve(timeline[timestamp])
        
        # Find nearest timestamp
        timestamps = sorted(timeline.keys())
        nearest = min(timestamps, key=lambda t: abs(t - timestamp))
        
        return self.retrieve(timeline[nearest])
    
    def export_manifest(self, character_id: str) -> Dict:
        """
        Export sprite manifest for a character
        
        Args:
            character_id: Character identifier
            
        Returns:
            Complete manifest dictionary
        """
        sprites = self.query(character_id=character_id)
        
        manifest = {
            'character_id': character_id,
            'sprite_count': len(sprites),
            'created_at': datetime.utcnow().isoformat(),
            'sprites': [asdict(s) for s in sprites],
            'dimensions': self.dimensions,
            'index': {
                'poses': list(set(s.pose for s in sprites)),
                'emotions': list(set(s.emotion for s in sprites)),
                'types': list(set(s.sprite_type for s in sprites))
            }
        }
        
        return manifest
    
    def import_manifest(self, manifest: Dict):
        """
        Import sprites from a manifest
        
        Args:
            manifest: Manifest dictionary from export_manifest
        """
        for sprite_dict in manifest['sprites']:
            sprite_data = SpriteData(**sprite_dict)
            self.store(sprite_data)
    
    def _update_indices(self, sprite_data: SpriteData):
        """Update multi-dimensional indices"""
        # Index by character
        if 'character' in self.dimensions:
            if sprite_data.character_id not in self.index['character']:
                self.index['character'][sprite_data.character_id] = []
            self.index['character'][sprite_data.character_id].append(sprite_data.sprite_id)
        
        # Index by pose
        if 'pose' in self.dimensions:
            if sprite_data.pose not in self.index['pose']:
                self.index['pose'][sprite_data.pose] = []
            self.index['pose'][sprite_data.pose].append(sprite_data.sprite_id)
        
        # Index by emotion
        if 'emotion' in self.dimensions:
            if sprite_data.emotion not in self.index['emotion']:
                self.index['emotion'][sprite_data.emotion] = []
            self.index['emotion'][sprite_data.emotion].append(sprite_data.sprite_id)
    
    def _invalidate_cache(self, character_id: str):
        """Clear cache entries for a character"""
        keys_to_remove = [
            key for key in self.cache 
            if character_id in key
        ]
        for key in keys_to_remove:
            del self.cache[key]
    
    def _make_cache_key(self, params: Dict) -> str:
        """Create cache key from query parameters"""
        return json.dumps(params, sort_keys=True)
    
    def get_statistics(self) -> Dict:
        """Get storage statistics"""
        return {
            'total_sprites': len(self.memory),
            'characters': len(set(s.character_id for s in self.memory.values())),
            'cache_size': len(self.cache),
            'dimensions': self.dimensions,
            'poses': len(self.index.get('pose', {})),
            'emotions': len(self.index.get('emotion', {}))
        }


# Example usage for testing
if __name__ == "__main__":
    # Initialize MPU
    mpu = MPU(['character', 'pose', 'emotion', 'scene'])
    
    # Create sample sprite
    sprite = SpriteData(
        sprite_id="test_001",
        character_id="sunshine_123",
        sprite_type="character",
        pose="standing",
        emotion="happy",
        url="https://example.com/sprite.png"
    )
    
    # Store sprite
    mpu.store(sprite)
    
    # Query sprites
    results = mpu.query(character_id="sunshine_123")
    print(f"Found {len(results)} sprites")
    
    # Export manifest
    manifest = mpu.export_manifest("sunshine_123")
    print(f"Manifest: {manifest}")
