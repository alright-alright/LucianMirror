"""
LucianMirror AI Brain
Local intelligence layer that reduces external API dependency
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
import asyncio
from collections import defaultdict


@dataclass
class GenerationContext:
    """Context for intelligent generation decisions"""
    user_id: str
    session_id: str
    character_profiles: Dict[str, Any]
    story_context: Optional[str]
    generation_history: List[Dict]
    quality_scores: List[float]
    provider_performance: Dict[str, float]
    cost_accumulated: float
    timestamp: datetime


class LucianBrain:
    """
    Local AI brain that makes intelligent decisions about generation
    Leverages LucianOS components for context-aware intelligence
    """
    
    def __init__(self):
        # LucianOS Components
        from core.mpu import MPU
        from core.ssp import SSP
        from core.hasr import HASR
        
        self.mpu = MPU()  # Memory Processing Unit for sprite storage
        self.ssp = SSP()  # Symbolic Sense Processor for understanding
        self.hasr = HASR()  # Hebbian learning for optimization
        
        # Additional intelligence layers
        self.context_memory = {}  # Active contexts
        self.pattern_library = PatternLibrary()
        self.quality_predictor = QualityPredictor()
        self.cost_optimizer = CostOptimizer()
        self.style_transfer = StyleTransferEngine()
        
    async def should_generate_new(
        self,
        request_type: str,
        requirements: Dict[str, Any],
        context: GenerationContext
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Decide if we need to generate new content or can reuse/modify existing
        
        Returns:
            (should_generate, alternative_action, metadata)
        """
        
        # Use MPU to check for existing sprites
        if request_type == 'sprite':
            character_id = requirements.get('character_id')
            pose = requirements.get('pose')
            emotion = requirements.get('emotion')
            
            # MPU's multi-dimensional search
            existing_sprites = self.mpu.query(
                character_id=character_id,
                pose=pose,
                emotion=emotion
            )
            
            if existing_sprites:
                # Found exact match in MPU
                return False, 'use_mpu_cache', {
                    'sprite': existing_sprites[0],
                    'confidence': 1.0,
                    'source': 'mpu'
                }
            
            # Check for similar sprites we could modify
            similar = self.mpu.find_best_match(character_id, pose, emotion)
            if similar:
                similarity_score = self._calculate_similarity(similar, requirements)
                if similarity_score > 0.85:
                    return False, 'modify_existing', {
                        'sprite': similar,
                        'similarity': similarity_score,
                        'modifications': self._determine_modifications(similar, requirements)
                    }
        
        # Check if we're in a loop (user requesting similar things)
        if self._detect_generation_loop(context):
            return False, 'suggest_alternative', {
                'reason': 'Similar request detected',
                'suggestion': 'Use existing asset or modify requirements'
            }
        
        # Check quality prediction
        predicted_quality = self.quality_predictor.predict(
            requirements,
            context.provider_performance
        )
        
        if predicted_quality < 0.6:
            # Low quality predicted, suggest improvements
            improvements = self._suggest_improvements(requirements)
            return True, 'generate_with_improvements', improvements
        
        return True, 'generate_new', {'predicted_quality': predicted_quality}
    
    async def select_optimal_provider(
        self,
        request_type: str,
        requirements: Dict[str, Any],
        context: GenerationContext
    ) -> Dict[str, Any]:
        """
        Intelligently select the best provider for this specific request
        """
        
        providers = {
            'dalle': {
                'cost': 0.04,
                'speed': 2,
                'quality': 0.95,
                'consistency': 0.9,
                'style_match': self._calculate_style_match('dalle', requirements)
            },
            'stable_diffusion': {
                'cost': 0.002,
                'speed': 5,
                'quality': 0.8,
                'consistency': 0.7,
                'style_match': self._calculate_style_match('sd', requirements)
            },
            'leonardo': {
                'cost': 0.005,
                'speed': 3,
                'quality': 0.85,
                'consistency': 0.75,
                'style_match': self._calculate_style_match('leonardo', requirements)
            }
        }
        
        # Weight factors based on context
        weights = self._calculate_weights(request_type, context)
        
        # Score each provider
        scores = {}
        for provider, metrics in providers.items():
            score = (
                metrics['quality'] * weights['quality'] +
                (1 / metrics['cost']) * weights['cost'] +
                (1 / metrics['speed']) * weights['speed'] +
                metrics['consistency'] * weights['consistency'] +
                metrics['style_match'] * weights['style']
            )
            
            # Apply historical performance
            if provider in context.provider_performance:
                score *= context.provider_performance[provider]
            
            scores[provider] = score
        
        # Select best provider
        best_provider = max(scores, key=scores.get)
        
        return {
            'provider': best_provider,
            'score': scores[best_provider],
            'reasoning': self._explain_selection(best_provider, scores, weights),
            'fallback': sorted(scores, key=scores.get, reverse=True)[1] if len(scores) > 1 else None
        }
    
    async def enhance_prompt(
        self,
        base_prompt: str,
        request_type: str,
        context: GenerationContext
    ) -> str:
        """
        Enhance prompt using SSP understanding and HASR learning
        """
        
        # Use SSP to understand the scene requirements
        if request_type == 'scene':
            scene_binding = self.ssp.bind(base_prompt)
            requirements = scene_binding.get_sprite_requirements()
            
            # Enhance with specific details from SSP analysis
            if requirements.get('emotion'):
                base_prompt += f", {requirements['emotion']} emotion"
            if requirements.get('action'):
                base_prompt += f", {requirements['action']} action"
            if requirements.get('setting'):
                base_prompt += f", {requirements['setting']} setting"
        
        # Use HASR to get learned preferences
        if context.character_profiles:
            character_id = list(context.character_profiles.keys())[0]
            best_combinations = self.hasr.get_best_combinations(character_id)
            
            if best_combinations:
                # Apply learned successful patterns
                top_combo = best_combinations[0]
                if 'style_modifiers' in top_combo:
                    base_prompt += f", {', '.join(top_combo['style_modifiers'])}"
        
        # Get successful patterns from history
        patterns = self.pattern_library.get_successful_patterns(
            request_type,
            context
        )
        
        # Apply learned enhancements
        if patterns:
            pattern_modifiers = self._extract_modifiers_from_patterns(patterns)
            base_prompt += f", {', '.join(pattern_modifiers[:3])}"
        
        # Add quality boosters
        quality_modifiers = self._get_quality_modifiers(request_type)
        base_prompt += f", {', '.join(quality_modifiers)}"
        
        return base_prompt
    
    async def validate_generation(
        self,
        generated_content: Any,
        requirements: Dict[str, Any],
        context: GenerationContext
    ) -> Dict[str, Any]:
        """
        Validate generated content and decide if it meets requirements
        """
        
        validation_results = {
            'passes': True,
            'quality_score': 0.0,
            'issues': [],
            'suggestions': []
        }
        
        # Check for common issues
        if generated_content.get('type') == 'sprite':
            # Check consistency with character
            consistency = await self._check_character_consistency(
                generated_content,
                context.character_profiles
            )
            
            if consistency < 0.7:
                validation_results['passes'] = False
                validation_results['issues'].append('Character consistency too low')
                validation_results['suggestions'].append('Regenerate with stronger reference')
            
            # Check technical quality
            technical_quality = self._check_technical_quality(generated_content)
            validation_results['quality_score'] = technical_quality
            
            if technical_quality < 0.6:
                validation_results['passes'] = False
                validation_results['issues'].append('Technical quality below threshold')
        
        return validation_results
    
    def learn_from_generation(
        self,
        request: Dict[str, Any],
        result: Dict[str, Any],
        context: GenerationContext,
        user_feedback: Optional[float] = None
    ):
        """
        Learn from each generation using HASR and update MPU
        """
        
        # Update HASR with feedback
        if user_feedback:
            sprite_choice = {
                'pose': request.get('pose'),
                'emotion': request.get('emotion'),
                'sprite_id': result.get('sprite_id')
            }
            
            context_data = {
                'scene': request.get('scene', 'general'),
                'emotion': request.get('emotion', 'neutral'),
                'character_id': request.get('character_id')
            }
            
            # HASR reinforcement learning
            self.hasr.reinforce(
                context=context_data,
                sprite_choice=sprite_choice,
                success_score=user_feedback
            )
        
        # Store sprite in MPU if successful
        if result.get('sprite_data') and user_feedback and user_feedback > 0.7:
            from core.mpu import SpriteData
            
            sprite = SpriteData(
                sprite_id=result['sprite_id'],
                character_id=request['character_id'],
                sprite_type=request.get('type', 'generated'),
                pose=request.get('pose', 'standing'),
                emotion=request.get('emotion', 'neutral'),
                url=result['url'],
                metadata={
                    'provider': request.get('provider'),
                    'quality_score': user_feedback,
                    'prompt': request.get('prompt')
                }
            )
            
            # Store in MPU for future retrieval
            self.mpu.store(sprite)
        
        # Update provider performance
        provider = request.get('provider')
        if provider and user_feedback:
            if provider not in context.provider_performance:
                context.provider_performance[provider] = 0.5
            
            # Exponential moving average
            alpha = 0.3
            context.provider_performance[provider] = (
                alpha * user_feedback + 
                (1 - alpha) * context.provider_performance[provider]
            )
        
        # Learn successful patterns
        if user_feedback and user_feedback > 0.8:
            self.pattern_library.add_successful_pattern(
                request_type=request.get('type'),
                prompt=request.get('prompt'),
                settings=request.get('settings'),
                score=user_feedback
            )
        
        # Update quality predictor
        self.quality_predictor.update(
            request,
            result.get('quality_score', user_feedback)
        )
    
    def _calculate_style_match(self, provider: str, requirements: Dict) -> float:
        """Calculate how well provider matches required style"""
        
        style = requirements.get('style', 'general')
        
        style_matches = {
            'dalle': {
                'photorealistic': 0.95,
                'watercolor': 0.9,
                'oil_painting': 0.85,
                'anime': 0.6,
                'pixel_art': 0.4
            },
            'sd': {
                'photorealistic': 0.85,
                'anime': 0.95,
                'pixel_art': 0.8,
                'watercolor': 0.7,
                'oil_painting': 0.75
            },
            'leonardo': {
                'photorealistic': 0.8,
                'fantasy': 0.9,
                'game_art': 0.95,
                'watercolor': 0.75,
                'anime': 0.7
            }
        }
        
        provider_key = 'sd' if provider == 'stable_diffusion' else provider
        return style_matches.get(provider_key, {}).get(style, 0.7)
    
    def _calculate_weights(self, request_type: str, context: GenerationContext) -> Dict[str, float]:
        """Calculate importance weights based on context"""
        
        # Default weights
        weights = {
            'quality': 0.4,
            'cost': 0.2,
            'speed': 0.2,
            'consistency': 0.15,
            'style': 0.05
        }
        
        # Adjust based on request type
        if request_type == 'hero_sprite':
            weights['quality'] = 0.5
            weights['consistency'] = 0.3
        elif request_type == 'background':
            weights['speed'] = 0.3
            weights['cost'] = 0.3
        
        # Adjust based on accumulated cost
        if context.cost_accumulated > 100:
            weights['cost'] = 0.4
            weights['quality'] = 0.3
        
        return weights
    
    def _detect_generation_loop(self, context: GenerationContext) -> bool:
        """Detect if user is requesting similar things repeatedly"""
        
        if len(context.generation_history) < 3:
            return False
        
        recent = context.generation_history[-3:]
        prompts = [h.get('prompt', '') for h in recent]
        
        # Check similarity
        from difflib import SequenceMatcher
        
        similarities = []
        for i in range(len(prompts) - 1):
            ratio = SequenceMatcher(None, prompts[i], prompts[i + 1]).ratio()
            similarities.append(ratio)
        
        return all(s > 0.8 for s in similarities)
    
    def _calculate_similarity(self, sprite: Any, requirements: Dict) -> float:
        """Calculate similarity between existing sprite and requirements"""
        
        similarity = 0.0
        
        # Same character is baseline
        if sprite.character_id == requirements.get('character_id'):
            similarity += 0.4
        
        # Same pose adds significant similarity
        if sprite.pose == requirements.get('pose'):
            similarity += 0.3
        
        # Same emotion
        if sprite.emotion == requirements.get('emotion'):
            similarity += 0.2
        
        # Similar metadata
        if sprite.metadata:
            if sprite.metadata.get('style') == requirements.get('style'):
                similarity += 0.1
        
        return min(similarity, 1.0)
    
    def _extract_modifiers_from_patterns(self, patterns: List[Dict]) -> List[str]:
        """Extract successful modifiers from patterns"""
        
        modifiers = []
        for pattern in patterns:
            prompt = pattern.get('prompt', '')
            # Simple extraction of comma-separated modifiers
            parts = prompt.split(',')
            for part in parts:
                part = part.strip()
                if len(part) < 30 and part not in modifiers:  # Likely a modifier, not full description
                    modifiers.append(part)
        
        return modifiers
    
    def _get_quality_modifiers(self, request_type: str) -> List[str]:
        """Get quality modifiers based on request type"""
        
        if request_type == 'hero_sprite':
            return ['masterpiece', 'best quality', 'highly detailed', 'professional']
        elif request_type == 'background':
            return ['high resolution', 'detailed environment', 'atmospheric']
        elif request_type == 'sprite':
            return ['consistent character', 'clean lines', 'transparent background']
        else:
            return ['high quality', 'detailed']
    
    def _explain_selection(self, provider: str, scores: Dict, weights: Dict) -> str:
        """Explain why a provider was selected"""
        
        reasons = []
        
        if weights['quality'] > 0.4:
            reasons.append("prioritizing quality")
        if weights['cost'] > 0.3:
            reasons.append("optimizing for cost")
        if weights['speed'] > 0.3:
            reasons.append("need for speed")
        
        return f"Selected {provider} because: {', '.join(reasons)}. Score: {scores[provider]:.2f}"
    
    def _determine_modifications(self, existing: Any, requirements: Dict) -> List[str]:
        """Determine what modifications would be needed"""
        
        modifications = []
        
        if existing.emotion != requirements.get('emotion'):
            modifications.append(f"Change emotion from {existing.emotion} to {requirements['emotion']}")
        
        if requirements.get('clothing') and existing.metadata.get('clothing') != requirements['clothing']:
            modifications.append(f"Update clothing to {requirements['clothing']}")
        
        return modifications


