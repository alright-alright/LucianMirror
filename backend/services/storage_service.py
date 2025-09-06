"""
Storage Service for managing sprite files
Supports local storage, S3, and Cloudflare R2
"""

import os
import io
import uuid
import hashlib
from typing import Optional, Dict, Any, List
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import aiofiles
from PIL import Image
import json

class StorageService:
    """Base storage service interface"""
    
    async def upload_image(self, image_data: bytes, key: str) -> str:
        """Upload image and return URL"""
        raise NotImplementedError
    
    async def download_image(self, key: str) -> bytes:
        """Download image data"""
        raise NotImplementedError
    
    async def delete_image(self, key: str) -> bool:
        """Delete image"""
        raise NotImplementedError
    
    async def list_images(self, prefix: str) -> List[str]:
        """List images with prefix"""
        raise NotImplementedError


class LocalStorageService(StorageService):
    """Local file system storage"""
    
    def __init__(self, base_path: str = "./storage"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        
    async def upload_image(self, image_data: bytes, key: str) -> str:
        """Save image to local filesystem"""
        
        file_path = os.path.join(self.base_path, key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(image_data)
        
        # Return local URL
        return f"file://{os.path.abspath(file_path)}"
    
    async def download_image(self, key: str) -> bytes:
        """Read image from local filesystem"""
        
        file_path = os.path.join(self.base_path, key)
        
        async with aiofiles.open(file_path, 'rb') as f:
            return await f.read()
    
    async def delete_image(self, key: str) -> bool:
        """Delete image from local filesystem"""
        
        file_path = os.path.join(self.base_path, key)
        
        try:
            os.remove(file_path)
            return True
        except FileNotFoundError:
            return False
    
    async def list_images(self, prefix: str) -> List[str]:
        """List images in directory"""
        
        path = os.path.join(self.base_path, prefix)
        
        if not os.path.exists(path):
            return []
        
        files = []
        for root, dirs, filenames in os.walk(path):
            for filename in filenames:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    rel_path = os.path.relpath(os.path.join(root, filename), self.base_path)
                    files.append(rel_path)
        
        return files


class R2StorageService(StorageService):
    """Cloudflare R2 storage service"""
    
    def __init__(self):
        self.account_id = os.getenv("R2_ACCOUNT_ID")
        self.access_key = os.getenv("R2_ACCESS_KEY_ID")
        self.secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
        self.bucket_name = os.getenv("R2_BUCKET_NAME", "lucianmirror-sprites")
        self.public_url = os.getenv("R2_PUBLIC_URL")
        
        self.client = boto3.client(
            's3',
            endpoint_url=f"https://{self.account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name='auto'
        )
    
    async def upload_image(self, image_data: bytes, key: str) -> str:
        """Upload image to R2"""
        
        try:
            # Add content type based on extension
            content_type = self._get_content_type(key)
            
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_data,
                ContentType=content_type
            )
            
            # Return public URL
            return f"{self.public_url}/{key}"
            
        except ClientError as e:
            raise Exception(f"R2 upload error: {e}")
    
    async def download_image(self, key: str) -> bytes:
        """Download image from R2"""
        
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return response['Body'].read()
            
        except ClientError as e:
            raise Exception(f"R2 download error: {e}")
    
    async def delete_image(self, key: str) -> bool:
        """Delete image from R2"""
        
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
            
        except ClientError:
            return False
    
    async def list_images(self, prefix: str) -> List[str]:
        """List images in R2 with prefix"""
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            return [obj['Key'] for obj in response['Contents']]
            
        except ClientError as e:
            raise Exception(f"R2 list error: {e}")
    
    def _get_content_type(self, key: str) -> str:
        """Get content type from file extension"""
        
        ext = key.lower().split('.')[-1]
        content_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'webp': 'image/webp',
            'gif': 'image/gif'
        }
        return content_types.get(ext, 'application/octet-stream')


