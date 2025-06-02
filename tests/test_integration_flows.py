import pytest
from flask import session, url_for
from src.models import db, User, Story, Progress, Achievement, Challenge
from datetime import datetime

class TestIntegrationFlows:
    """Test cases for critical user flows that span multiple features"""
    
    def test_complete_story_creation_flow(self, client, app):
        """Test the complete story creation flow from registration to story completion"""
        # Step 1: Register a new user
        response = client.post('/auth/register', data={
            'username': 'integration_user',
            'email': 'integration@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome, integration_user' in response.data
        
        # Step 2: Create a new story
        response = client.post('/story/create', data={
            'title': 'Integration Test Story',
            'description': 'A story created during integration testing',
            'age_group': '7-9'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Story created successfully' in response.data
        
        # Get the story ID from the database
        with app.app_context():
            story = Story.query.filter_by(title='Integration Test Story').first()
            assert story is not None
            story_id = story.id
        
        # Step 3: Add a character to the story - Fix route to match actual implementation
        response = client.post(f'/story/{story_id}/character/create', data={
            'name': 'Integration Hero',
            'description': 'A brave hero for integration testing',
            'traits': 'brave,smart,kind'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Character created successfully' in response.data
        
        # Step 4: Add a setting to the story - Fix route to match actual implementation
        response = client.post(f'/story/{story_id}/setting/create', data={
            'name': 'Integration Land',
            'description': 'A magical land for integration testing',
            'time_period': 'fantasy'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Setting created successfully' in response.data
        
        # Step 5: Save progress
        response = client.post('/progress/save', data={
            'story_id': story_id,
            'current_step': 'plot_development',
            'data': '{"plot_points":["Beginning","Middle","End"]}'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify progress was saved
        with app.app_context():
            progress = Progress.query.filter_by(story_id=story_id).first()
            assert progress is not None
            assert progress.current_step == 'plot_development'
        
        # Step 6: Complete and share the story - Fix route to match actual implementation
        response = client.post(f'/story/{story_id}/share', data={
            'share_type': 'public'
        }, follow_redirects=True)
        
        # Since this is now AJAX, we expect a JSON response
        assert response.status_code == 200
        assert b'success' in response.data
        
        # Verify story is now public
        with app.app_context():
            updated_story = Story.query.get(story_id)
            assert updated_story.is_public == True
    
    def test_challenge_participation_flow(self, client, app):
        """Test the flow of participating in a challenge and earning an achievement"""
        # Step 1: Register a new user
        response = client.post('/auth/register', data={
            'username': 'challenge_user',
            'email': 'challenge@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Step 2: Create a new story
        response = client.post('/story/create', data={
            'title': 'Challenge Test Story',
            'description': 'A story created for challenge testing',
            'age_group': '7-9'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Get the story ID from the database
        with app.app_context():
            story = Story.query.filter_by(title='Challenge Test Story').first()
            assert story is not None
            story_id = story.id
            
            # Create a test challenge - Fix date format to use datetime objects
            challenge = Challenge(
                title='Integration Challenge',
                description='A challenge for integration testing',
                difficulty='easy',
                age_group='7-9',
                start_date=datetime(2025, 1, 1),  # Use datetime object instead of string
                end_date=datetime(2025, 12, 31),   # Use datetime object instead of string
                is_active=True
            )
            db.session.add(challenge)
            db.session.commit()
            challenge_id = challenge.id
            
            # Create a test achievement
            achievement = Achievement(
                name='Integration Achievement',
                description='An achievement for completing integration testing',
                criteria='Complete the integration challenge',
                points=100
            )
            db.session.add(achievement)
            db.session.commit()
            achievement_id = achievement.id
        
        # Step 3: Submit story to challenge - Fix route to match actual implementation
        response = client.post('/viral/submit_challenge', data={
            'challenge_id': challenge_id,
            'story_id': story_id
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Story submitted to challenge successfully' in response.data
        
        # Step 4: Award achievement for completing challenge - Fix route to match actual implementation
        # Fix: Pass user_id as a string to match route expectations
        with app.app_context():
            user = User.query.filter_by(username='challenge_user').first()
            user_id = user.id
            
        response = client.post('/viral/award_achievement', data={
            'user_id': str(user_id),  # Convert to string to match form data expectations
            'achievement_id': str(achievement_id)  # Convert to string to match form data expectations
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Achievement awarded successfully' in response.data
        
        # Verify achievement was awarded
        with app.app_context():
            user = User.query.filter_by(username='challenge_user').first()
            achievement = Achievement.query.get(achievement_id)
            achievement_ids = [a.id for a in user.achievements]
            assert achievement.id in achievement_ids
    
    def test_story_resume_and_edit_flow(self, client, app):
        """Test the flow of resuming and editing a story"""
        # Step 1: Register a new user
        response = client.post('/auth/register', data={
            'username': 'resume_user',
            'email': 'resume@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Step 2: Create a new story
        response = client.post('/story/create', data={
            'title': 'Resume Test Story',
            'description': 'A story for testing resume functionality',
            'age_group': '7-9'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Get the story ID from the database
        with app.app_context():
            story = Story.query.filter_by(title='Resume Test Story').first()
            assert story is not None
            story_id = story.id
        
        # Step 3: Save initial progress
        response = client.post('/progress/save', data={
            'story_id': story_id,
            'current_step': 'character_creation',
            'data': '{"character_name":"Resume Hero","character_traits":["brave","smart"]}'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Step 4: Logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        
        # Step 5: Log back in
        response = client.post('/auth/login', data={
            'username': 'resume_user',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome, resume_user' in response.data
        
        # Step 6: Resume the story
        response = client.get(f'/story/resume/{story_id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Resume Test Story' in response.data
        assert b'character_creation' in response.data
        
        # Step 7: Update progress
        response = client.post('/progress/save', data={
            'story_id': story_id,
            'current_step': 'setting_creation',
            'data': '{"setting_name":"Resume Land","setting_type":"fantasy"}'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify progress was updated
        with app.app_context():
            progress = Progress.query.filter_by(story_id=story_id).first()
            assert progress is not None
            assert progress.current_step == 'setting_creation'
            assert 'Resume Land' in progress.data
