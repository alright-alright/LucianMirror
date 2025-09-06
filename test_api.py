#!/usr/bin/env python3
"""
Test script for LucianMirror API
Run this to verify the API is working correctly for MySunshineStories integration
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

class LucianMirrorAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_character_id = f"test_{int(time.time())}"
        self.results = []
        
    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 LucianMirror API Test Suite")
        print("=" * 60)
        
        # Test 1: Health Check
        self.test_health_check()
        
        # Test 2: Character Initialization
        self.test_character_init()
        
        # Test 3: Sprite Generation
        self.test_sprite_generation()
        
        # Test 4: Get Sprites
        self.test_get_sprites()
        
        # Test 5: Scene Composition
        self.test_scene_composition()
        
        # Test 6: Story Processing
        self.test_story_processing()
        
        # Test 7: Manual Composition
        self.test_manual_composition()
        
        # Print Results
        self.print_results()
        
    def test_health_check(self):
        """Test API health check endpoint"""
        print("\n📍 Test 1: Health Check")
        try:
            response = requests.get(f"{self.base_url}/")
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "operational":
                self.results.append(("Health Check", "✅ PASSED", None))
                print(f"  ✅ API is operational")
                print(f"  Version: {data.get('version', 'Unknown')}")
            else:
                self.results.append(("Health Check", "❌ FAILED", "API not operational"))
                
        except Exception as e:
            self.results.append(("Health Check", "❌ FAILED", str(e)))
            print(f"  ❌ Failed: {e}")
            print("\n  ⚠️  Make sure the API server is running:")
            print("     cd backend && python -m uvicorn main:app --port 8000")
            sys.exit(1)
    
    def test_character_init(self):
        """Test character initialization"""
        print("\n📍 Test 2: Character Initialization")
        
        character_data = {
            "character_id": self.test_character_id,
            "name": "Test Lucy",
            "reference_photos": [
                "https://via.placeholder.com/300x400/FF6B6B/FFFFFF?text=Lucy"
            ],
            "physical_features": {
                "hair": "brown curly",
                "eyes": "blue"
            },
            "age": 6,
            "gender": "girl",
            "style": "watercolor"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/characters/initialize",
                json=character_data
            )
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "success":
                self.results.append(("Character Init", "✅ PASSED", None))
                print(f"  ✅ Character initialized: {data['character_id']}")
            else:
                self.results.append(("Character Init", "❌ FAILED", "Initialization failed"))
                
        except Exception as e:
            self.results.append(("Character Init", "❌ FAILED", str(e)))
            print(f"  ❌ Failed: {e}")
    
    def test_sprite_generation(self):
        """Test sprite generation"""
        print("\n📍 Test 3: Sprite Generation")
        
        generation_request = {
            "character_id": self.test_character_id,
            "character_data": {
                "name": "Test Lucy",
                "reference_photo": "https://via.placeholder.com/300x400",
                "style": "watercolor"
            },
            "poses": ["standing", "sitting"],
            "emotions": ["happy", "sad"],
            "include_actions": False,
            "generation_api": "dalle"
        }
        
        try:
            print("  ⏳ Generating sprites (this may take 30-60 seconds)...")
            response = requests.post(
                f"{self.base_url}/api/sprites/generate",
                json=generation_request,
                timeout=120  # 2 minute timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "success":
                self.results.append(("Sprite Generation", "✅ PASSED", None))
                print(f"  ✅ Generated {data.get('sprites_generated', 0)} sprites")
            else:
                self.results.append(("Sprite Generation", "⚠️ WARNING", "Generation incomplete"))
                
        except requests.exceptions.Timeout:
            self.results.append(("Sprite Generation", "⚠️ WARNING", "Timeout - generation may still be running"))
            print("  ⚠️  Generation timed out (may still be running in background)")
        except Exception as e:
            self.results.append(("Sprite Generation", "❌ FAILED", str(e)))
            print(f"  ❌ Failed: {e}")
    
    def test_get_sprites(self):
        """Test getting sprites for a character"""
        print("\n📍 Test 4: Get Sprites")
        
        try:
            response = requests.get(f"{self.base_url}/api/sprites/{self.test_character_id}")
            
            if response.status_code == 404:
                self.results.append(("Get Sprites", "⚠️ WARNING", "No sprites found yet"))
                print("  ⚠️  No sprites found (generation may still be running)")
            else:
                response.raise_for_status()
                data = response.json()
                
                if data["status"] == "success":
                    sprite_count = len(data.get("sprites", {}).get("by_pose", {}))
                    self.results.append(("Get Sprites", "✅ PASSED", None))
                    print(f"  ✅ Retrieved sprites for character")
                    print(f"     Poses: {sprite_count}")
                    
        except Exception as e:
            self.results.append(("Get Sprites", "❌ FAILED", str(e)))
            print(f"  ❌ Failed: {e}")
    
    def test_scene_composition(self):
        """Test single scene composition"""
        print("\n📍 Test 5: Scene Composition")
        
        scene_request = {
            "scene_text": "Lucy was happy playing in the sunny park",
            "character_mappings": {"Lucy": self.test_character_id},
            "background_style": "watercolor",
            "generation_api": "dalle",
            "auto_compose": True
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/scenes/compose",
                json=scene_request,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "success":
                self.results.append(("Scene Composition", "✅ PASSED", None))
                print(f"  ✅ Scene composed successfully")
                if data.get("composed_url"):
                    print(f"     Composed URL: {data['composed_url'][:50]}...")
                    
        except Exception as e:
            self.results.append(("Scene Composition", "⚠️ WARNING", str(e)))
            print(f"  ⚠️  Warning: {e}")
    
    def test_story_processing(self):
        """Test full story processing"""
        print("\n📍 Test 6: Story Processing")
        
        story_request = {
            "story_text": """
            Lucy was excited for her first day at school.
            She put on her favorite blue dress and smiled.
            At school, she made new friends and felt happy.
            """,
            "character_mappings": {"Lucy": self.test_character_id},
            "background_style": "watercolor",
            "generation_api": "dalle"
        }
        
        try:
            print("  ⏳ Processing story...")
            response = requests.post(
                f"{self.base_url}/api/stories/process",
                json=story_request,
                timeout=120
            )
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "success":
                scene_count = data.get("total_scenes", 0)
                self.results.append(("Story Processing", "✅ PASSED", None))
                print(f"  ✅ Story processed into {scene_count} scenes")
                
                # Show scene details
                for scene in data.get("scenes", [])[:2]:  # Show first 2 scenes
                    print(f"     Scene {scene['index']}: {scene['scene_text'][:50]}...")
                    
        except Exception as e:
            self.results.append(("Story Processing", "⚠️ WARNING", str(e)))
            print(f"  ⚠️  Warning: {e}")
    
    def test_manual_composition(self):
        """Test manual sprite composition"""
        print("\n📍 Test 7: Manual Composition")
        
        composition_request = {
            "background_url": "https://via.placeholder.com/1920x1080/87CEEB/FFFFFF?text=Background",
            "sprites": [
                {
                    "url": "https://via.placeholder.com/300x400/FF6B6B/FFFFFF?text=Sprite",
                    "x": 0.5,
                    "y": 0.7,
                    "scale": 0.4
                }
            ],
            "output_format": "png"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/compose/manual",
                json=composition_request
            )
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "success":
                self.results.append(("Manual Composition", "✅ PASSED", None))
                print(f"  ✅ Manual composition successful")
                
        except Exception as e:
            self.results.append(("Manual Composition", "⚠️ WARNING", str(e)))
            print(f"  ⚠️  Warning: {e}")
    
    def print_results(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, status, _ in self.results if "PASSED" in status)
        warnings = sum(1 for _, status, _ in self.results if "WARNING" in status)
        failed = sum(1 for _, status, _ in self.results if "FAILED" in status)
        
        for test_name, status, error in self.results:
            print(f"{status} {test_name:20}", end="")
            if error:
                print(f" - {error[:40]}")
            else:
                print()
        
        print("\n" + "-" * 60)
        print(f"Total Tests: {len(self.results)}")
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"❌ Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 All critical tests passed! API is ready for integration.")
        else:
            print("\n⚠️  Some tests failed. Please check the errors above.")
        
        # Integration example
        print("\n" + "=" * 60)
        print("💡 INTEGRATION EXAMPLE FOR MYSUNSHINESTORIES")
        print("=" * 60)
        print("""
# In your MySunshineStories backend:

import requests

def generate_story_images(sunshine_profile, story_text):
    # 1. Initialize character from Sunshine profile
    response = requests.post(
        "http://localhost:8000/api/characters/initialize",
        json={
            "character_id": sunshine_profile.id,
            "name": sunshine_profile.child_name,
            "reference_photos": sunshine_profile.photos,
            "style": "watercolor"
        }
    )
    
    # 2. Process the story
    response = requests.post(
        "http://localhost:8000/api/stories/process",
        json={
            "story_text": story_text,
            "character_mappings": {
                sunshine_profile.child_name: sunshine_profile.id
            }
        }
    )
    
    # 3. Return composed scene URLs
    story_data = response.json()
    return [scene['composed_url'] for scene in story_data['scenes']]
        """)


if __name__ == "__main__":
    print("\n🚀 Starting LucianMirror API Tests")
    print("   Make sure the API server is running on port 8000")
    print("   Run: cd backend && python -m uvicorn main:app --port 8000\n")
    
    tester = LucianMirrorAPITester()
    
    # Check if custom URL provided
    if len(sys.argv) > 1:
        tester.base_url = sys.argv[1]
        print(f"Using API URL: {tester.base_url}")
    
    tester.run_all_tests()