"""
Profile and Template Management Service
Reusable standards for AI artifact generation
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
from dataclasses import dataclass, asdict


@dataclass
class GenerationProfile:
    """
    Reusable profile for consistent AI generation
    """
    profile_id: str
    profile_name: str
    profile_type: str  # personal, company, project, character
    
    # Visual Standards
    art_style: str  # watercolor, photorealistic, anime, corporate, etc.
    color_palette: List[str]  # Hex colors for consistency
    lighting_preference: str  # bright, moody, natural, studio
    composition_rules: Dict[str, Any]  # Rule of thirds, centered, etc.
    
    # Generation Parameters
    quality_preset: str  # draft, standard, high, production
    preferred_providers: List[str]  # Ordered by preference
    fallback_providers: List[str]
    
    # Style References
    reference_images: List[str]  # URLs to style references
    negative_prompts: List[str]  # Things to avoid
    style_weights: Dict[str, float]  # Style emphasis
    
    # Metadata
    created_by: str
    created_at: str
    last_modified: str
    version: str
    tags: List[str]


@dataclass
class CompanyStandards:
    """
    Company-wide standards for brand consistency
    """
    company_id: str
    company_name: str
    
    # Brand Guidelines
    brand_colors: Dict[str, str]  # primary, secondary, accent
    typography: Dict[str, str]  # fonts for different contexts
    logo_placement: Dict[str, Any]  # positioning rules
    
    # Content Standards
    tone_of_voice: List[str]  # professional, friendly, casual
    content_rating: str  # G, PG, PG-13, etc.
    cultural_sensitivity: Dict[str, Any]
    accessibility_requirements: Dict[str, Any]
    
    # Legal/Compliance
    copyright_text: str
    disclaimers: List[str]
    usage_rights: Dict[str, Any]
    
    # AI Generation Rules
    approved_models: List[str]
    prohibited_content: List[str]
    quality_thresholds: Dict[str, float]


class ProfileTemplateService:
    """
    Manages reusable profiles and templates for AI generation
    """
    
    def __init__(self):
        self.profiles = {}  # profile_id -> GenerationProfile
        self.company_standards = {}  # company_id -> CompanyStandards
        self.templates = {}  # template_id -> template data
        self.prompt_library = PromptLibrary()
        
    async def create_generation_profile(
        self,
        profile_name: str,
        profile_type: str,
        settings: Dict[str, Any]
    ) -> GenerationProfile:
        """
        Create a reusable generation profile
        """
        
        profile = GenerationProfile(
            profile_id=f"profile_{uuid.uuid4().hex[:8]}",
            profile_name=profile_name,
            profile_type=profile_type,
            art_style=settings.get('art_style', 'watercolor'),
            color_palette=settings.get('color_palette', []),
            lighting_preference=settings.get('lighting', 'natural'),
            composition_rules=settings.get('composition', {}),
            quality_preset=settings.get('quality', 'standard'),
            preferred_providers=settings.get('preferred_providers', ['dalle']),
            fallback_providers=settings.get('fallback_providers', ['stable_diffusion']),
            reference_images=settings.get('references', []),
            negative_prompts=settings.get('negative_prompts', []),
            style_weights=settings.get('style_weights', {}),
            created_by=settings.get('created_by', 'system'),
            created_at=datetime.utcnow().isoformat(),
            last_modified=datetime.utcnow().isoformat(),
            version='1.0.0',
            tags=settings.get('tags', [])
        )
        
        self.profiles[profile.profile_id] = profile
        return profile
    
    async def create_company_standards(
        self,
        company_name: str,
        brand_guidelines: Dict[str, Any]
    ) -> CompanyStandards:
        """
        Create company-wide standards for consistency
        """
        
        standards = CompanyStandards(
            company_id=f"company_{uuid.uuid4().hex[:8]}",
            company_name=company_name,
            brand_colors=brand_guidelines.get('colors', {}),
            typography=brand_guidelines.get('typography', {}),
            logo_placement=brand_guidelines.get('logo', {}),
            tone_of_voice=brand_guidelines.get('tone', ['professional']),
            content_rating=brand_guidelines.get('rating', 'PG'),
            cultural_sensitivity=brand_guidelines.get('cultural', {}),
            accessibility_requirements=brand_guidelines.get('accessibility', {}),
            copyright_text=brand_guidelines.get('copyright', ''),
            disclaimers=brand_guidelines.get('disclaimers', []),
            usage_rights=brand_guidelines.get('usage_rights', {}),
            approved_models=brand_guidelines.get('approved_models', []),
            prohibited_content=brand_guidelines.get('prohibited', []),
            quality_thresholds=brand_guidelines.get('quality', {})
        )
        
        self.company_standards[standards.company_id] = standards
        return standards
    
    def apply_profile_to_prompt(
        self,
        base_prompt: str,
        profile_id: str
    ) -> str:
        """
        Apply a profile's standards to a prompt
        """
        
        profile = self.profiles.get(profile_id)
        if not profile:
            return base_prompt
        
        # Build enhanced prompt with profile standards
        enhanced_prompt = f"{base_prompt}, {profile.art_style} style"
        
        # Add color palette
        if profile.color_palette:
            colors = ', '.join(profile.color_palette)
            enhanced_prompt += f", color palette: {colors}"
        
        # Add lighting
        enhanced_prompt += f", {profile.lighting_preference} lighting"
        
        # Add negative prompts
        if profile.negative_prompts:
            enhanced_prompt += f", avoid: {', '.join(profile.negative_prompts)}"
        
        return enhanced_prompt
    
    def get_generation_settings(
        self,
        profile_id: str,
        company_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get complete generation settings from profile and company standards
        """
        
        settings = {}
        
        # Apply profile settings
        if profile_id in self.profiles:
            profile = self.profiles[profile_id]
            settings.update({
                'art_style': profile.art_style,
                'quality': profile.quality_preset,
                'providers': profile.preferred_providers,
                'fallbacks': profile.fallback_providers,
                'style_weights': profile.style_weights
            })
        
        # Apply company standards
        if company_id and company_id in self.company_standards:
            standards = self.company_standards[company_id]
            settings.update({
                'brand_colors': standards.brand_colors,
                'content_rating': standards.content_rating,
                'approved_models': standards.approved_models,
                'quality_thresholds': standards.quality_thresholds
            })
        
        return settings
    
    async def create_artifact_template(
        self,
        template_name: str,
        template_type: str,
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a reusable template for artifact generation
        """
        
        template_id = f"template_{uuid.uuid4().hex[:8]}"
        
        template = {
            'template_id': template_id,
            'template_name': template_name,
            'template_type': template_type,  # sprite_sheet, story, video, game_asset
            'template_data': template_data,
            'created_at': datetime.utcnow().isoformat(),
            'usage_count': 0
        }
        
        self.templates[template_id] = template
        return template
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a template for reuse
        """
        
        template = self.templates.get(template_id)
        if template:
            template['usage_count'] += 1
        return template
    
    async def export_profile(self, profile_id: str) -> str:
        """
        Export a profile as JSON for sharing/backup
        """
        
        profile = self.profiles.get(profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")
        
        return json.dumps(asdict(profile), indent=2)
    
    async def import_profile(self, profile_json: str) -> GenerationProfile:
        """
        Import a profile from JSON
        """
        
        data = json.loads(profile_json)
        profile = GenerationProfile(**data)
        
        # Generate new ID to avoid conflicts
        profile.profile_id = f"profile_{uuid.uuid4().hex[:8]}"
        profile.last_modified = datetime.utcnow().isoformat()
        
        self.profiles[profile.profile_id] = profile
        return profile


class PromptLibrary:
    """
    Library of reusable prompt templates and components
    """
    
    def __init__(self):
        self.prompts = {
            'character': {
                'base': "{name}, {age} years old, {description}",
                'detailed': "{name}, {age} years old, {gender}, {ethnicity}, {body_type}, wearing {clothing}, {expression} expression",
                'sprite': "{name} character sprite, {pose} pose, {emotion} emotion, transparent background, {style} style"
            },
            'background': {
                'simple': "{location}, {time_of_day}, {weather}",
                'detailed': "{location} environment, {time_of_day} lighting, {weather} conditions, {mood} atmosphere, {style} art style",
                'game': "{location} game background, {layer} layer, tileable, {style} style"
            },
            'scene': {
                'story': "{characters} in {location}, {action}, {mood} mood, {style} illustration",
                'video': "Frame {frame_num}: {description}, cinematic composition, {camera_angle}",
                'game': "{location} scene, game perspective, {interactive_elements}"
            },
            'style_modifiers': {
                'quality': [
                    "masterpiece",
                    "best quality",
                    "high resolution",
                    "detailed",
                    "professional"
                ],
                'artistic': [
                    "watercolor",
                    "oil painting",
                    "digital art",
                    "anime style",
                    "photorealistic",
                    "cel shaded",
                    "low poly",
                    "pixel art"
                ],
                'lighting': [
                    "soft lighting",
                    "dramatic lighting",
                    "golden hour",
                    "studio lighting",
                    "natural light",
                    "neon lighting",
                    "backlit"
                ],
                'camera': [
                    "wide shot",
                    "close up",
                    "medium shot",
                    "bird's eye view",
                    "low angle",
                    "dutch angle",
                    "over the shoulder"
                ]
            },
            'negative': {
                'common': [
                    "blurry",
                    "low quality",
                    "distorted",
                    "disfigured",
                    "bad anatomy",
                    "watermark",
                    "text",
                    "logo"
                ],
                'character': [
                    "extra limbs",
                    "missing limbs",
                    "floating limbs",
                    "disconnected limbs",
                    "malformed hands",
                    "extra fingers"
                ]
            }
        }
    
    def build_prompt(
        self,
        template_type: str,
        template_name: str,
        variables: Dict[str, str],
        modifiers: Optional[List[str]] = None,
        negative: Optional[List[str]] = None
    ) -> str:
        """
        Build a prompt from templates and variables
        """
        
        # Get base template
        template = self.prompts.get(template_type, {}).get(template_name, "")
        
        # Replace variables
        prompt = template.format(**variables)
        
        # Add modifiers
        if modifiers:
            prompt += ", " + ", ".join(modifiers)
        
        # Build negative prompt
        negative_prompt = ""
        if negative:
            negative_prompt = ", ".join(negative)
        
        return prompt, negative_prompt
    
    def get_style_preset(self, style_name: str) -> Dict[str, Any]:
        """
        Get a complete style preset
        """
        
        presets = {
            'children_book': {
                'modifiers': ['watercolor', 'soft lighting', 'whimsical', 'colorful'],
                'negative': ['scary', 'dark', 'violent', 'realistic'],
                'settings': {
                    'cfg_scale': 7,
                    'steps': 30
                }
            },
            'anime': {
                'modifiers': ['anime style', 'cel shaded', 'vibrant colors'],
                'negative': ['realistic', 'photographic', '3d render'],
                'settings': {
                    'cfg_scale': 8,
                    'steps': 40
                }
            },
            'photorealistic': {
                'modifiers': ['photorealistic', 'high detail', '8k', 'professional photography'],
                'negative': ['cartoon', 'painting', 'drawing', 'illustration'],
                'settings': {
                    'cfg_scale': 7.5,
                    'steps': 50
                }
            },
            'game_asset': {
                'modifiers': ['game art', 'clean lines', 'consistent style'],
                'negative': ['blurry', 'photograph', 'realistic'],
                'settings': {
                    'cfg_scale': 8,
                    'steps': 35
                }
            }
        }
        
        return presets.get(style_name, presets['children_book'])


class ArtifactTemplates:
    """
    Reusable templates for different artifact types
    """
    
    @staticmethod
    def sprite_sheet_template() -> Dict[str, Any]:
        """Template for sprite sheet generation"""
        return {
            'grid_size': (8, 8),
            'sprite_size': (128, 128),
            'poses': [
                'idle_front', 'idle_back', 'idle_left', 'idle_right',
                'walk_front', 'walk_back', 'walk_left', 'walk_right',
                'run_front', 'run_back', 'run_left', 'run_right',
                'attack', 'defend', 'hurt', 'victory'
            ],
            'format': 'png',
            'background': 'transparent'
        }
    
    @staticmethod
    def story_template() -> Dict[str, Any]:
        """Template for story generation"""
        return {
            'structure': {
                'introduction': {'scenes': 1, 'duration': 15},
                'rising_action': {'scenes': 2, 'duration': 30},
                'climax': {'scenes': 1, 'duration': 20},
                'resolution': {'scenes': 1, 'duration': 15}
            },
            'scene_composition': {
                'background': True,
                'characters': True,
                'foreground_elements': False,
                'text_overlay': True
            },
            'transitions': ['fade', 'dissolve', 'cut']
        }
    
    @staticmethod
    def video_template(video_type: str = 'tiktok') -> Dict[str, Any]:
        """Template for video generation"""
        templates = {
            'tiktok': {
                'aspect_ratio': '9:16',
                'duration': 15,
                'fps': 30,
                'resolution': (1080, 1920),
                'include_music': True,
                'include_captions': True
            },
            'youtube_short': {
                'aspect_ratio': '9:16',
                'duration': 60,
                'fps': 30,
                'resolution': (1080, 1920),
                'include_music': True,
                'include_captions': True
            },
            'instagram_reel': {
                'aspect_ratio': '9:16',
                'duration': 30,
                'fps': 30,
                'resolution': (1080, 1920),
                'include_music': True,
                'include_captions': False
            },
            'standard': {
                'aspect_ratio': '16:9',
                'duration': 120,
                'fps': 24,
                'resolution': (1920, 1080),
                'include_music': False,
                'include_captions': False
            }
        }
        return templates.get(video_type, templates['standard'])
    
    @staticmethod
    def game_asset_template(asset_type: str = 'character') -> Dict[str, Any]:
        """Template for game asset generation"""
        templates = {
            'character': {
                'sprite_count': 16,
                'animations': ['idle', 'walk', 'run', 'attack', 'hurt'],
                'equipment_slots': ['weapon', 'armor', 'accessory'],
                'export_formats': ['png', 'atlas']
            },
            'tileset': {
                'tile_size': 32,
                'grid': (16, 16),
                'categories': ['ground', 'walls', 'props', 'decoration'],
                'seamless': True
            },
            'ui': {
                'elements': ['buttons', 'panels', 'icons', 'bars'],
                'states': ['normal', 'hover', 'pressed', 'disabled'],
                'sizes': ['small', 'medium', 'large']
            }
        }
        return templates.get(asset_type, templates['character'])


# Global instance
profile_template_service = ProfileTemplateService()