class PatternLibrary:
    """Library of successful generation patterns"""
    
    def __init__(self):
        self.patterns = defaultdict(list)
    
    def add_successful_pattern(
        self,
        request_type: str,
        prompt: str,
        settings: Dict,
        score: float
    ):
        """Store successful patterns for reuse"""
        
        pattern = {
            'prompt': prompt,
            'settings': settings,
            'score': score,
            'timestamp': datetime.utcnow(),
            'usage_count': 0
        }
        
        self.patterns[request_type].append(pattern)
        
        # Keep only top 100 patterns per type
        self.patterns[request_type] = sorted(
            self.patterns[request_type],
            key=lambda x: x['score'],
            reverse=True
        )[:100]
    
    def get_successful_patterns(
        self,
        request_type: str,
        context: Any,
        top_n: int = 5
    ) -> List[Dict]:
        """Get most successful patterns for a request type"""
        
        patterns = self.patterns.get(request_type, [])
        
        # Filter by recency (last 30 days)
        recent = [
            p for p in patterns
            if (datetime.utcnow() - p['timestamp']).days < 30
        ]
        
        return recent[:top_n]


class QualityPredictor:
    """Predicts generation quality before making API calls"""
    
    def __init__(self):
        self.history = []
        self.model = None  # Could be a simple ML model
    
    def predict(self, requirements: Dict, provider_performance: Dict) -> float:
        """Predict quality score (0-1) for given requirements"""
        
        # Simple heuristic for now
        base_score = 0.7
        
        # Adjust based on prompt complexity
        prompt = requirements.get('prompt', '')
        if len(prompt) > 200:
            base_score += 0.1  # Detailed prompts often better
        
        if 'reference_image' in requirements:
            base_score += 0.15  # Reference images improve quality
        
        # Adjust based on provider history
        provider = requirements.get('provider', 'dalle')
        if provider in provider_performance:
            base_score *= provider_performance[provider]
        
        return min(base_score, 1.0)
    
    def update(self, request: Dict, actual_quality: float):
        """Update predictor with actual results"""
        
        self.history.append({
            'request': request,
            'predicted': self.predict(request, {}),
            'actual': actual_quality,
            'timestamp': datetime.utcnow()
        })
        
        # Keep last 1000 entries
        self.history = self.history[-1000:]


