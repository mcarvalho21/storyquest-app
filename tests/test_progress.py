import pytest
from src.models.user import User
from src.models.progress import Progress

def test_progress_saving(authenticated_client, db):
    """Test saving and retrieving user progress."""
    # Create a story for the authenticated user
    from src.models.story import Story
    user = User.query.filter_by(username='testuser').first()
    
    story = Story(
        title='Progress Test Story',
        description='This is a story for testing progress saving',
        age_group='7-9',
        user_id=user.id
    )
    db.session.add(story)
    db.session.commit()
    
    # Save progress
    response = authenticated_client.post(f'/progress/save', data={
        'story_id': story.id,
        'current_step': 'character_creation',
        'data': '{"character_name":"Test Hero","character_traits":["brave","smart"]}'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Check that progress was saved in the database
    progress = Progress.query.filter_by(user_id=user.id, story_id=story.id).first()
    assert progress is not None
    assert progress.current_step == 'character_creation'
    assert '"character_name":"Test Hero"' in progress.data
    
    # Test retrieving progress
    response = authenticated_client.get(f'/progress/load/{story.id}')
    assert response.status_code == 200
    assert b'character_creation' in response.data
    assert b'Test Hero' in response.data

def test_resume_progress(authenticated_client, db):
    """Test resuming from saved progress."""
    # Create a story and progress for the authenticated user
    from src.models.story import Story
    user = User.query.filter_by(username='testuser').first()
    
    story = Story(
        title='Resume Test Story',
        description='This is a story for testing progress resumption',
        age_group='7-9',
        user_id=user.id
    )
    db.session.add(story)
    db.session.commit()
    
    # Create progress record
    progress = Progress(
        user_id=user.id,
        story_id=story.id,
        current_step='setting_creation',
        data='{"setting_name":"Magic Forest","setting_type":"fantasy"}'
    )
    db.session.add(progress)
    db.session.commit()
    
    # Test resuming progress
    response = authenticated_client.get(f'/story/resume/{story.id}', follow_redirects=True)
    assert response.status_code == 200
    
    # Check that we're directed to the correct step with data loaded
    assert b'setting_creation' in response.data
    assert b'Magic Forest' in response.data

def test_progress_update(authenticated_client, db):
    """Test updating existing progress."""
    # Create a story and progress for the authenticated user
    from src.models.story import Story
    user = User.query.filter_by(username='testuser').first()
    
    story = Story(
        title='Update Progress Test',
        description='This is a story for testing progress updates',
        age_group='7-9',
        user_id=user.id
    )
    db.session.add(story)
    db.session.commit()
    
    # Create initial progress record
    progress = Progress(
        user_id=user.id,
        story_id=story.id,
        current_step='character_creation',
        data='{"character_name":"Initial Hero","character_traits":["brave"]}'
    )
    db.session.add(progress)
    db.session.commit()
    
    # Update progress
    response = authenticated_client.post(f'/progress/save', data={
        'story_id': story.id,
        'current_step': 'character_creation',
        'data': '{"character_name":"Updated Hero","character_traits":["brave","wise"]}'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Check that progress was updated in the database
    updated_progress = Progress.query.filter_by(user_id=user.id, story_id=story.id).first()
    assert updated_progress is not None
    assert updated_progress.current_step == 'character_creation'
    assert '"character_name":"Updated Hero"' in updated_progress.data
    assert '"wise"' in updated_progress.data
    
    # Ensure only one progress record exists for this story/user
    progress_count = Progress.query.filter_by(user_id=user.id, story_id=story.id).count()
    assert progress_count == 1