class SpriteStorageManager:
    """High-level sprite storage management"""
    
    def __init__(self, storage_type: str = "local"):
        if storage_type == "r2":
            self.storage = R2StorageService()
        else:
            self.storage = LocalStorageService()
        
        self.manifest_cache = {}
    
    async def save_sprite(
        self,
        image: Image.Image,
        character_id: str,
        sprite_type: str,
        pose: str,
        emotion: str
    ) -> Dict[str, str]:
        """
        Save a sprite and return URLs
        
        Args:
            image: PIL Image object
            character_id: Character identifier
            sprite_type: Type of sprite (character, family, pet, item)
            pose: Pose name
            emotion: Emotion name
            
        Returns:
            Dictionary with urls and metadata
        """
        
        # Generate unique key
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        sprite_id = f"{character_id}_{sprite_type}_{pose}_{emotion}_{timestamp}"
        
        # Save full size
        full_key = f"sprites/{character_id}/{sprite_type}/{sprite_id}.png"
        full_data = self._image_to_bytes(image, "PNG")
        full_url = await self.storage.upload_image(full_data, full_key)
        
        # Save thumbnail
        thumbnail = self._create_thumbnail(image)
        thumb_key = f"sprites/{character_id}/{sprite_type}/thumbs/{sprite_id}_thumb.png"
        thumb_data = self._image_to_bytes(thumbnail, "PNG")
        thumb_url = await self.storage.upload_image(thumb_data, thumb_key)
        
        return {
            "sprite_id": sprite_id,
            "url": full_url,
            "thumbnail_url": thumb_url,
            "character_id": character_id,
            "sprite_type": sprite_type,
            "pose": pose,
            "emotion": emotion,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def save_sprite_manifest(
        self,
        character_id: str,
        sprites: List[Dict[str, Any]]
    ) -> str:
        """Save sprite manifest for a character"""
        
        manifest = {
            "character_id": character_id,
            "created_at": datetime.utcnow().isoformat(),
            "sprite_count": len(sprites),
            "sprites": sprites,
            "version": "1.0"
        }
        
        # Save manifest as JSON
        manifest_key = f"manifests/{character_id}/manifest.json"
        manifest_data = json.dumps(manifest, indent=2).encode()
        manifest_url = await self.storage.upload_image(manifest_data, manifest_key)
        
        # Cache manifest
        self.manifest_cache[character_id] = manifest
        
        return manifest_url
    
    async def load_sprite_manifest(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Load sprite manifest for a character"""
        
        # Check cache first
        if character_id in self.manifest_cache:
            return self.manifest_cache[character_id]
        
        try:
            manifest_key = f"manifests/{character_id}/manifest.json"
            manifest_data = await self.storage.download_image(manifest_key)
            manifest = json.loads(manifest_data.decode())
            
            # Cache it
            self.manifest_cache[character_id] = manifest
            
            return manifest
            
        except Exception:
            return None
    
    async def delete_character_sprites(self, character_id: str) -> bool:
        """Delete all sprites for a character"""
        
        # List all sprites
        sprites = await self.storage.list_images(f"sprites/{character_id}/")
        
        # Delete each sprite
        for sprite_key in sprites:
            await self.storage.delete_image(sprite_key)
        
        # Delete manifest
        manifest_key = f"manifests/{character_id}/manifest.json"
        await self.storage.delete_image(manifest_key)
        
        # Clear cache
        if character_id in self.manifest_cache:
            del self.manifest_cache[character_id]
        
        return True
    
    def _image_to_bytes(self, image: Image.Image, format: str = "PNG") -> bytes:
        """Convert PIL Image to bytes"""
        
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_thumbnail(self, image: Image.Image, size: Tuple[int, int] = (256, 256)) -> Image.Image:
        """Create thumbnail from image"""
        
        thumbnail = image.copy()
        thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
        return thumbnail
    
    async def create_sprite_sheet(
        self,
        character_id: str,
        output_format: str = "unity"
    ) -> str:
        """
        Create a sprite sheet for game engines
        
        Args:
            character_id: Character to create sheet for
            output_format: Format type (unity, godot, generic)
            
        Returns:
            URL of sprite sheet
        """
        
        manifest = await self.load_sprite_manifest(character_id)
        
        if not manifest:
            raise Exception(f"No manifest found for character {character_id}")
        
        sprites = manifest["sprites"]
        
        # Calculate sheet dimensions
        sprite_count = len(sprites)
        cols = 8  # 8 columns
        rows = (sprite_count + cols - 1) // cols
        
        sprite_size = (256, 256)
        sheet_width = cols * sprite_size[0]
        sheet_height = rows * sprite_size[1]
        
        # Create sheet
        sheet = Image.new("RGBA", (sheet_width, sheet_height), (0, 0, 0, 0))
        
        # Place sprites
        for i, sprite_data in enumerate(sprites):
            # Download sprite
            sprite_key = sprite_data["url"].split("/")[-1]
            sprite_bytes = await self.storage.download_image(f"sprites/{character_id}/{sprite_key}")
            sprite = Image.open(io.BytesIO(sprite_bytes))
            
            # Resize to standard size
            sprite = sprite.resize(sprite_size, Image.Resampling.LANCZOS)
            
            # Calculate position
            col = i % cols
            row = i // cols
            x = col * sprite_size[0]
            y = row * sprite_size[1]
            
            # Paste onto sheet
            sheet.paste(sprite, (x, y), sprite)
        
        # Save sheet
        sheet_key = f"sheets/{character_id}/sprite_sheet_{output_format}.png"
        sheet_data = self._image_to_bytes(sheet, "PNG")
        sheet_url = await self.storage.upload_image(sheet_data, sheet_key)
        
        # Generate metadata for game engines
        if output_format == "unity":
            metadata = self._generate_unity_metadata(sprites, sprite_size, cols)
        elif output_format == "godot":
            metadata = self._generate_godot_metadata(sprites, sprite_size, cols)
        else:
            metadata = None
        
        if metadata:
            meta_key = f"sheets/{character_id}/sprite_sheet_{output_format}.meta"
            await self.storage.upload_image(metadata.encode(), meta_key)
        
        return sheet_url
    
    def _generate_unity_metadata(
        self,
        sprites: List[Dict],
        sprite_size: Tuple[int, int],
        cols: int
    ) -> str:
        """Generate Unity .meta file for sprite sheet"""
        
        # Unity metadata format
        metadata = {
            "TextureImporter": {
                "spriteMode": 2,
                "spriteSheet": {
                    "sprites": []
                }
            }
        }
        
        for i, sprite in enumerate(sprites):
            col = i % cols
            row = i // cols
            
            metadata["TextureImporter"]["spriteSheet"]["sprites"].append({
                "name": f"{sprite['pose']}_{sprite['emotion']}",
                "rect": {
                    "x": col * sprite_size[0],
                    "y": row * sprite_size[1],
                    "width": sprite_size[0],
                    "height": sprite_size[1]
                },
                "pivot": {"x": 0.5, "y": 0.5}
            })
        
        return json.dumps(metadata, indent=2)
    
    def _generate_godot_metadata(
        self,
        sprites: List[Dict],
        sprite_size: Tuple[int, int],
        cols: int
    ) -> str:
        """Generate Godot .tres file for sprite sheet"""
        
        # Godot resource format
        tres = "[gd_resource type=\"AtlasTexture\"]\n\n"
        
        for i, sprite in enumerate(sprites):
            col = i % cols
            row = i // cols
            
            tres += f"[sub_resource type=\"AtlasTexture\" id={i+1}]\n"
            tres += f"atlas = ExtResource(1)\n"
            tres += f"region = Rect2({col * sprite_size[0]}, {row * sprite_size[1]}, {sprite_size[0]}, {sprite_size[1]})\n\n"
        
        return tres


# Global instance
sprite_storage = SpriteStorageManager(
    storage_type=os.getenv("STORAGE_TYPE", "local")
)
