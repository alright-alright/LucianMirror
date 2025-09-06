"""
Sprite Composition Service
Handles combining sprites with backgrounds and scene composition
"""

from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
import io
import base64
import httpx
from dataclasses import dataclass
import os

@dataclass
class SpritePosition:
    """Position and transform data for a sprite"""
    x: float  # 0-1 normalized position
    y: float  # 0-1 normalized position
    scale: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0
    flip_horizontal: bool = False
    
    def to_pixels(self, canvas_width: int, canvas_height: int) -> Tuple[int, int]:
        """Convert normalized position to pixel coordinates"""
        return (int(self.x * canvas_width), int(self.y * canvas_height))


class CompositionService:
    """Service for composing sprites onto backgrounds"""
    
    def __init__(self):
        self.default_canvas_size = (1024, 1024)
        
    async def compose_scene(
        self,
        background_url: str,
        sprites: List[Dict[str, Any]],
        output_format: str = "png",
        canvas_size: Optional[Tuple[int, int]] = None
    ) -> str:
        """
        Compose sprites onto a background
        
        Args:
            background_url: URL of the background image
            sprites: List of sprite dictionaries with url and position
            output_format: Output format (png, jpg, webp)
            canvas_size: Optional canvas size, otherwise uses background size
            
        Returns:
            URL of the composed image
        """
        
        # Load background
        background = await self._load_image_from_url(background_url)
        
        if canvas_size:
            background = background.resize(canvas_size, Image.Resampling.LANCZOS)
        
        canvas = background.convert("RGBA")
        
        # Compose each sprite
        for sprite_data in sprites:
            sprite_image = await self._load_image_from_url(sprite_data["url"])
            position = SpritePosition(**sprite_data.get("position", {}))
            
            # Apply transformations
            sprite_image = self._transform_sprite(
                sprite_image,
                position,
                canvas.size
            )
            
            # Composite onto canvas
            canvas = self._composite_sprite(
                canvas,
                sprite_image,
                position
            )
        
        # Save and return URL
        return await self._save_composed_image(canvas, output_format)
    
    async def auto_compose_story_scene(
        self,
        background_url: str,
        character_sprite_url: str,
        additional_sprites: List[Dict[str, Any]] = None,
        scene_type: str = "standard"
    ) -> str:
        """
        Automatically compose a story scene with smart positioning
        
        Args:
            background_url: Background image URL
            character_sprite_url: Main character sprite URL
            additional_sprites: Other sprites (family, pets, objects)
            scene_type: Type of scene for positioning hints
            
        Returns:
            URL of composed scene
        """
        
        # Determine character position based on scene type
        character_position = self._get_character_position(scene_type)
        
        sprites = [{
            "url": character_sprite_url,
            "position": character_position.__dict__
        }]
        
        # Add additional sprites with smart positioning
        if additional_sprites:
            for i, sprite in enumerate(additional_sprites):
                position = self._get_secondary_position(scene_type, i)
                sprites.append({
                    "url": sprite["url"],
                    "position": position.__dict__
                })
        
        return await self.compose_scene(background_url, sprites)
    
    def _get_character_position(self, scene_type: str) -> SpritePosition:
        """Get optimal character position for scene type"""
        
        positions = {
            "bedroom": SpritePosition(0.5, 0.7, 0.8),
            "outdoor": SpritePosition(0.4, 0.65, 0.9),
            "sitting": SpritePosition(0.5, 0.75, 0.85),
            "walking": SpritePosition(0.3, 0.7, 0.9),
            "group": SpritePosition(0.35, 0.7, 0.8),
            "standard": SpritePosition(0.5, 0.7, 0.85)
        }
        
        return positions.get(scene_type, positions["standard"])
    
    def _get_secondary_position(self, scene_type: str, index: int) -> SpritePosition:
        """Get position for secondary sprites"""
        
        # Offset positions for multiple sprites
        base_positions = [
            SpritePosition(0.65, 0.7, 0.8),  # Right side
            SpritePosition(0.25, 0.7, 0.8),  # Left side
            SpritePosition(0.5, 0.6, 0.7),   # Behind/above
        ]
        
        return base_positions[index % len(base_positions)]
    
    def _transform_sprite(
        self,
        sprite: Image.Image,
        position: SpritePosition,
        canvas_size: Tuple[int, int]
    ) -> Image.Image:
        """Apply transformations to sprite"""
        
        # Calculate target size
        base_height = int(canvas_size[1] * 0.4)  # Sprites take up ~40% of height
        target_height = int(base_height * position.scale)
        aspect_ratio = sprite.width / sprite.height
        target_width = int(target_height * aspect_ratio)
        
        # Resize
        sprite = sprite.resize(
            (target_width, target_height),
            Image.Resampling.LANCZOS
        )
        
        # Rotate if needed
        if position.rotation != 0:
            sprite = sprite.rotate(
                position.rotation,
                expand=True,
                fillcolor=(0, 0, 0, 0)
            )
        
        # Flip if needed
        if position.flip_horizontal:
            sprite = sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        
        # Adjust opacity
        if position.opacity < 1.0:
            alpha = sprite.split()[-1]
            alpha = alpha.point(lambda p: p * position.opacity)
            sprite.putalpha(alpha)
        
        return sprite
    
    def _composite_sprite(
        self,
        canvas: Image.Image,
        sprite: Image.Image,
        position: SpritePosition
    ) -> Image.Image:
        """Composite sprite onto canvas"""
        
        # Get pixel position
        x, y = position.to_pixels(canvas.width, canvas.height)
        
        # Center the sprite on the position
        x -= sprite.width // 2
        y -= sprite.height // 2
        
        # Create a copy of canvas
        result = canvas.copy()
        
        # Paste sprite with alpha channel
        result.paste(sprite, (x, y), sprite)
        
        return result
    
    async def _load_image_from_url(self, url: str) -> Image.Image:
        """Load image from URL"""
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
            image_data = io.BytesIO(response.content)
            return Image.open(image_data)
    
    async def _save_composed_image(
        self,
        image: Image.Image,
        format: str = "png"
    ) -> str:
        """Save composed image and return URL"""
        
        # Convert to appropriate format
        if format == "jpg":
            # Convert RGBA to RGB for JPEG
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[3] if len(image.split()) > 3 else None)
            image = rgb_image
        
        # Save to bytes
        output = io.BytesIO()
        image.save(output, format=format.upper(), quality=95)
        output.seek(0)
        
        # TODO: Upload to actual storage (S3/R2)
        # For now, return base64 data URL
        base64_data = base64.b64encode(output.getvalue()).decode()
        return f"data:image/{format};base64,{base64_data}"
    
    async def create_sprite_sheet(
        self,
        sprites: List[str],
        columns: int = 4,
        sprite_size: Tuple[int, int] = (256, 256),
        padding: int = 10
    ) -> str:
        """
        Create a sprite sheet from individual sprites
        
        Args:
            sprites: List of sprite URLs
            columns: Number of columns in sheet
            sprite_size: Size of each sprite
            padding: Padding between sprites
            
        Returns:
            URL of sprite sheet
        """
        
        rows = (len(sprites) + columns - 1) // columns
        
        sheet_width = columns * (sprite_size[0] + padding) + padding
        sheet_height = rows * (sprite_size[1] + padding) + padding
        
        sheet = Image.new("RGBA", (sheet_width, sheet_height), (0, 0, 0, 0))
        
        for i, sprite_url in enumerate(sprites):
            sprite = await self._load_image_from_url(sprite_url)
            sprite = sprite.resize(sprite_size, Image.Resampling.LANCZOS)
            
            row = i // columns
            col = i % columns
            
            x = col * (sprite_size[0] + padding) + padding
            y = row * (sprite_size[1] + padding) + padding
            
            sheet.paste(sprite, (x, y), sprite)
        
        return await self._save_composed_image(sheet, "png")
    
    async def remove_background(self, image_url: str) -> str:
        """
        Remove background from an image
        
        Args:
            image_url: URL of image to process
            
        Returns:
            URL of image with transparent background
        """
        
        image = await self._load_image_from_url(image_url)
        
        try:
            # Try using rembg if available
            from rembg import remove
            
            output = remove(image)
            return await self._save_composed_image(output, "png")
            
        except ImportError:
            # Fallback to simple color-based removal
            image = image.convert("RGBA")
            
            # Assume white or near-white background
            data = np.array(image)
            red, green, blue, alpha = data.T
            
            # Find white/near-white pixels
            white_areas = (red > 240) & (blue > 240) & (green > 240)
            
            data[..., 3][white_areas.T] = 0  # Make white transparent
            
            result = Image.fromarray(data)
            return await self._save_composed_image(result, "png")


