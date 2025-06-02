import pytest
from src.models.achievement import Achievement
from src.models.user import User
from datetime import datetime, timedelta

def test_achievement_creation(authenticated_client, db):
    """Test creating and awarding achievements."""
    # Get the authenticated user
    user = User.query.filter_by(username='testuser').first()
    
    # Create an achievement
    achievement = Achievement(
        name='First Story',
        description='Created your first story',
        badge_image='first_story.png',
        points=10
    )
    db.session.add(achievement)
    db.session.commit()
    
    # Award achievement to user
    response = authenticated_client.post('/viral/award_achievement', data={
        'user_id': user.id,
        'achievement_id': achievement.id
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Check that the achievement was awarded
    user = User.query.filter_by(username='testuser').first()
    assert achievement in user.achievements

def test_achievement_display(authenticated_client, db):
    """Test displaying user achievements."""
    # Get the authenticated user
    user = User.query.filter_by(username='testuser').first()
    
    # Create and award multiple achievements
    achievements = [
        Achievement(name='Story Master', description='Created 5 stories', badge_image='story_master.png', points=50),
        Achievement(name='Character Creator', description='Created 10 characters', badge_image='character_creator.png', points=30)
    ]
    
    for achievement in achievements:
        db.session.add(achievement)
    db.session.commit()
    
    # Award achievements to user
    for achievement in achievements:
        user.achievements.append(achievement)
    db.session.commit()
    
    # View achievements page
    response = authenticated_client.get('/viral/achievements')
    assert response.status_code == 200
    
    # Check that all achievements are displayed
    for achievement in achievements:
        assert achievement.name.encode() in response.data
        assert achievement.description.encode() in response.data

def test_story_sharing(authenticated_client, db):
    """Test sharing a story."""
    # Create a story for the authenticated user
    from src.models.story import Story
    user = User.query.filter_by(username='testuser').first()
    
    story = Story(
        title='Share Test Story',
        description='This is a story for testing sharing',
        age_group='7-9',
        user_id=user.id
    )
    db.session.add(story)
    db.session.commit()
    
    # Share the story
    response = authenticated_client.post(f'/viral/share/{story.id}', data={
        'share_type': 'public'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Check that the story is now shared
    shared_story = Story.query.get(story.id)
    assert shared_story.is_shared == True
    
    # Test viewing shared stories
    response = authenticated_client.get('/viral/shared')
    assert response.status_code == 200
    assert b'Share Test Story' in response.data

def test_weekly_challenge(authenticated_client, db):
    """Test weekly challenge functionality."""
    # Create a weekly challenge with proper datetime objects
    from src.models.challenge import Challenge
    
    # Use Python datetime objects instead of strings
    today = datetime.now()
    start_date = today - timedelta(days=3)  # 3 days ago
    end_date = today + timedelta(days=4)    # 4 days from now
    
    challenge = Challenge(
        title='Test Weekly Challenge',
        description='Create a story about space exploration',
        start_date=start_date,
        end_date=end_date,
        difficulty='medium',
        age_group='7-9',
        is_active=True
    )
    db.session.add(challenge)
    db.session.commit()
    
    # View active challenges
    response = authenticated_client.get('/viral/challenges')
    assert response.status_code == 200
    assert b'Test Weekly Challenge' in response.data
    
    # Submit a story for the challenge
    from src.models.story import Story
    user = User.query.filter_by(username='testuser').first()
    
    story = Story(
        title='Space Adventure',
        description='A story about exploring the stars',
        age_group='7-9',
        user_id=user.id
    )
    db.session.add(story)
    db.session.commit()
    
    response = authenticated_client.post(f'/viral/submit_challenge', data={
        'challenge_id': challenge.id,
        'story_id': story.id
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Check that the story is linked to the challenge
    story = Story.query.get(story.id)
    assert story.challenge_id == challenge.id