class CostOptimizer:
    """Optimizes API usage to minimize costs"""
    
    def __init__(self):
        self.cost_history = []
        self.budget_remaining = float('inf')
        self.cost_per_provider = {
            'dalle': 0.04,
            'stable_diffusion': 0.002,
            'leonardo': 0.005,
            'midjourney': 0.01
        }
    
    def should_use_premium(self, importance: float) -> bool:
        """Decide if we should use premium (expensive) generation"""
        
        if self.budget_remaining == float('inf'):
            return importance > 0.7
        
        # Conservative with limited budget
        if self.budget_remaining < 10:
            return importance > 0.9
        
        return importance > 0.75
    
    def track_cost(self, provider: str, count: int = 1):
        """Track API usage costs"""
        
        cost = self.cost_per_provider.get(provider, 0.01) * count
        
        self.cost_history.append({
            'provider': provider,
            'cost': cost,
            'timestamp': datetime.utcnow()
        })
        
        if self.budget_remaining != float('inf'):
            self.budget_remaining -= cost
    
    def get_cost_report(self) -> Dict[str, Any]:
        """Get cost usage report"""
        
        if not self.cost_history:
            return {'total': 0, 'by_provider': {}}
        
        total = sum(h['cost'] for h in self.cost_history)
        by_provider = defaultdict(float)
        
        for h in self.cost_history:
            by_provider[h['provider']] += h['cost']
        
        return {
            'total': total,
            'by_provider': dict(by_provider),
            'budget_remaining': self.budget_remaining,
            'average_per_generation': total / len(self.cost_history)
        }


