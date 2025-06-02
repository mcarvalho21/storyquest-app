import os
import sys
import pytest
from flask import Flask
from flask.testing import FlaskClient
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app as flask_app
from src.models.user import db as _db
from src.models.user import User
from src.models.story import Story
from src.models.character import Character
from src.models.setting import Setting
from src.models.achievement import Achievement
from src.models.challenge import Challenge
from src.models.progress import Progress

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Set testing configuration
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost.localdomain'
    })

    # Create app context
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def db(app):
    """Database for testing."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def test_user(app, db):
    """Create a test user for testing."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            age_group='7-9'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Detach the user from the session to avoid cross-session issues
        db.session.expunge_all()
        
        # Retrieve a fresh instance
        user = User.query.filter_by(username='testuser').first()
        return user

@pytest.fixture
def test_story(app, db, test_user):
    """Create a test story for testing."""
    with app.app_context():
        story = Story(
            title='Test Story',
            description='This is a test story',
            content='Once upon a time, there was a test story. The end.',
            user_id=test_user.id,
            age_group='7-9',
            theme='adventure',
            is_public=False,
            is_draft=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(story)
        db.session.commit()
        
        # Detach the story from the session to avoid cross-session issues
        db.session.expunge_all()
        
        # Retrieve a fresh instance
        story = Story.query.filter_by(title='Test Story').first()
        return story

@pytest.fixture
def test_character(app, db, test_story):
    """Create a test character for testing."""
    with app.app_context():
        character = Character(
            name='Test Character',
            description='This is a test character',
            age='10',
            personality='Brave and curious',
            story_id=test_story.id
        )
        db.session.add(character)
        db.session.commit()
        
        # Detach from session
        db.session.expunge_all()
        
        # Retrieve a fresh instance
        character = Character.query.filter_by(name='Test Character').first()
        return character

@pytest.fixture
def test_setting(app, db, test_story):
    """Create a test setting for testing."""
    with app.app_context():
        setting = Setting(
            name='Test Setting',
            description='This is a test setting',
            time_period='Medieval',
            mood='Mysterious',
            story_id=test_story.id
        )
        db.session.add(setting)
        db.session.commit()
        
        # Detach from session
        db.session.expunge_all()
        
        # Retrieve a fresh instance
        setting = Setting.query.filter_by(name='Test Setting').first()
        return setting

@pytest.fixture
def test_achievement(app, db):
    """Create a test achievement for testing."""
    with app.app_context():
        achievement = Achievement(
            name='Test Achievement',
            description='This is a test achievement',
            badge_image='test_badge.png',
            points=10
        )
        db.session.add(achievement)
        db.session.commit()
        
        # Detach from session
        db.session.expunge_all()
        
        # Retrieve a fresh instance
        achievement = Achievement.query.filter_by(name='Test Achievement').first()
        return achievement

@pytest.fixture
def test_challenge(app, db):
    """Create a test challenge for testing."""
    with app.app_context():
        challenge = Challenge(
            title='Test Challenge',
            description='This is a test challenge',
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=7),
            difficulty='medium',
            age_group='7-9',
            is_active=True
        )
        db.session.add(challenge)
        db.session.commit()
        
        # Detach from session
        db.session.expunge_all()
        
        # Retrieve a fresh instance
        challenge = Challenge.query.filter_by(title='Test Challenge').first()
        return challenge

@pytest.fixture
def test_progress(app, db, test_user, test_story):
    """Create a test progress record for testing."""
    with app.app_context():
        progress = Progress(
            user_id=test_user.id,
            story_id=test_story.id,
            progress_value=50,
            last_position='chapter_2',
            is_complete=False
        )
        db.session.add(progress)
        db.session.commit()
        
        # Detach from session
        db.session.expunge_all()
        
        # Retrieve a fresh instance
        progress = Progress.query.filter_by(user_id=test_user.id, story_id=test_story.id).first()
        return progress

@pytest.fixture
def authenticated_client(client, app, test_user):
    """A test client with authenticated user."""
    with app.app_context():
        # Log in the user
        client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'password123'
        }, follow_redirects=True)
        
        return client

@pytest.fixture
def shared_story(app, db, test_story):
    """Create a shared version of the test story."""
    with app.app_context():
        # Use SQLAlchemy 2.0 compatible method
        story = db.session.get(Story, test_story.id)
        story.is_public = True
        story.is_shared = True
        story.share_url = f'shared/{story.id}'
        story.share_message = 'Check out my test story!'
        db.session.commit()
        
        # Detach from session
        db.session.expunge_all()
        
        # Retrieve a fresh instance using SQLAlchemy 2.0 compatible method
        story = db.session.get(Story, test_story.id)
        return story
