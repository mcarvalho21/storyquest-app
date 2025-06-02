import pytest
from flask import session, url_for
from src.models import db, Story, Progress

class TestProgressFeatures:
    """Test suite for progress tracking features"""
    
    def test_view_progress_not_logged_in(self, client):
        """Test viewing progress when not logged in"""
        response = client.get('/progress/stats', follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in' in response.data
    
    def test_view_progress_logged_in(self, client, app, test_user):
        """Test viewing progress when logged in"""
        # Log in the test user
        client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'password123'
        })
        
        response = client.get('/progress/stats')
        assert response.status_code == 200
        assert b'Your Progress' in response.data
    
    def test_track_story_progress(self, client, app, test_user, test_story):
        """Test tracking progress on a story"""
        # Log in the test user
        client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'password123'
        })
        
        # Update progress on the story
        response = client.post('/progress/update', data={
            'story_id': test_story.id,
            'progress_value': 50
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Progress updated' in response.data
        
        # Verify the progress was saved
        with app.app_context():
            progress = Progress.query.filter_by(
                user_id=test_user.id,
                story_id=test_story.id
            ).first()
            assert progress is not None
            assert progress.progress_value == 50
    
    def test_resume_story(self, client, app, test_user, test_story):
        """Test resuming a story with saved progress"""
        # Create progress record
        with app.app_context():
            progress = Progress(
                user_id=test_user.id,
                story_id=test_story.id,
                progress_value=75,
                last_position="chapter_3"
            )
            db.session.add(progress)
            db.session.commit()
        
        # Log in the test user
        client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'password123'
        })
        
        # Resume the story
        response = client.get(f'/story/resume/{test_story.id}')
        assert response.status_code == 200
        assert b'Resume' in response.data
        assert b'75%' in response.data
    
    def test_complete_story(self, client, app, test_user, test_story):
        """Test marking a story as complete"""
        # Log in the test user
        client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'password123'
        })
        
        # Mark story as complete
        response = client.post('/progress/complete', data={
            'story_id': test_story.id
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Story marked as complete' in response.data
        
        # Verify the progress was updated
        with app.app_context():
            progress = Progress.query.filter_by(
                user_id=test_user.id,
                story_id=test_story.id
            ).first()
            assert progress is not None
            assert progress.progress_value == 100
            assert progress.is_complete == True
    
    def test_progress_statistics(self, client, app, test_user):
        """Test viewing progress statistics"""
        # Create multiple progress records
        with app.app_context():
            # Create some test stories
            story1 = Story(
                title="Test Story 1",
                content="Test content 1",
                user_id=test_user.id
            )
            story2 = Story(
                title="Test Story 2",
                content="Test content 2",
                user_id=test_user.id
            )
            story3 = Story(
                title="Test Story 3",
                content="Test content 3",
                user_id=test_user.id
            )
            db.session.add_all([story1, story2, story3])
            db.session.commit()
            
            # Add progress records
            progress1 = Progress(
                user_id=test_user.id,
                story_id=story1.id,
                progress_value=100,
                is_complete=True
            )
            progress2 = Progress(
                user_id=test_user.id,
                story_id=story2.id,
                progress_value=50,
                is_complete=False
            )
            progress3 = Progress(
                user_id=test_user.id,
                story_id=story3.id,
                progress_value=25,
                is_complete=False
            )
            db.session.add_all([progress1, progress2, progress3])
            db.session.commit()
        
        # Log in the test user
        client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'password123'
        })
        
        # View progress statistics
        response = client.get('/progress/stats')
        assert response.status_code == 200
        assert b'Your Progress' in response.data
        assert b'Completed Stories' in response.data
        assert b'In Progress' in response.data
        
        # Check that the statistics are correct
        assert b'1' in response.data  # 1 completed story
        assert b'2' in response.data  # 2 in-progress stories
    
    def test_progress_history(self, client, app, test_user, test_story):
        """Test viewing progress history"""
        # Create progress history
        with app.app_context():
            # Add progress record with history
            progress = Progress(
                user_id=test_user.id,
                story_id=test_story.id,
                progress_value=75,
                history=[
                    {"timestamp": "2025-05-01T10:00:00", "value": 25},
                    {"timestamp": "2025-05-02T11:30:00", "value": 50},
                    {"timestamp": "2025-05-03T14:15:00", "value": 75}
                ]
            )
            db.session.add(progress)
            db.session.commit()
        
        # Log in the test user
        client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'password123'
        })
        
        # View progress history
        response = client.get(f'/progress/history/{test_story.id}')
        assert response.status_code == 200
        assert b'Progress History' in response.data
        assert b'May 1' in response.data
        assert b'May 2' in response.data
        assert b'May 3' in response.data
