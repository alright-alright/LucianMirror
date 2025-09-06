"""
Base adapter class and implementations for different image generation APIs
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import os
import httpx
import base64
from io import BytesIO
from PIL import Image
import json

class GenerationAdapter(ABC):
    """Base class for all image generation adapters"""
    
    @abstractmethod
    async def generate_sprite(
        self, 
        prompt: str, 
        reference_image: Optional[str] = None,
        style: str = "consistent_character",
        **kwargs
    ) -> str:
        """Generate a single sprite and return URL"""
        pass
    
    @abstractmethod
    async def generate_background(
        self,
        setting: str,
        time_of_day: str,
        style: str = "watercolor",
        **kwargs
    ) -> str:
        """Generate a background and return URL"""
        pass


class DalleAdapter(GenerationAdapter):
    """DALL-E 3 API adapter"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/images/generations"
        
    async def generate_sprite(
        self, 
        prompt: str, 
        reference_image: Optional[str] = None,
        style: str = "consistent_character",
        **kwargs
    ) -> str:
        """Generate sprite using DALL-E 3"""
        
        # Enhance prompt for sprite generation
        enhanced_prompt = self._build_sprite_prompt(prompt, style)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "dall-e-3",
                    "prompt": enhanced_prompt,
                    "n": 1,
                    "size": "1024x1024",
                    "quality": "hd",
                    "style": "vivid"
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["data"][0]["url"]
            else:
                raise Exception(f"DALL-E API error: {response.text}")
    
    async def generate_background(
        self,
        setting: str,
        time_of_day: str,
        style: str = "watercolor",
        **kwargs
    ) -> str:
        """Generate background using DALL-E 3"""
        
        prompt = self._build_background_prompt(setting, time_of_day, style)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "dall-e-3",
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1024",
                    "quality": "standard",
                    "style": "vivid"
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["data"][0]["url"]
            else:
                raise Exception(f"DALL-E API error: {response.text}")
    
    def _build_sprite_prompt(self, base_prompt: str, style: str) -> str:
        """Build enhanced prompt for sprite generation"""
        style_modifiers = {
            "consistent_character": "consistent character design, clear silhouette, transparent background, high quality sprite art",
            "watercolor": "watercolor style character, soft edges, transparent background",
            "cartoon": "cartoon character, bold lines, simple shapes, transparent background",
            "realistic": "realistic character, detailed features, transparent background"
        }
        
        modifier = style_modifiers.get(style, style_modifiers["consistent_character"])
        return f"{base_prompt}, {modifier}, centered composition, full body visible"
    
    def _build_background_prompt(self, setting: str, time_of_day: str, style: str) -> str:
        """Build prompt for background generation"""
        return f"Empty {setting} scene during {time_of_day}, {style} art style, no characters or people, scenic background only, children's book illustration"


