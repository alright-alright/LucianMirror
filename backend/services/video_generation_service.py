"""
Video Generation Service for TikTok/Shorts animations
Uses sprite libraries to create smooth animations
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from PIL import Image, ImageDraw
import io
import math
from datetime import datetime

# For video generation
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("⚠️ OpenCV not installed - video features limited")


class VideoGenerationService:
    """
    Creates animated videos from sprite libraries
    Perfect for TikTok, YouTube Shorts, Instagram Reels, and episodic content
    Supports sitcoms, social stories, and serialized narratives
    """
    
    def __init__(self):
        self.default_fps = 30
        self.default_duration = 15  # TikTok length
        self.episode_cache = {}  # Cache character consistency across episodes
        self.genre_styles = {
            'sitcom': {'lighting': 'bright', 'camera': 'static', 'transitions': 'quick_cut'},
            'sci_fi': {'lighting': 'neon', 'camera': 'dynamic', 'transitions': 'glitch'},
            'romance': {'lighting': 'soft', 'camera': 'smooth', 'transitions': 'fade'},
            'old_style': {'lighting': 'sepia', 'camera': 'vintage', 'transitions': 'iris'},
            'social_story': {'lighting': 'warm', 'camera': 'steady', 'transitions': 'dissolve'}
        }
        
    async def create_story_animation(
        self,
        story_scenes: List[Dict[str, Any]],
        sprites: Dict[str, Any],
        settings: Dict[str, Any]
    ) -> str:
        """
        Create an animated video from story scenes
        
        Args:
            story_scenes: List of scenes with text and composed images
            sprites: Dictionary of sprite URLs by character and pose
            settings: Animation settings (duration, transitions, genre, etc.)
            
        Returns:
            URL to the generated video
        """
        
        video_type = settings.get('video_type', 'tiktok')
        genre = settings.get('genre', 'sitcom')
        
        if video_type == 'tiktok':
            return await self._create_tiktok_animation(story_scenes, sprites, settings)
        elif video_type == 'youtube_short':
            return await self._create_youtube_short(story_scenes, sprites, settings)
        elif video_type == 'instagram_reel':
            return await self._create_instagram_reel(story_scenes, sprites, settings)
        else:
            return await self._create_standard_animation(story_scenes, sprites, settings)
    
    async def create_episode(
        self,
        episode_data: Dict[str, Any],
        series_id: str,
        episode_number: int
    ) -> str:
        """
        Create an episode for a series (sitcom, drama, etc.)
        Maintains character consistency across episodes
        """
        
        # Load series character models from cache
        if series_id not in self.episode_cache:
            self.episode_cache[series_id] = await self._initialize_series(episode_data)
        
        series_data = self.episode_cache[series_id]
        
        # Generate episode with consistent characters
        scenes = await self._generate_episode_scenes(
            episode_data,
            series_data,
            episode_number
        )
        
        # Add intro/outro if series
        if episode_number > 1:
            scenes = self._add_series_branding(scenes, series_data)
        
        return await self.create_story_animation(
            scenes,
            series_data['sprites'],
            episode_data['settings']
        )
    
    async def _initialize_series(self, episode_data: Dict) -> Dict:
        """
        Initialize a new series with consistent characters
        """
        
        characters = episode_data.get('characters', [])
        series_sprites = {}
        
        # Generate base sprites for all main characters
        for character in characters:
            character_id = character['id']
            
            # Multiple outfits/looks for variety
            outfits = ['casual', 'formal', 'pajamas'] if character.get('is_main') else ['casual']
            
            for outfit in outfits:
                sprite_key = f"{character_id}_{outfit}"
                # This would generate sprites with consistent face but different outfits
                series_sprites[sprite_key] = await self._generate_character_variants(
                    character,
                    outfit
                )
        
        return {
            'sprites': series_sprites,
            'characters': characters,
            'settings': episode_data.get('settings', {})
        }
    
    async def _generate_episode_scenes(
        self,
        episode_data: Dict,
        series_data: Dict,
        episode_number: int
    ) -> List[Dict]:
        """
        Generate scenes for an episode with proper pacing
        """
        
        scenes = []
        genre = episode_data.get('genre', 'sitcom')
        
        # Opening scene
        scenes.append(self._create_opening_scene(episode_data, genre))
        
        # Main story beats
        for beat in episode_data.get('story_beats', []):
            scene = await self._create_story_beat_scene(
                beat,
                series_data,
                genre
            )
            scenes.append(scene)
        
        # Resolution/cliffhanger
        if episode_data.get('has_cliffhanger'):
            scenes.append(self._create_cliffhanger_scene(episode_data, series_data))
        else:
            scenes.append(self._create_resolution_scene(episode_data, series_data))
        
        return scenes
    
    async def _create_tiktok_animation(
        self,
        scenes: List[Dict],
        sprites: Dict,
        settings: Dict
    ) -> str:
        """
        Create a vertical TikTok-optimized animation (9:16 aspect ratio)
        """
        
        width = 1080
        height = 1920
        fps = 30
        duration_per_scene = 3  # 3 seconds per scene for 15 second video (5 scenes)
        
        frames = []
        
        for scene_idx, scene in enumerate(scenes[:5]):  # Limit to 5 scenes for 15 seconds
            # Create animated frames for this scene
            scene_frames = await self._animate_scene(
                scene=scene,
                sprites=sprites,
                width=width,
                height=height,
                duration=duration_per_scene,
                fps=fps,
                animation_type='tiktok'
            )
            frames.extend(scene_frames)
        
        # Add transitions between scenes
        frames_with_transitions = self._add_transitions(frames, fps)
        
        # Generate video file
        video_url = await self._compile_video(
            frames_with_transitions,
            width,
            height,
            fps,
            format='mp4'
        )
        
        return video_url
    
    async def _animate_scene(
        self,
        scene: Dict,
        sprites: Dict,
        width: int,
        height: int,
        duration: float,
        fps: int,
        animation_type: str
    ) -> List[Image.Image]:
        """
        Create animated frames for a single scene
        """
        
        frames = []
        total_frames = int(duration * fps)
        
        # Load background and sprites
        background = await self._load_image(scene.get('background_url'))
        character_sprite = await self._load_image(scene.get('character_sprite_url'))
        
        # Resize for video dimensions
        background = background.resize((width, height), Image.Resampling.LANCZOS)
        
        # Calculate sprite size (40% of height for TikTok)
        sprite_height = int(height * 0.4)
        sprite_width = int(character_sprite.width * (sprite_height / character_sprite.height))
        character_sprite = character_sprite.resize((sprite_width, sprite_height), Image.Resampling.LANCZOS)
        
        # Animation patterns based on type
        if animation_type == 'tiktok':
            # Fun, energetic animations for TikTok
            animations = self._get_tiktok_animations(scene.get('emotion', 'happy'))
        else:
            # Standard animations
            animations = self._get_standard_animations(scene.get('emotion', 'neutral'))
        
        for frame_idx in range(total_frames):
            # Create frame
            frame = background.copy()
            
            # Calculate sprite position with animation
            t = frame_idx / total_frames  # Progress 0-1
            
            # Apply animation
            x, y, scale, rotation = animations['movement'](t, width, height)
            
            # Transform sprite
            animated_sprite = self._transform_sprite(
                character_sprite,
                scale=scale,
                rotation=rotation
            )
            
            # Composite sprite onto background
            frame.paste(animated_sprite, (int(x), int(y)), animated_sprite)
            
            # Add text overlay if specified
            if scene.get('show_text', True):
                frame = self._add_text_overlay(
                    frame,
                    scene.get('description', ''),
                    frame_idx,
                    total_frames
                )
            
            frames.append(frame)
        
        return frames
    
    def _get_genre_effects(self, genre: str) -> Dict:
        """
        Get visual effects based on genre
        """
        
        effects = {
            'sitcom': {
                'filter': None,
                'lighting_adjustment': 1.2,  # Brighter
                'saturation': 1.1,
                'camera_shake': 0
            },
            'sci_fi': {
                'filter': 'cyberpunk',
                'lighting_adjustment': 0.8,
                'saturation': 1.3,
                'camera_shake': 0.02,
                'overlay': 'holographic_scanlines'
            },
            'romance': {
                'filter': 'soft_glow',
                'lighting_adjustment': 1.1,
                'saturation': 0.9,
                'camera_shake': 0,
                'overlay': 'light_leaks'
            },
            'old_style': {
                'filter': 'vintage_film',
                'lighting_adjustment': 0.9,
                'saturation': 0.6,
                'camera_shake': 0.01,
                'overlay': 'film_grain'
            },
            'social_story': {
                'filter': None,
                'lighting_adjustment': 1.0,
                'saturation': 1.0,
                'camera_shake': 0
            }
        }
        
        return effects.get(genre, effects['sitcom'])
    
    def _get_tiktok_animations(self, emotion: str) -> Dict:
        """
        Get TikTok-style animations based on emotion
        """
        
        if emotion == 'happy':
            return {
                'movement': lambda t, w, h: (
                    w/2 - 150 + math.sin(t * math.pi * 4) * 50,  # Bounce horizontally
                    h * 0.6 + math.abs(math.sin(t * math.pi * 8)) * 30,  # Jump
                    1.0 + math.sin(t * math.pi * 2) * 0.1,  # Pulse scale
                    math.sin(t * math.pi * 2) * 10  # Wiggle rotation
                )
            }
        elif emotion == 'worried':
            return {
                'movement': lambda t, w, h: (
                    w/2 - 150 + math.sin(t * math.pi * 2) * 20,  # Gentle sway
                    h * 0.65,  # Static vertical
                    1.0,  # No scale change
                    math.sin(t * math.pi * 3) * 5  # Small nervous wiggle
                )
            }
        elif emotion == 'brave':
            return {
                'movement': lambda t, w, h: (
                    w/2 - 150 + t * 100,  # March forward
                    h * 0.6,  # Static vertical
                    1.0 + t * 0.2,  # Grow bigger
                    0  # No rotation
                )
            }
        else:
            return {
                'movement': lambda t, w, h: (
                    w/2 - 150,  # Center
                    h * 0.6,  # Static position
                    1.0,  # No scale
                    0  # No rotation
                )
            }
    
    def _get_standard_animations(self, emotion: str) -> Dict:
        """
        Get standard animations for longer form content
        """
        
        return {
            'movement': lambda t, w, h: (
                w/2 - 150 + math.sin(t * math.pi * 2) * 30,  # Gentle sway
                h * 0.7,  # Lower position
                1.0,  # No scale change
                0  # No rotation
            )
        }
    
    def _transform_sprite(
        self,
        sprite: Image.Image,
        scale: float = 1.0,
        rotation: float = 0.0
    ) -> Image.Image:
        """
        Apply transformations to sprite
        """
        
        # Scale
        if scale != 1.0:
            new_size = (
                int(sprite.width * scale),
                int(sprite.height * scale)
            )
            sprite = sprite.resize(new_size, Image.Resampling.LANCZOS)
        
        # Rotate
        if rotation != 0:
            sprite = sprite.rotate(rotation, expand=True, fillcolor=(0, 0, 0, 0))
        
        return sprite
    
    def _add_text_overlay(
        self,
        frame: Image.Image,
        text: str,
        frame_idx: int,
        total_frames: int
    ) -> Image.Image:
        """
        Add animated text overlay for TikTok style
        """
        
        # Create text layer
        from PIL import ImageFont
        
        try:
            # Try to use a fun font
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        draw = ImageDraw.Draw(frame)
        
        # Text animation (fade in/out)
        alpha = 1.0
        if frame_idx < 10:
            alpha = frame_idx / 10
        elif frame_idx > total_frames - 10:
            alpha = (total_frames - frame_idx) / 10
        
        # Draw text with shadow for readability
        text_color = (255, 255, 255, int(255 * alpha))
        shadow_color = (0, 0, 0, int(128 * alpha))
        
        # Center text
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (frame.width - text_width) // 2
        text_y = frame.height - 200
        
        # Draw shadow
        draw.text((text_x + 2, text_y + 2), text, font=font, fill=shadow_color)
        # Draw text
        draw.text((text_x, text_y), text, font=font, fill=text_color)
        
        return frame
    
    def _add_transitions(
        self,
        frames: List[Image.Image],
        fps: int,
        transition_duration: float = 0.5
    ) -> List[Image.Image]:
        """
        Add smooth transitions between scenes
        """
        
        transition_frames = int(transition_duration * fps)
        frames_with_transitions = []
        
        for i, frame in enumerate(frames):
            frames_with_transitions.append(frame)
            
            # Add transition at scene boundaries
            if i > 0 and i % (fps * 3) == 0 and i < len(frames) - 1:
                # Cross-fade transition
                for t in range(transition_frames):
                    alpha = t / transition_frames
                    
                    if i < len(frames) - 1:
                        blended = Image.blend(frames[i], frames[i + 1], alpha)
                        frames_with_transitions.append(blended)
        
        return frames_with_transitions
    
    async def create_social_story_video(
        self,
        story_data: Dict,
        target_issue: str,
        audience_age: str = 'teen'
    ) -> str:
        """
        Create educational social story videos for real-world issues
        """
        
        # Adjust pacing and complexity based on audience
        if audience_age == 'teen':
            scene_duration = 4  # Longer scenes for complex topics
            text_complexity = 'advanced'
        else:
            scene_duration = 3
            text_complexity = 'simple'
        
        # Create scenes that address the issue
        scenes = await self._create_social_story_scenes(
            story_data,
            target_issue,
            text_complexity
        )
        
        # Add educational overlays
        scenes_with_info = self._add_educational_overlays(
            scenes,
            target_issue,
            audience_age
        )
        
        settings = {
            'video_type': 'social_story',
            'genre': 'social_story',
            'duration_per_scene': scene_duration,
            'include_captions': True,
            'accessibility': True  # Add audio descriptions
        }
        
        return await self.create_story_animation(
            scenes_with_info,
            story_data.get('sprites', {}),
            settings
        )
    
    async def _compile_video(
        self,
        frames: List[Image.Image],
        width: int,
        height: int,
        fps: int,
        format: str = 'mp4',
        quality: str = 'high'
    ) -> str:
        """
        Compile frames into video file with quality options
        """
        
        if not OPENCV_AVAILABLE:
            # Try alternative libraries
            try:
                return await self._compile_with_moviepy(frames, width, height, fps, format)
            except:
                # Final fallback: save as GIF
                return await self._save_as_gif(frames)
        
        # Use OpenCV to create MP4
        import tempfile
        import os
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=f'.{format}', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        # Select codec based on quality
        if quality == 'high':
            fourcc = cv2.VideoWriter_fourcc(*'H264')  # Better quality
            bitrate = '5M'
        else:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            bitrate = '2M'
        
        out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))
        
        # Write frames
        for frame in frames:
            # Convert PIL to OpenCV format
            frame_array = np.array(frame.convert('RGB'))
            frame_bgr = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)
        
        out.release()
        
        # Upload to storage and return URL
        # This would upload to R2/S3
        video_url = f"https://storage.example.com/videos/{datetime.now().isoformat()}.{format}"
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return video_url
    
    async def _save_as_gif(self, frames: List[Image.Image]) -> str:
        """
        Fallback: Save as animated GIF
        """
        
        import tempfile
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.gif', delete=False)
        
        # Save as GIF
        frames[0].save(
            temp_file.name,
            save_all=True,
            append_images=frames[1:],
            duration=33,  # ~30fps
            loop=0
        )
        
        # Upload and return URL
        gif_url = f"https://storage.example.com/gifs/{datetime.now().isoformat()}.gif"
        
        return gif_url
    
    async def _load_image(self, url: str) -> Image.Image:
        """
        Load image from URL
        """
        
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return Image.open(io.BytesIO(response.content)).convert('RGBA')


    async def _compile_with_moviepy(self, frames, width, height, fps, format):
        """
        Alternative compilation using moviepy for better quality
        """
        try:
            from moviepy.editor import ImageSequenceClip
            import tempfile
            import os
            
            # Save frames as temp images
            temp_dir = tempfile.mkdtemp()
            frame_paths = []
            
            for i, frame in enumerate(frames):
                frame_path = os.path.join(temp_dir, f"frame_{i:05d}.png")
                frame.save(frame_path)
                frame_paths.append(frame_path)
            
            # Create video clip
            clip = ImageSequenceClip(frame_paths, fps=fps)
            
            # Export with high quality
            output_path = tempfile.NamedTemporaryFile(suffix=f'.{format}', delete=False).name
            clip.write_videofile(
                output_path,
                codec='libx264',
                audio=False,
                bitrate="5000k",
                preset='slow',  # Better compression
                ffmpeg_params=["-crf", "18"]  # High quality
            )
            
            # Clean up temp frames
            for path in frame_paths:
                os.unlink(path)
            os.rmdir(temp_dir)
            
            # Upload and return URL
            video_url = f"https://storage.example.com/videos/{datetime.now().isoformat()}.{format}"
            return video_url
            
        except ImportError:
            raise Exception("MoviePy not available, falling back to OpenCV")

# Global instance
video_generation_service = VideoGenerationService()