class CachePredictor:
    """Predicts if we have useful cached content"""
    
    def __init__(self):
        self.cache_hits = []
        self.cache_misses = []
    
    def check(self, requirements: Dict, context: Any) -> Dict[str, Any]:
        """Check if cache likely has useful content"""
        
        # Check MPU for existing sprites
        from services.sprite_generation_service import sprite_generation_service
        
        if requirements.get('type') == 'sprite':
            character_id = requirements.get('character_id')
            pose = requirements.get('pose')
            emotion = requirements.get('emotion')
            
            existing = sprite_generation_service.mpu.query(
                character_id=character_id,
                pose=pose,
                emotion=emotion
            )
            
            if existing:
                return {
                    'confidence': 0.95,
                    'cache_hit': True,
                    'sprite': existing[0]
                }
        
        return {
            'confidence': 0.1,
            'cache_hit': False
        }


class StyleTransferEngine:
    """Maintains style consistency across generations"""
    
    def __init__(self):
        self.style_signatures = {}
    
    def extract_style_signature(self, content: Any) -> Dict[str, Any]:
        """Extract style elements from generated content"""
        
        # This would analyze the image/content for style elements
        return {
            'colors': ['#FF5733', '#33FF57'],  # Dominant colors
            'lighting': 'soft',
            'composition': 'centered',
            'mood': 'cheerful'
        }
    
    def apply_style_transfer(
        self,
        prompt: str,
        source_style: Dict[str, Any]
    ) -> str:
        """Apply style from source to new prompt"""
        
        style_descriptors = []
        
        if source_style.get('lighting'):
            style_descriptors.append(f"{source_style['lighting']} lighting")
        
        if source_style.get('mood'):
            style_descriptors.append(f"{source_style['mood']} mood")
        
        if source_style.get('colors'):
            color_str = ', '.join(source_style['colors'][:2])
            style_descriptors.append(f"color palette: {color_str}")
        
        return f"{prompt}, {', '.join(style_descriptors)}"


# Global instance
lucian_brain = LucianBrain()