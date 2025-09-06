"""
HASR (Hebbian-Analog Symbolic Reinforcement) - Adapted for Sprite Learning
From LucianOS Core - Optimized for production sprite selection
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
from collections import defaultdict

class HASR:
    """
    Hebbian-Analog Symbolic Reinforcement for Sprite Optimization
    
    Learns which sprite combinations work best for different story contexts.
    Reinforces successful sprite selections and weakens poor choices.
    
    Example usage:
        hasr = HASR()
        
        # Reinforce a successful sprite combination
        hasr.reinforce(
            context={'scene': 'bedroom', 'emotion': 'worried'},
            sprite_choice={'pose': 'sitting', 'emotion': 'worried'},
            success_score=0.9
        )
        
        # Get optimized sprite suggestion
        best_sprite = hasr.suggest_sprite(
            context={'scene': 'bedroom', 'emotion': 'worried'},
            available_sprites=sprite_list
        )
    """
    
    def __init__(self, learning_rate: float = 0.1, decay_rate: float = 0.95):
        """
        Initialize HASR with learning parameters
        
        Args:
            learning_rate: How quickly to adapt weights (0.0-1.0)
            decay_rate: How quickly old associations decay (0.0-1.0)
        """
        self.learning_rate = learning_rate
        self.decay_rate = decay_rate
        
        # Weight matrices for different associations
        self.weights = {
            'scene_to_pose': defaultdict(lambda: defaultdict(float)),
            'emotion_to_sprite': defaultdict(lambda: defaultdict(float)),
            'action_to_pose': defaultdict(lambda: defaultdict(float)),
            'time_to_lighting': defaultdict(lambda: defaultdict(float)),
            'character_preferences': defaultdict(lambda: defaultdict(float))
        }
        
        # Success history for tracking performance
        self.history = []
        
        # Cache for fast lookups
        self.cache = {}
        
    def reinforce(self, context: Dict[str, Any], sprite_choice: Dict[str, Any], 
                  success_score: float):
        """
        Reinforce a sprite selection based on success
        
        Args:
            context: The story context (scene, emotion, action, etc.)
            sprite_choice: The sprite that was chosen
            success_score: How successful this choice was (0.0-1.0)
        """
        # Update scene-to-pose weights
        if 'scene' in context and 'pose' in sprite_choice:
            old_weight = self.weights['scene_to_pose'][context['scene']][sprite_choice['pose']]
            new_weight = old_weight + self.learning_rate * (success_score - old_weight)
            self.weights['scene_to_pose'][context['scene']][sprite_choice['pose']] = new_weight
        
        # Update emotion-to-sprite weights
        if 'emotion' in context and 'emotion' in sprite_choice:
            emotion_match = 1.0 if context['emotion'] == sprite_choice['emotion'] else 0.5
            combined_score = success_score * emotion_match
            
            old_weight = self.weights['emotion_to_sprite'][context['emotion']][sprite_choice['emotion']]
            new_weight = old_weight + self.learning_rate * (combined_score - old_weight)
            self.weights['emotion_to_sprite'][context['emotion']][sprite_choice['emotion']] = new_weight
        
        # Update action-to-pose weights
        if 'action' in context and 'pose' in sprite_choice:
            old_weight = self.weights['action_to_pose'][context['action']][sprite_choice['pose']]
            new_weight = old_weight + self.learning_rate * (success_score - old_weight)
            self.weights['action_to_pose'][context['action']][sprite_choice['pose']] = new_weight
        
        # Update character-specific preferences
        if 'character_id' in context:
            char_id = context['character_id']
            sprite_key = f"{sprite_choice.get('pose', 'unknown')}_{sprite_choice.get('emotion', 'unknown')}"
            
            old_weight = self.weights['character_preferences'][char_id][sprite_key]
            new_weight = old_weight + self.learning_rate * (success_score - old_weight)
            self.weights['character_preferences'][char_id][sprite_key] = new_weight
        
        # Record in history
        self.history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'context': context,
            'sprite_choice': sprite_choice,
            'success_score': success_score
        })
        
        # Clear cache as weights have changed
        self.cache.clear()
        
        # Apply decay to all weights
        self._apply_decay()
    
    def suggest_sprite(self, context: Dict[str, Any], 
                      available_sprites: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Suggest the best sprite based on learned weights
        
        Args:
            context: Current story context
            available_sprites: List of available sprite options
            
        Returns:
            Best sprite choice or None if no sprites available
        """
        if not available_sprites:
            return None
        
        # Score each available sprite
        scores = []
        for sprite in available_sprites:
            score = self._calculate_sprite_score(context, sprite)
            scores.append((sprite, score))
        
        # Sort by score and return the best
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores[0][0] if scores else None
    
    def _calculate_sprite_score(self, context: Dict[str, Any], 
                                sprite: Dict[str, Any]) -> float:
        """
        Calculate a score for a sprite given the context
        
        Args:
            context: Story context
            sprite: Sprite to score
            
        Returns:
            Score value (higher is better)
        """
        score = 0.0
        weight_count = 0
        
        # Check scene-to-pose weight
        if 'scene' in context and 'pose' in sprite:
            weight = self.weights['scene_to_pose'][context['scene']].get(sprite['pose'], 0.0)
            score += weight
            weight_count += 1
        
        # Check emotion matching
        if 'emotion' in context and 'emotion' in sprite:
            # Exact match gets bonus
            if context['emotion'] == sprite['emotion']:
                score += 1.0
            
            # Also check learned weight
            weight = self.weights['emotion_to_sprite'][context['emotion']].get(sprite['emotion'], 0.0)
            score += weight
            weight_count += 1
        
        # Check action-to-pose weight
        if 'action' in context and 'pose' in sprite:
            weight = self.weights['action_to_pose'][context['action']].get(sprite['pose'], 0.0)
            score += weight
            weight_count += 1
        
        # Check character-specific preferences
        if 'character_id' in context:
            char_id = context['character_id']
            sprite_key = f"{sprite.get('pose', 'unknown')}_{sprite.get('emotion', 'unknown')}"
            weight = self.weights['character_preferences'][char_id].get(sprite_key, 0.0)
            score += weight * 2  # Character preferences are more important
            weight_count += 2
        
        # Normalize score
        if weight_count > 0:
            score = score / weight_count
        
        return score
    
    def get_best_combinations(self, character_id: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Get the best sprite combinations for a character
        
        Args:
            character_id: Character to get combinations for
            top_n: Number of top combinations to return
            
        Returns:
            List of (sprite_key, weight) tuples
        """
        if character_id not in self.weights['character_preferences']:
            return []
        
        prefs = self.weights['character_preferences'][character_id]
        sorted_prefs = sorted(prefs.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_prefs[:top_n]
    
    def _apply_decay(self):
        """Apply decay to all weights to forget old associations"""
        for weight_type in self.weights:
            for key1 in self.weights[weight_type]:
                for key2 in self.weights[weight_type][key1]:
                    self.weights[weight_type][key1][key2] *= self.decay_rate
    
    def save_weights(self, filepath: str):
        """
        Save weights to a file
        
        Args:
            filepath: Path to save weights
        """
        data = {
            'weights': {k: dict(v) for k, v in self.weights.items()},
            'learning_rate': self.learning_rate,
            'decay_rate': self.decay_rate,
            'history_size': len(self.history)
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load_weights(self, filepath: str):
        """
        Load weights from a file
        
        Args:
            filepath: Path to load weights from
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Convert back to defaultdicts
        for weight_type, weights in data['weights'].items():
            self.weights[weight_type] = defaultdict(lambda: defaultdict(float))
            for key1, inner_dict in weights.items():
                for key2, value in inner_dict.items():
                    self.weights[weight_type][key1][key2] = value
        
        self.learning_rate = data.get('learning_rate', 0.1)
        self.decay_rate = data.get('decay_rate', 0.95)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics"""
        total_weights = sum(
            len(inner) for weight_dict in self.weights.values() 
            for inner in weight_dict.values()
        )
        
        # Calculate average success from recent history
        recent_history = self.history[-100:] if self.history else []
        avg_success = np.mean([h['success_score'] for h in recent_history]) if recent_history else 0.0
        
        return {
            'total_weights': total_weights,
            'history_size': len(self.history),
            'average_recent_success': avg_success,
            'learning_rate': self.learning_rate,
            'decay_rate': self.decay_rate,
            'weight_types': list(self.weights.keys())
        }
    
    def optimize_for_engagement(self, story_id: str, engagement_metrics: Dict[str, float]):
        """
        Optimize based on story engagement metrics
        
        Args:
            story_id: Story identifier
            engagement_metrics: Dictionary of metrics like completion_rate, likes, etc.
        """
        # Calculate overall success score from engagement
        success_score = self._calculate_engagement_score(engagement_metrics)
        
        # Find all sprite choices used in this story from history
        story_choices = [h for h in self.history if h.get('story_id') == story_id]
        
        # Reinforce all choices based on engagement
        for choice in story_choices:
            adjusted_score = choice['success_score'] * 0.3 + success_score * 0.7
            self.reinforce(choice['context'], choice['sprite_choice'], adjusted_score)
    
    def _calculate_engagement_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall score from engagement metrics"""
        # Weighted combination of different metrics
        score = 0.0
        
        if 'completion_rate' in metrics:
            score += metrics['completion_rate'] * 0.4
        
        if 'like_rate' in metrics:
            score += metrics['like_rate'] * 0.3
        
        if 'share_rate' in metrics:
            score += metrics['share_rate'] * 0.2
        
        if 'replay_rate' in metrics:
            score += metrics['replay_rate'] * 0.1
        
        return min(1.0, score)  # Cap at 1.0


# Example usage for testing
if __name__ == "__main__":
    # Initialize HASR
    hasr = HASR(learning_rate=0.15)
    
    # Simulate learning from successful sprite choices
    context = {
        'scene': 'bedroom',
        'emotion': 'worried',
        'action': 'sitting',
        'character_id': 'sunshine_123'
    }
    
    sprite_choice = {
        'pose': 'sitting',
        'emotion': 'worried',
        'sprite_id': 'sprite_001'
    }
    
    # Reinforce this as a good choice
    hasr.reinforce(context, sprite_choice, success_score=0.9)
    
    # Get suggestion for similar context
    available_sprites = [
        {'pose': 'sitting', 'emotion': 'worried', 'id': 'sprite_001'},
        {'pose': 'standing', 'emotion': 'happy', 'id': 'sprite_002'},
        {'pose': 'sitting', 'emotion': 'neutral', 'id': 'sprite_003'}
    ]
    
    best_sprite = hasr.suggest_sprite(context, available_sprites)
    print(f"Best sprite suggestion: {best_sprite}")
    
    # Get statistics
    stats = hasr.get_statistics()
    print(f"HASR Statistics: {stats}")
