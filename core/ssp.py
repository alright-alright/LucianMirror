"""
SSP (Symbolic Sense Processor) - Adapted for Sprite Scene Analysis
From LucianOS Core - Production-ready for story parsing
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json

@dataclass
class SceneBinding:
    """Represents a parsed scene with sprite requirements"""
    text: str
    characters: List[Dict[str, str]]  # [{'id': 'sunshine_123', 'name': 'Lucy'}]
    actions: List[str]
    emotions: List[str]
    objects: List[str]
    setting: str
    time_of_day: str
    weather: Optional[str] = None
    
    def get_primary_character(self) -> Optional[Dict[str, str]]:
        """Get the main character in this scene"""
        return self.characters[0] if self.characters else None
    
    def get_sprite_requirements(self) -> Dict[str, Any]:
        """Extract sprite requirements for this scene"""
        primary_char = self.get_primary_character()
        
        return {
            'character_id': primary_char['id'] if primary_char else None,
            'pose': self._determine_pose(),
            'emotion': self._determine_emotion(),
            'additional_characters': self.characters[1:],
            'objects_needed': self.objects,
            'background': {
                'setting': self.setting,
                'time': self.time_of_day,
                'weather': self.weather
            }
        }
    
    def _determine_pose(self) -> str:
        """Determine the primary pose needed"""
        action_to_pose = {
            'sitting': 'sitting',
            'standing': 'standing',
            'walking': 'walking',
            'running': 'running',
            'jumping': 'jumping',
            'sleeping': 'sleeping',
            'reading': 'sitting',
            'eating': 'sitting',
            'playing': 'standing',
            'hugging': 'hugging',
            'waving': 'waving'
        }
        
        for action in self.actions:
            for key, pose in action_to_pose.items():
                if key in action.lower():
                    return pose
        
        return 'standing'  # default
    
    def _determine_emotion(self) -> str:
        """Determine the primary emotion needed"""
        if self.emotions:
            return self.emotions[0]
        
        # Infer from text
        emotion_keywords = {
            'happy': ['smiled', 'laughed', 'excited', 'joy', 'cheerful'],
            'sad': ['cried', 'tears', 'upset', 'unhappy', 'depressed'],
            'worried': ['worried', 'anxious', 'nervous', 'scared', 'afraid'],
            'angry': ['angry', 'mad', 'frustrated', 'annoyed'],
            'surprised': ['surprised', 'amazed', 'shocked', 'astonished'],
            'neutral': ['looked', 'saw', 'went', 'was']
        }
        
        text_lower = self.text.lower()
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return emotion
        
        return 'neutral'


class SSP:
    """
    Symbolic Sense Processor for Story-to-Sprite Binding
    
    Analyzes story text and determines which sprites are needed.
    Creates semantic bindings between narrative and visual elements.
    
    Example usage:
        ssp = SSP()
        
        # Configure with character info
        ssp.set_character_mapping({
            'Lucy': 'sunshine_123',
            'Mom': 'family_456',
            'Fluffy': 'pet_789'
        })
        
        # Parse a story scene
        binding = ssp.bind("Lucy sat on her bed feeling worried about the dark")
        
        # Get sprite requirements
        requirements = binding.get_sprite_requirements()
        # Returns: {'character_id': 'sunshine_123', 'pose': 'sitting', 'emotion': 'worried', ...}
    """
    
    def __init__(self):
        """Initialize the SSP"""
        self.character_mapping = {}  # Name to ID mapping
        self.bindings = []  # Store all bindings
        self.emotion_lexicon = self._load_emotion_lexicon()
        self.action_lexicon = self._load_action_lexicon()
        self.setting_lexicon = self._load_setting_lexicon()
    
    def set_character_mapping(self, mapping: Dict[str, str]):
        """
        Set the character name to ID mapping
        
        Args:
            mapping: Dictionary mapping character names to IDs
                    e.g., {'Lucy': 'sunshine_123', 'Mom': 'family_456'}
        """
        self.character_mapping = mapping
    
    def bind(self, text: str) -> SceneBinding:
        """
        Parse text and create a scene binding
        
        Args:
            text: Scene description text
            
        Returns:
            SceneBinding object with extracted information
        """
        binding = SceneBinding(
            text=text,
            characters=self._extract_characters(text),
            actions=self._extract_actions(text),
            emotions=self._extract_emotions(text),
            objects=self._extract_objects(text),
            setting=self._extract_setting(text),
            time_of_day=self._extract_time(text),
            weather=self._extract_weather(text)
        )
        
        self.bindings.append(binding)
        return binding
    
    def parse_story(self, story_text: str) -> List[SceneBinding]:
        """
        Parse an entire story into scene bindings
        
        Args:
            story_text: Complete story text
            
        Returns:
            List of SceneBinding objects, one per scene
        """
        # Split story into scenes (paragraphs or sentences)
        scenes = self._split_into_scenes(story_text)
        
        bindings = []
        for scene_text in scenes:
            if scene_text.strip():
                binding = self.bind(scene_text)
                bindings.append(binding)
        
        return bindings
    
    def _extract_characters(self, text: str) -> List[Dict[str, str]]:
        """Extract character references from text"""
        characters = []
        
        for name, char_id in self.character_mapping.items():
            if name.lower() in text.lower():
                characters.append({
                    'id': char_id,
                    'name': name
                })
        
        # Also look for pronouns if we have a primary character
        if not characters and self.character_mapping:
            # Check for pronouns that might refer to the main character
            pronouns = ['she', 'he', 'they']
            if any(pronoun in text.lower() for pronoun in pronouns):
                # Assume it's the first character in our mapping (main character)
                first_char = list(self.character_mapping.items())[0]
                characters.append({
                    'id': first_char[1],
                    'name': first_char[0]
                })
        
        return characters
    
    def _extract_actions(self, text: str) -> List[str]:
        """Extract action words from text"""
        actions = []
        
        # Common action patterns
        action_patterns = [
            r'\b(sat|sitting|sits)\b',
            r'\b(stood|standing|stands)\b',
            r'\b(walked|walking|walks)\b',
            r'\b(ran|running|runs)\b',
            r'\b(jumped|jumping|jumps)\b',
            r'\b(slept|sleeping|sleeps)\b',
            r'\b(read|reading|reads)\b',
            r'\b(ate|eating|eats)\b',
            r'\b(played|playing|plays)\b',
            r'\b(hugged|hugging|hugs)\b',
            r'\b(waved|waving|waves)\b',
            r'\b(looked|looking|looks)\b',
            r'\b(smiled|smiling|smiles)\b',
            r'\b(cried|crying|cries)\b'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            actions.extend(matches)
        
        return list(set(actions))  # Remove duplicates
    
    def _extract_emotions(self, text: str) -> List[str]:
        """Extract emotional states from text"""
        emotions = []
        
        for emotion, keywords in self.emotion_lexicon.items():
            if any(keyword in text.lower() for keyword in keywords):
                emotions.append(emotion)
        
        return emotions
    
    def _extract_objects(self, text: str) -> List[str]:
        """Extract objects mentioned in text"""
        objects = []
        
        # Common story objects
        object_patterns = [
            r'\b(bed|beds)\b',
            r'\b(chair|chairs)\b',
            r'\b(table|tables)\b',
            r'\b(book|books)\b',
            r'\b(toy|toys)\b',
            r'\b(ball|balls)\b',
            r'\b(teddy bear|teddy|bear)\b',
            r'\b(bicycle|bike)\b',
            r'\b(car|cars)\b',
            r'\b(tree|trees)\b',
            r'\b(flower|flowers)\b',
            r'\b(door|doors)\b',
            r'\b(window|windows)\b',
            r'\b(lamp|lamps|light|lights)\b'
        ]
        
        for pattern in object_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Extract just the base object name
                obj = pattern.replace(r'\b', '').replace('|', '/').strip('()')
                objects.append(obj.split('|')[0])  # Take first variant
        
        return list(set(objects))
    
    def _extract_setting(self, text: str) -> str:
        """Extract location/setting from text"""
        settings = {
            'bedroom': ['bedroom', 'bed', 'pillow', 'blanket'],
            'kitchen': ['kitchen', 'table', 'eating', 'breakfast', 'dinner'],
            'living_room': ['living room', 'couch', 'sofa', 'tv', 'television'],
            'bathroom': ['bathroom', 'bath', 'shower', 'brush'],
            'garden': ['garden', 'flowers', 'grass', 'outside'],
            'park': ['park', 'playground', 'swing', 'slide'],
            'school': ['school', 'classroom', 'teacher', 'desk'],
            'forest': ['forest', 'trees', 'woods', 'path'],
            'beach': ['beach', 'ocean', 'sand', 'waves'],
            'street': ['street', 'road', 'sidewalk', 'cars']
        }
        
        text_lower = text.lower()
        for setting, keywords in settings.items():
            if any(keyword in text_lower for keyword in keywords):
                return setting
        
        return 'generic'  # Default setting
    
    def _extract_time(self, text: str) -> str:
        """Extract time of day from text"""
        time_indicators = {
            'morning': ['morning', 'sunrise', 'dawn', 'breakfast'],
            'afternoon': ['afternoon', 'lunch', 'noon'],
            'evening': ['evening', 'sunset', 'dusk', 'dinner'],
            'night': ['night', 'dark', 'bedtime', 'moon', 'stars']
        }
        
        text_lower = text.lower()
        for time, keywords in time_indicators.items():
            if any(keyword in text_lower for keyword in keywords):
                return time
        
        return 'day'  # Default
    
    def _extract_weather(self, text: str) -> Optional[str]:
        """Extract weather conditions from text"""
        weather_keywords = {
            'sunny': ['sunny', 'sun', 'bright'],
            'rainy': ['rain', 'rainy', 'raining', 'wet'],
            'cloudy': ['cloudy', 'clouds', 'overcast'],
            'snowy': ['snow', 'snowy', 'snowing'],
            'stormy': ['storm', 'thunder', 'lightning'],
            'windy': ['wind', 'windy', 'breeze']
        }
        
        text_lower = text.lower()
        for weather, keywords in weather_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return weather
        
        return None  # No specific weather mentioned
    
    def _split_into_scenes(self, story_text: str) -> List[str]:
        """Split story text into individual scenes"""
        # Try splitting by double newlines first (paragraphs)
        scenes = story_text.split('\n\n')
        
        # If no paragraphs, split by sentences
        if len(scenes) == 1:
            # Simple sentence splitting (can be improved)
            scenes = re.split(r'[.!?]+\s+', story_text)
        
        return [s.strip() for s in scenes if s.strip()]
    
    def _load_emotion_lexicon(self) -> Dict[str, List[str]]:
        """Load emotion keywords"""
        return {
            'happy': ['happy', 'joy', 'smile', 'laugh', 'excited', 'cheerful', 'delighted'],
            'sad': ['sad', 'cry', 'tears', 'upset', 'unhappy', 'miserable', 'depressed'],
            'worried': ['worried', 'anxious', 'nervous', 'scared', 'afraid', 'frightened', 'fear'],
            'angry': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'rage'],
            'surprised': ['surprised', 'amazed', 'shocked', 'astonished', 'wondered'],
            'excited': ['excited', 'thrilled', 'eager', 'enthusiastic'],
            'calm': ['calm', 'peaceful', 'relaxed', 'serene'],
            'confused': ['confused', 'puzzled', 'bewildered', 'perplexed']
        }
    
    def _load_action_lexicon(self) -> Dict[str, List[str]]:
        """Load action keywords"""
        return {
            'movement': ['walk', 'run', 'jump', 'skip', 'hop', 'crawl'],
            'rest': ['sit', 'stand', 'lie', 'sleep', 'rest'],
            'interaction': ['talk', 'hug', 'kiss', 'wave', 'shake hands'],
            'activity': ['play', 'read', 'write', 'draw', 'paint', 'sing', 'dance']
        }
    
    def _load_setting_lexicon(self) -> Dict[str, List[str]]:
        """Load setting keywords"""
        return {
            'indoor': ['room', 'house', 'home', 'inside', 'building'],
            'outdoor': ['outside', 'garden', 'park', 'street', 'forest', 'beach'],
            'nature': ['tree', 'grass', 'flower', 'mountain', 'river', 'lake']
        }
    
    def optimize_bindings(self, hasr):
        """
        Use HASR to optimize scene bindings based on what worked before
        
        Args:
            hasr: HASR instance for learning
        """
        # This would integrate with HASR to learn optimal sprite selections
        pass


# Example usage for testing
if __name__ == "__main__":
    # Initialize SSP
    ssp = SSP()
    
    # Set character mapping
    ssp.set_character_mapping({
        'Lucy': 'sunshine_123',
        'Mom': 'family_456',
        'Fluffy': 'pet_789'
    })
    
    # Parse a scene
    scene_text = "Lucy sat on her bed feeling worried about the dark night outside."
    binding = ssp.bind(scene_text)
    
    print(f"Scene: {binding.text}")
    print(f"Characters: {binding.characters}")
    print(f"Actions: {binding.actions}")
    print(f"Emotions: {binding.emotions}")
    print(f"Setting: {binding.setting}")
    print(f"Time: {binding.time_of_day}")
    
    # Get sprite requirements
    requirements = binding.get_sprite_requirements()
    print(f"\nSprite Requirements: {requirements}")