class VideoCompositionService:
    """Service for creating animated videos from sprites"""
    
    def __init__(self):
        self.fps = 30
        self.default_duration = 30  # seconds
        
    async def create_sprite_animation(
        self,
        sprites: List[Dict[str, Any]],
        background_url: str,
        duration: float = 30,
        transitions: List[str] = None
    ) -> str:
        """
        Create an animated video from sprites
        
        Args:
            sprites: List of sprites with animation data
            background_url: Background image URL
            duration: Video duration in seconds
            transitions: List of transition effects
            
        Returns:
            URL of generated video
        """
        
        # TODO: Implement actual video generation
        # This would use libraries like moviepy or opencv
        
        frames = []
        total_frames = int(duration * self.fps)
        
        for frame_num in range(total_frames):
            # Calculate positions for this frame
            frame_sprites = self._calculate_frame_positions(
                sprites,
                frame_num,
                total_frames
            )
            
            # Compose frame
            # frame = await composition_service.compose_scene(
            #     background_url,
            #     frame_sprites
            # )
            # frames.append(frame)
        
        # Create video from frames
        # video_url = self._create_video(frames)
        
        return "https://storage.example.com/generated_video.mp4"
    
    def _calculate_frame_positions(
        self,
        sprites: List[Dict[str, Any]],
        frame_num: int,
        total_frames: int
    ) -> List[Dict[str, Any]]:
        """Calculate sprite positions for a specific frame"""
        
        progress = frame_num / total_frames
        frame_sprites = []
        
        for sprite in sprites:
            # Interpolate position based on animation keyframes
            if "animation" in sprite:
                position = self._interpolate_position(
                    sprite["animation"],
                    progress
                )
            else:
                position = sprite.get("position", {})
            
            frame_sprites.append({
                "url": sprite["url"],
                "position": position
            })
        
        return frame_sprites
    
    def _interpolate_position(
        self,
        animation: Dict[str, Any],
        progress: float
    ) -> Dict[str, float]:
        """Interpolate position between keyframes"""
        
        keyframes = animation.get("keyframes", [])
        
        if not keyframes:
            return {"x": 0.5, "y": 0.7}
        
        # Find surrounding keyframes
        for i in range(len(keyframes) - 1):
            if keyframes[i]["time"] <= progress <= keyframes[i + 1]["time"]:
                # Linear interpolation
                t = (progress - keyframes[i]["time"]) / (keyframes[i + 1]["time"] - keyframes[i]["time"])
                
                return {
                    "x": keyframes[i]["x"] + t * (keyframes[i + 1]["x"] - keyframes[i]["x"]),
                    "y": keyframes[i]["y"] + t * (keyframes[i + 1]["y"] - keyframes[i]["y"]),
                    "scale": keyframes[i].get("scale", 1) + t * (keyframes[i + 1].get("scale", 1) - keyframes[i].get("scale", 1))
                }
        
        # Return last keyframe if beyond
        return keyframes[-1]


# Global instances
composition_service = CompositionService()
video_composition_service = VideoCompositionService()
