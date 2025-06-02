import pytest
from src.models.story import Story
from src.models.character import Character
from src.models.setting import Setting

def test_story_creation(authenticated_client, db):
    """Test creating a new story."""
    response = authenticated_client.post('/story/create', data={
        'title': 'Test Story',
        'description': 'This is a test story',
        'age_group': '7-9'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Check that the story was created in the database
    story = Story.query.filter_by(title='Test Story').first()
    assert story is not None
    assert story.description == 'This is a test story'
    assert story.age_group == '7-9'

def test_story_view(authenticated_client, db):
    """Test viewing a story."""
    # Create a story for the authenticated user
    from src.models.user import User
    user = User.query.filter_by(username='testuser').first()
    
    story = Story(
        title='View Test Story',
        description='This is a story for testing view',
        age_group='7-9',
        user_id=user.id
    )
    db.session.add(story)
    db.session.commit()
    
    # View the story
    response = authenticated_client.get(f'/story/{story.id}/view')
    assert response.status_code == 200
    assert b'View Test Story' in response.data

def test_story_edit(authenticated_client, db):
    """Test editing a story."""
    # Create a story for the authenticated user
    from src.models.user import User
    user = User.query.filter_by(username='testuser').first()
    
    story = Story(
        title='Edit Test Story',
        description='This is a story for testing edit',
        age_group='7-9',
        user_id=user.id
    )
    db.session.add(story)
    db.session.commit()
    
    # Edit the story
    response = authenticated_client.post(f'/story/{story.id}/edit', data={
        'title': 'Updated Story Title',
        'description': 'Updated story description',
        'age_group': '10-12'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Check that the story was updated in the database
    updated_story = Story.query.get(story.id)
    assert updated_story.title == 'Updated Story Title'
    assert updated_story.description == 'Updated story description'
    assert updated_story.age_group == '10-12'

def test_character_creation(authenticated_client, db):
    """Test creating a character for a story."""
    # Create a story for the authenticated user
    from src.models.user import User
    user = User.query.filter_by(username='testuser').first()
    
    story = Story(
        title='Character Test Story',
        description='This is a story for testing character creation',
        age_group='7-9',
        user_id=user.id
    )
    db.session.add(story)
    db.session.commit()
    
    # Create a character
    response = authenticated_client.post(f'/story/{story.id}/character/create', data={
        'name': 'Test Character',
        'description': 'This is a test character',
        'traits': 'brave,smart,kind'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Check that the character was created in the database
    character = Character.query.filter_by(name='Test Character').first()
    assert character is not None
    assert character.description == 'This is a test character'
    assert character.story_id == story.id

def test_setting_creation(authenticated_client, db):
    """Test creating a setting for a story."""
    # Create a story for the authenticated user
    from src.models.user import User
    user = User.query.filter_by(username='testuser').first()
    
    story = Story(
        title='Setting Test Story',
        description='This is a story for testing setting creation',
        age_group='7-9',
        user_id=user.id
    )
    db.session.add(story)
    db.session.commit()
    
    # Create a setting
    response = authenticated_client.post(f'/story/{story.id}/setting/create', data={
        'name': 'Test Setting',
        'description': 'This is a test setting',
        'time_period': 'fantasy'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Check that the setting was created in the database
    setting = Setting.query.filter_by(name='Test Setting').first()
    assert setting is not None
    assert setting.description == 'This is a test setting'
    assert setting.story_id == story.id
