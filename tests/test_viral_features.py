import pytest
from flask import session
from src.models import db, User, Story, Challenge, Achievement

class TestViralFeatures:
    """Test cases for viral features (challenges, achievements, sharing)"""
    
    def test_view_challenges(self, client):
        """Test viewing challenges page"""
        response = client.get('/viral/challenges')
        assert response.status_code == 200
        assert b'Story Challenges' in response.data
    
    def test_view_challenge_detail(self, client, app, test_challenge):
        """Test viewing a specific challenge"""
        response = client.get(f'/viral/challenge/{test_challenge.id}')
        assert response.status_code == 200
        assert test_challenge.title.encode() in response.data
    
    def test_submit_to_challenge_not_logged_in(self, client, test_challenge, test_story):
        """Test submitting to a challenge when not logged in"""
        response = client.post('/viral/submit_challenge', data={
            'challenge_id': test_challenge.id,
            'story_id': test_story.id
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in' in response.data
    
    def test_submit_to_challenge_logged_in(self, client, app, test_user, test_story, test_challenge):
        """Test submitting to a challenge when logged in"""
        # Log in the test user
        client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'password123'
        })
        
        response = client.post('/viral/submit_challenge', data={
            'challenge_id': test_challenge.id,
            'story_id': test_story.id
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Story submitted to challenge successfully' in response.data
        
        # Verify the story is now associated with the challenge
        with app.app_context():
            updated_story = db.session.get(Story, test_story.id)
            assert updated_story.challenge_id == test_challenge.id
            assert updated_story.is_public == True
    
    def test_view_achievements_not_logged_in(self, client):
        """Test viewing achievements when not logged in"""
        response = client.get('/viral/achievements', follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in' in response.data
    
    def test_view_achievements_logged_in(self, client, app, test_user, test_achievement):
        """Test viewing achievements when logged in"""
        # Log in the test user
        client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'password123'
        })
        
        # Award an achievement to the user
        with app.app_context():
            test_user.achievements.append(test_achievement)
            db.session.commit()
        
        response = client.get('/viral/achievements')
        assert response.status_code == 200
        assert test_achievement.name.encode() in response.data
    
    def test_award_achievement_not_logged_in(self, client, test_user, test_achievement):
        """Test awarding an achievement when not logged in"""
        response = client.post('/viral/award_achievement', data={
            'user_id': test_user.id,
            'achievement_id': test_achievement.id
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in' in response.data
    
    def test_award_achievement(self, client, app, test_user, test_achievement):
        """Test awarding an achievement"""
        # Log in the test user
        client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'password123'
        })
        
        response = client.post('/viral/award_achievement', data={
            'user_id': test_user.id,
            'achievement_id': test_achievement.id
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Achievement awarded successfully' in response.data
        
        # Verify the user now has the achievement
        with app.app_context():
            user = db.session.get(User, test_user.id)
            # Check if achievement is in user's achievements by ID instead of object comparison
            achievement_ids = [a.id for a in user.achievements]
            assert test_achievement.id in achievement_ids
    
    def test_share_story_not_logged_in(self, client, test_story):
        """Test sharing a story when not logged in"""
        response = client.get(f'/viral/share/{test_story.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in' in response.data
    
    def test_share_story_logged_in(self, client, app, test_user, test_story):
        """Test sharing a story when logged in"""
        # Log in the test user
        client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'password123'
        })
        
        response = client.get(f'/viral/share/{test_story.id}')
        assert response.status_code == 200
        assert b'Share Your Story' in response.data
        
        # Test the actual sharing action
        response = client.post(f'/viral/share/{test_story.id}', data={
            'share_type': 'public'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Your story has been shared successfully' in response.data
        
        # Verify the story is now public and shared
        with app.app_context():
            updated_story = db.session.get(Story, test_story.id)
            assert updated_story.is_public == True
            assert updated_story.is_shared == True
    
    def test_view_shared_stories(self, client, app, test_user, test_story):
        """Test viewing shared stories"""
        # Make the test story public and shared directly in the database
        with app.app_context():
            story = db.session.get(Story, test_story.id)
            story.is_public = True
            story.is_shared = True
            story.title = "Test Story"  # Ensure title is set
            db.session.commit()
            
            # Debug: Verify story state after commit
            story_check = db.session.get(Story, test_story.id)
            print(f"DEBUG: Story ID: {story_check.id}, Title: {story_check.title}, Public: {story_check.is_public}, Shared: {story_check.is_shared}")
            
            # Debug: Check what stories are returned by the query used in the route
            shared_stories = Story.query.filter_by(is_public=True, is_shared=True).all()
            print(f"DEBUG: Shared stories count: {len(shared_stories)}")
            for s in shared_stories:
                print(f"DEBUG: Shared story: {s.id} - {s.title} - Public: {s.is_public} - Shared: {s.is_shared}")
        
        # Clear any existing session data
        client.get('/auth/logout', follow_redirects=True)
        
        # Access the shared stories page
        response = client.get('/viral/shared')
        
        # Debug: Print response data
        print(f"DEBUG: Response status: {response.status_code}")
        print(f"DEBUG: Response data: {response.data[:200]}...")
        
        assert response.status_code == 200
        assert test_story.title.encode() in response.data
    
    def test_like_story_not_logged_in(self, client, test_story):
        """Test liking a story when not logged in"""
        response = client.post(f'/viral/story/{test_story.id}/like')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == False
    
    def test_like_story_logged_in(self, client, app, test_user, test_story):
        """Test liking a story when logged in"""
        # Log in the test user
        client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'password123'
        })
        
        response = client.post(f'/viral/story/{test_story.id}/like')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        
        # Verify the story like count increased
        with app.app_context():
            updated_story = db.session.get(Story, test_story.id)
            assert updated_story.like_count == 1
