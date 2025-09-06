"""
Context Management Service
Maintains conversation and generation context across sessions
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib
from collections import deque
import asyncio


class ContextManager:
    """
    Manages context across user sessions, stories, and generations
    Enables continuity and learning
    """
    
    def __init__(self):
        self.active_contexts = {}  # session_id -> context
        self.user_contexts = {}    # user_id -> historical context
        self.story_contexts = {}   # story_id -> story-specific context
        self.character_memory = CharacterMemory()
        self.generation_queue = GenerationQueue()
        self.relationship_graph = RelationshipGraph()
        
    async def create_session_context(
        self,
        user_id: str,
        session_type: str = 'story_generation'
    ) -> str:
        """
        Create a new session context
        """
        
        session_id = f"session_{hashlib.md5(f'{user_id}{datetime.utcnow()}'.encode()).hexdigest()[:8]}"
        
        # Load user's historical context if exists
        user_history = self.user_contexts.get(user_id, {})
        
        context = {
            'session_id': session_id,
            'user_id': user_id,
            'session_type': session_type,
            'started_at': datetime.utcnow().isoformat(),
            'generation_count': 0,
            'total_cost': 0.0,
            'characters': {},
            'stories': [],
            'preferences': user_history.get('preferences', {}),
            'quality_history': user_history.get('quality_history', []),
            'provider_preferences': user_history.get('provider_preferences', {}),
            'style_consistency': user_history.get('style_consistency', {}),
            'interaction_history': deque(maxlen=50)  # Last 50 interactions
        }
        
        self.active_contexts[session_id] = context
        
        return session_id
    
    async def update_context(
        self,
        session_id: str,
        update_type: str,
        data: Dict[str, Any]
    ):
        """
        Update session context with new information
        """
        
        if session_id not in self.active_contexts:
            raise ValueError(f"Session {session_id} not found")
        
        context = self.active_contexts[session_id]
        
        if update_type == 'character_added':
            character_id = data['character_id']
            context['characters'][character_id] = {
                'name': data['name'],
                'sprites_generated': 0,
                'reference_photos': data.get('reference_photos', []),
                'personality': data.get('personality', {}),
                'relationships': data.get('relationships', []),
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Update character memory
            await self.character_memory.store_character(
                character_id,
                data
            )
            
        elif update_type == 'generation_completed':
            context['generation_count'] += 1
            context['total_cost'] += data.get('cost', 0)
            
            # Track quality
            if 'quality_score' in data:
                context['quality_history'].append(data['quality_score'])
            
            # Track provider performance
            provider = data.get('provider')
            if provider:
                if provider not in context['provider_preferences']:
                    context['provider_preferences'][provider] = []
                context['provider_preferences'][provider].append(
                    data.get('quality_score', 0.7)
                )
        
        elif update_type == 'story_created':
            context['stories'].append({
                'story_id': data['story_id'],
                'title': data['title'],
                'scenes': data.get('scenes', []),
                'characters_used': data.get('characters', []),
                'created_at': datetime.utcnow().isoformat()
            })
            
            # Create story-specific context
            await self._create_story_context(data['story_id'], data)
        
        elif update_type == 'interaction':
            context['interaction_history'].append({
                'type': data['type'],
                'input': data.get('input'),
                'output': data.get('output'),
                'timestamp': datetime.utcnow().isoformat()
            })
    
    async def get_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get current session context
        """
        
        if session_id not in self.active_contexts:
            raise ValueError(f"Session {session_id} not found")
        
        return self.active_contexts[session_id]
    
    async def get_character_context(
        self,
        character_id: str,
        include_relationships: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive context for a character
        """
        
        character_data = await self.character_memory.get_character(character_id)
        
        if not character_data:
            return {}
        
        context = {
            'character_id': character_id,
            'profile': character_data,
            'generation_history': await self.character_memory.get_generation_history(character_id),
            'style_signature': await self.character_memory.get_style_signature(character_id),
            'sprites_available': await self._get_available_sprites(character_id)
        }
        
        if include_relationships:
            context['relationships'] = await self.relationship_graph.get_relationships(character_id)
        
        return context
    
    async def save_user_context(self, user_id: str, session_id: str):
        """
        Save session context to user's historical context
        """
        
        if session_id not in self.active_contexts:
            return
        
        session_context = self.active_contexts[session_id]
        
        # Initialize user context if doesn't exist
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {
                'user_id': user_id,
                'first_seen': datetime.utcnow().isoformat(),
                'preferences': {},
                'quality_history': [],
                'provider_preferences': {},
                'style_consistency': {},
                'total_generations': 0,
                'total_cost': 0.0
            }
        
        user_context = self.user_contexts[user_id]
        
        # Merge session data into user context
        user_context['total_generations'] += session_context['generation_count']
        user_context['total_cost'] += session_context['total_cost']
        
        # Update preferences based on session
        if session_context['quality_history']:
            avg_quality = sum(session_context['quality_history']) / len(session_context['quality_history'])
            if avg_quality > 0.8:
                # Session was successful, save preferences
                user_context['preferences'].update(session_context.get('preferences', {}))
        
        # Update provider preferences
        for provider, scores in session_context['provider_preferences'].items():
            if provider not in user_context['provider_preferences']:
                user_context['provider_preferences'][provider] = []
            user_context['provider_preferences'][provider].extend(scores)
            # Keep only last 100 scores
            user_context['provider_preferences'][provider] = user_context['provider_preferences'][provider][-100:]
        
        user_context['last_seen'] = datetime.utcnow().isoformat()
    
    async def _create_story_context(self, story_id: str, story_data: Dict):
        """
        Create context specific to a story
        """
        
        self.story_contexts[story_id] = {
            'story_id': story_id,
            'title': story_data['title'],
            'characters': story_data.get('characters', []),
            'scenes': story_data.get('scenes', []),
            'theme': story_data.get('theme'),
            'mood': story_data.get('mood'),
            'setting': story_data.get('setting'),
            'style_guide': story_data.get('style_guide', {}),
            'created_at': datetime.utcnow().isoformat()
        }
    
    async def _get_available_sprites(self, character_id: str) -> Dict[str, List[str]]:
        """
        Get available sprites for a character
        """
        
        from services.sprite_generation_service import sprite_generation_service
        
        sprites = sprite_generation_service.mpu.query(character_id=character_id)
        
        organized = {}
        for sprite in sprites:
            pose = sprite.pose
            if pose not in organized:
                organized[pose] = []
            organized[pose].append(sprite.emotion)
        
        return organized
    
    def cleanup_old_contexts(self, max_age_hours: int = 24):
        """
        Clean up old inactive contexts
        """
        
        now = datetime.utcnow()
        to_remove = []
        
        for session_id, context in self.active_contexts.items():
            started_at = datetime.fromisoformat(context['started_at'])
            age = (now - started_at).total_seconds() / 3600
            
            if age > max_age_hours:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            # Save to user context before removing
            user_id = self.active_contexts[session_id]['user_id']
            asyncio.create_task(self.save_user_context(user_id, session_id))
            
            del self.active_contexts[session_id]


class CharacterMemory:
    """
    Maintains detailed memory for each character
    """
    
    def __init__(self):
        self.characters = {}
        self.generation_history = {}  # character_id -> list of generations
        self.style_signatures = {}    # character_id -> style elements
    
    async def store_character(self, character_id: str, data: Dict):
        """
        Store character information
        """
        
        self.characters[character_id] = {
            'character_id': character_id,
            'name': data['name'],
            'profile': data,
            'created_at': datetime.utcnow().isoformat(),
            'last_updated': datetime.utcnow().isoformat()
        }
        
        if character_id not in self.generation_history:
            self.generation_history[character_id] = []
    
    async def get_character(self, character_id: str) -> Optional[Dict]:
        """
        Retrieve character information
        """
        
        return self.characters.get(character_id)
    
    async def add_generation(
        self,
        character_id: str,
        generation_data: Dict
    ):
        """
        Add a generation to character's history
        """
        
        if character_id not in self.generation_history:
            self.generation_history[character_id] = []
        
        self.generation_history[character_id].append({
            'type': generation_data['type'],
            'prompt': generation_data.get('prompt'),
            'provider': generation_data.get('provider'),
            'quality_score': generation_data.get('quality_score'),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Keep only last 100 generations
        self.generation_history[character_id] = self.generation_history[character_id][-100:]
        
        # Update style signature if high quality
        if generation_data.get('quality_score', 0) > 0.8:
            await self._update_style_signature(character_id, generation_data)
    
    async def get_generation_history(
        self,
        character_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent generation history for character
        """
        
        history = self.generation_history.get(character_id, [])
        return history[-limit:]
    
    async def get_style_signature(self, character_id: str) -> Dict[str, Any]:
        """
        Get learned style signature for character
        """
        
        return self.style_signatures.get(character_id, {})
    
    async def _update_style_signature(
        self,
        character_id: str,
        generation_data: Dict
    ):
        """
        Update character's style signature based on successful generation
        """
        
        if character_id not in self.style_signatures:
            self.style_signatures[character_id] = {
                'colors': [],
                'styles': [],
                'modifiers': [],
                'successful_prompts': []
            }
        
        signature = self.style_signatures[character_id]
        
        # Extract style elements from prompt
        prompt = generation_data.get('prompt', '')
        
        # This would use NLP to extract style elements
        # For now, simple keyword extraction
        style_keywords = ['watercolor', 'anime', 'realistic', 'cartoon', 'fantasy']
        for keyword in style_keywords:
            if keyword in prompt.lower():
                if keyword not in signature['styles']:
                    signature['styles'].append(keyword)
        
        # Store successful prompt patterns
        if len(signature['successful_prompts']) < 20:
            signature['successful_prompts'].append(prompt)


class GenerationQueue:
    """
    Manages generation request queue with priority
    """
    
    def __init__(self):
        self.queue = asyncio.PriorityQueue()
        self.processing = {}
        
    async def add_request(
        self,
        request_type: str,
        data: Dict,
        priority: int = 5
    ) -> str:
        """
        Add generation request to queue
        Priority: 1 (highest) to 10 (lowest)
        """
        
        request_id = f"req_{hashlib.md5(json.dumps(data).encode()).hexdigest()[:8]}"
        
        request = {
            'request_id': request_id,
            'type': request_type,
            'data': data,
            'priority': priority,
            'queued_at': datetime.utcnow().isoformat(),
            'status': 'queued'
        }
        
        await self.queue.put((priority, request_id, request))
        
        return request_id
    
    async def get_next_request(self) -> Optional[Dict]:
        """
        Get next request from queue
        """
        
        if self.queue.empty():
            return None
        
        priority, request_id, request = await self.queue.get()
        
        request['status'] = 'processing'
        request['started_at'] = datetime.utcnow().isoformat()
        
        self.processing[request_id] = request
        
        return request
    
    async def complete_request(self, request_id: str, result: Any):
        """
        Mark request as completed
        """
        
        if request_id in self.processing:
            request = self.processing[request_id]
            request['status'] = 'completed'
            request['completed_at'] = datetime.utcnow().isoformat()
            request['result'] = result
            
            del self.processing[request_id]


class RelationshipGraph:
    """
    Tracks relationships between characters
    """
    
    def __init__(self):
        self.relationships = {}  # character_id -> list of relationships
        
    async def add_relationship(
        self,
        character1_id: str,
        character2_id: str,
        relationship_type: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add relationship between characters
        """
        
        if character1_id not in self.relationships:
            self.relationships[character1_id] = []
        
        if character2_id not in self.relationships:
            self.relationships[character2_id] = []
        
        rel_data = {
            'other_character': character2_id,
            'type': relationship_type,
            'metadata': metadata or {},
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Add bidirectional relationship
        self.relationships[character1_id].append(rel_data)
        
        rel_data_reverse = rel_data.copy()
        rel_data_reverse['other_character'] = character1_id
        self.relationships[character2_id].append(rel_data_reverse)
    
    async def get_relationships(self, character_id: str) -> List[Dict]:
        """
        Get all relationships for a character
        """
        
        return self.relationships.get(character_id, [])
    
    async def get_related_characters(
        self,
        character_id: str,
        relationship_type: Optional[str] = None
    ) -> List[str]:
        """
        Get IDs of related characters
        """
        
        relationships = self.relationships.get(character_id, [])
        
        if relationship_type:
            relationships = [r for r in relationships if r['type'] == relationship_type]
        
        return [r['other_character'] for r in relationships]


# Global instance
context_manager = ContextManager()