class StableDiffusionAdapter(GenerationAdapter):
    """Stable Diffusion API adapter (using Stability AI or local)"""
    
    def __init__(self, api_url: Optional[str] = None):
        self.api_key = os.getenv("STABILITY_API_KEY")
        self.api_url = api_url or "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
    async def generate_sprite(
        self, 
        prompt: str, 
        reference_image: Optional[str] = None,
        style: str = "consistent_character",
        **kwargs
    ) -> str:
        """Generate sprite using Stable Diffusion"""
        
        enhanced_prompt = self._build_sprite_prompt(prompt, style)
        negative_prompt = "background, scenery, multiple characters, text, watermark"
        
        payload = {
            "text_prompts": [
                {"text": enhanced_prompt, "weight": 1},
                {"text": negative_prompt, "weight": -1}
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30
        }
        
        # Add reference image if provided (for ControlNet/IP-Adapter)
        if reference_image and kwargs.get("use_controlnet"):
            payload["init_image"] = reference_image
            payload["init_image_mode"] = "IMAGE_STRENGTH"
            payload["image_strength"] = 0.35
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json=payload,
                timeout=120.0
            )
            
            if response.status_code == 200:
                data = response.json()
                # Process and save image
                image_data = base64.b64decode(data["artifacts"][0]["base64"])
                return await self._save_image(image_data)
            else:
                raise Exception(f"Stable Diffusion API error: {response.text}")
    
    async def generate_background(
        self,
        setting: str,
        time_of_day: str,
        style: str = "watercolor",
        **kwargs
    ) -> str:
        """Generate background using Stable Diffusion"""
        
        prompt = self._build_background_prompt(setting, time_of_day, style)
        negative_prompt = "people, characters, figures, text, watermark"
        
        payload = {
            "text_prompts": [
                {"text": prompt, "weight": 1},
                {"text": negative_prompt, "weight": -1}
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 25
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json=payload,
                timeout=120.0
            )
            
            if response.status_code == 200:
                data = response.json()
                image_data = base64.b64decode(data["artifacts"][0]["base64"])
                return await self._save_image(image_data)
            else:
                raise Exception(f"Stable Diffusion API error: {response.text}")
    
    def _build_sprite_prompt(self, base_prompt: str, style: str) -> str:
        """Build enhanced prompt for sprite generation"""
        return f"{base_prompt}, isolated character, transparent background, {style}, high quality, detailed"
    
    def _build_background_prompt(self, setting: str, time_of_day: str, style: str) -> str:
        """Build prompt for background generation"""
        return f"{setting} environment, {time_of_day} lighting, {style} painting style, empty scene, no people"
    
    async def _save_image(self, image_data: bytes) -> str:
        """Save image and return URL"""
        # TODO: Implement actual storage (S3/R2)
        # For now, return a placeholder
        return "https://storage.example.com/generated_image.png"


class LocalSDAdapter(GenerationAdapter):
    """Local Stable Diffusion with LoRA support"""
    
    def __init__(self, model_path: str = "./models"):
        self.model_path = model_path
        self.pipeline = None
        self._init_pipeline()
    
    def _init_pipeline(self):
        """Initialize the diffusion pipeline"""
        try:
            from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
            import torch
            
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                "stabilityai/stable-diffusion-2-1",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            
            self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipeline.scheduler.config
            )
            
            if torch.cuda.is_available():
                self.pipeline = self.pipeline.to("cuda")
            
        except ImportError:
            print("Diffusers library not installed. Install with: pip install diffusers transformers")
    
    async def generate_sprite(
        self, 
        prompt: str, 
        reference_image: Optional[str] = None,
        style: str = "consistent_character",
        lora_path: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate sprite using local Stable Diffusion"""
        
        if not self.pipeline:
            raise Exception("Pipeline not initialized")
        
        # Load LoRA if provided
        if lora_path:
            self._load_lora(lora_path)
        
        enhanced_prompt = self._build_sprite_prompt(prompt, style)
        negative_prompt = "background, multiple people, text"
        
        # Generate image
        image = self.pipeline(
            prompt=enhanced_prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=30,
            guidance_scale=7.5,
            height=512,
            width=512
        ).images[0]
        
        # Remove background
        image_with_transparency = await self._remove_background(image)
        
        # Save and return URL
        return await self._save_image(image_with_transparency)
    
    async def generate_background(
        self,
        setting: str,
        time_of_day: str,
        style: str = "watercolor",
        **kwargs
    ) -> str:
        """Generate background using local Stable Diffusion"""
        
        if not self.pipeline:
            raise Exception("Pipeline not initialized")
        
        prompt = self._build_background_prompt(setting, time_of_day, style)
        negative_prompt = "people, characters, text"
        
        image = self.pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=25,
            guidance_scale=7.5,
            height=512,
            width=512
        ).images[0]
        
        return await self._save_image(image)
    
    def _load_lora(self, lora_path: str):
        """Load LoRA weights"""
        # TODO: Implement LoRA loading
        pass
    
    async def _remove_background(self, image: Image.Image) -> Image.Image:
        """Remove background from image"""
        try:
            from rembg import remove
            
            # Convert to RGBA
            image_rgba = image.convert("RGBA")
            
            # Remove background
            output = remove(image_rgba)
            
            return output
        except ImportError:
            print("rembg not installed. Install with: pip install rembg")
            return image
    
    def _build_sprite_prompt(self, base_prompt: str, style: str) -> str:
        """Build enhanced prompt for sprite generation"""
        return f"{base_prompt}, white background, centered, {style}, high quality"
    
    def _build_background_prompt(self, setting: str, time_of_day: str, style: str) -> str:
        """Build prompt for background generation"""
        return f"{setting}, {time_of_day}, {style} art style, scenic, no people"
    
    async def _save_image(self, image: Image.Image) -> str:
        """Save image and return URL"""
        # TODO: Implement actual storage
        return "https://storage.example.com/generated_image.png"


class AdapterFactory:
    """Factory for creating generation adapters"""
    
    @staticmethod
    def create_adapter(adapter_type: str = "dalle") -> GenerationAdapter:
        """Create and return the appropriate adapter"""
        
        adapters = {
            "dalle": DalleAdapter,
            "stable_diffusion": StableDiffusionAdapter,
            "local_sd": LocalSDAdapter
        }
        
        adapter_class = adapters.get(adapter_type, DalleAdapter)
        return adapter_class()
