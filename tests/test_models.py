import pytest
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import User
from src.models.story import Story
from src.models.character import Character
from src.models.setting import Setting
from src.models.story_element import StoryElement
from src.models.progress import Progress
from src.models.achievement import Achievement

class TestUserModel:
    """Test suite for User model."""
    
    def test_user_creation(self, db):
        """Test creating a user with valid data."""
        user = User(
            username='testuser1',
            email='test1@example.com',
            password=generate_password_hash('password123'),
            age_group='7-9'
        )
        db.session.add(user)
        db.session.commit()
        
        saved_user = User.query.filter_by(username='testuser1').first()
        assert saved_user is not None
        assert saved_user.email == 'test1@example.com'
        assert saved_user.age_group == '7-9'
    
    def test_user_unique_constraints(self, db):
        """Test unique constraints on username and email."""
        # Create first user
        user1 = User(
            username='uniqueuser',
            email='unique@example.com',
            password=generate_password_hash('password123'),
            age_group='7-9'
        )
        db.session.add(user1)
        db.session.commit()
        
        # Try to create user with same username
        user2 = User(
            username='uniqueuser',
            email='different@example.com',
            password=generate_password_hash('password123'),
            age_group='7-9'
        )
        db.session.add(user2)
        
        with pytest.raises(Exception):
            db.session.commit()
        
        db.session.rollback()
        
        # Try to create user with same email
        user3 = User(
            username='differentuser',
            email='unique@example.com',
            password=generate_password_hash('password123'),
            age_group='7-9'
        )
        db.session.add(user3)
        
        with pytest.raises(Exception):
            db.session.commit()
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = 'secure_password123'
        hashed = generate_password_hash(password)
        
        assert check_password_hash(hashed, password) is True
        assert check_password_hash(hashed, 'wrong_password') is False
    
    def test_user_story_relationship(self, db):
        """Test relationship between user and stories."""
        # Create a user
        user = User(
            username='storyuser',
            email='story@example.com',
            password=generate_password_hash('password123'),
            age_group='7-9'
        )
        db.session.add(user)
        db.session.commit()
        
        # Create stories for the user
        story1 = Story(
            title='Test Story 1',
            description='Description 1',
            age_group='7-9',
            user_id=user.id
        )
        
        story2 = Story(
            title='Test Story 2',
            description='Description 2',
            age_group='10-12',
            user_id=user.id
        )
        
        db.session.add_all([story1, story2])
        db.session.commit()
        
        # Check relationship
        assert len(user.stories) == 2
        assert user.stories[0].title in ['Test Story 1', 'Test Story 2']
        assert user.stories[1].title in ['Test Story 1', 'Test Story 2']
    
    def test_user_achievement_relationship(self, db):
        """Test many-to-many relationship between users and achievements."""
        # Create a user
        user = User(
            username='achievementuser',
            email='achievement@example.com',
            password=generate_password_hash('password123'),
            age_group='7-9'
        )
        db.session.add(user)
        
        # Create achievements
        achievement1 = Achievement(
            name='First Story',
            description='Created your first story',
            badge_image='first_story.png',
            points=10
        )
        
        achievement2 = Achievement(
            name='Prolific Writer',
            description='Created 5 stories',
            badge_image='prolific_writer.png',
            points=50
        )
        
        db.session.add_all([achievement1, achievement2])
        db.session.commit()
        
        # Add achievements to user
        user.achievements.append(achievement1)
        user.achievements.append(achievement2)
        db.session.commit()
        
        # Check relationship
        assert len(user.achievements) == 2
        achievement_names = [a.name for a in user.achievements]
        assert 'First Story' in achievement_names
        assert 'Prolific Writer' in achievement_names
        
        # Check reverse relationship
        assert len(achievement1.users) == 1
        assert achievement1.users[0].username == 'achievementuser'


class TestStoryModel:
    """Test suite for Story model."""
    
    def test_story_creation(self, db):
        """Test creating a story with valid data."""
        # Create a user first
        user = User(
            username='storymodeluser',
            email='storymodel@example.com',
            password=generate_password_hash('password123'),
            age_group='7-9'
        )
        db.session.add(user)
        db.session.commit()
        
        # Create a story
        story = Story(
            title='Model Test Story',
            description='This is a test story for model testing',
            age_group='7-9',
            user_id=user.id
        )
        db.session.add(story)
        db.session.commit()
        
        # Retrieve and verify
        saved_story = Story.query.filter_by(title='Model Test Story').first()
        assert saved_story is not None
        assert saved_story.description == 'This is a test story for model testing'
        assert saved_story.age_group == '7-9'
        assert saved_story.is_shared is False  # Default value
    
    def test_story_relationships(self, db):
        """Test relationships between story and other models."""
        # Create a user
        user = User(
            username='relationuser',
            email='relation@example.com',
            password=generate_password_hash('password123'),
            age_group='7-9'
        )
        db.session.add(user)
        db.session.commit()
        
        # Create a story
        story = Story(
            title='Relationship Test Story',
            description='Testing relationships',
            age_group='7-9',
            user_id=user.id
        )
        db.session.add(story)
        db.session.commit()
        
        # Add characters
        character1 = Character(
            name='Hero',
            description='The main protagonist',
            traits='brave,smart',
            story_id=story.id
        )
        
        character2 = Character(
            name='Villain',
            description='The antagonist',
            traits='cunning,powerful',
            story_id=story.id
        )
        
        db.session.add_all([character1, character2])
        
        # Add setting
        setting = Setting(
            name='Enchanted Forest',
            description='A magical forest setting',
            time_period='fantasy',
            story_id=story.id
        )
        db.session.add(setting)
        
        # Add story elements
        element1 = StoryElement(
            element_type='introduction',
            content='Once upon a time...',
            position=1,
            story_id=story.id
        )
        
        element2 = StoryElement(
            element_type='conflict',
            content='Suddenly, a dragon appeared!',
            position=2,
            story_id=story.id
        )
        
        db.session.add_all([element1, element2])
        db.session.commit()
        
        # Check relationships
        assert len(story.characters) == 2
        assert len(story.settings) == 1
        assert len(story.story_elements) == 2
        
        # Check character names
        character_names = [c.name for c in story.characters]
        assert 'Hero' in character_names
        assert 'Villain' in character_names
        
        # Check setting
        assert story.settings[0].name == 'Enchanted Forest'
        
        # Check story elements
        assert story.story_elements[0].position < story.story_elements[1].position
        element_types = [e.element_type for e in story.story_elements]
        assert 'introduction' in element_types
        assert 'conflict' in element_types
    
    def test_story_cascade_delete(self, db):
        """Test cascade delete of related objects when story is deleted."""
        # Create a user
        user = User(
            username='cascadeuser',
            email='cascade@example.com',
            password=generate_password_hash('password123'),
            age_group='7-9'
        )
        db.session.add(user)
        db.session.commit()
        
        # Create a story
        story = Story(
            title='Cascade Test Story',
            description='Testing cascade delete',
            age_group='7-9',
            user_id=user.id
        )
        db.session.add(story)
        db.session.commit()
        
        # Add a character
        character = Character(
            name='Test Character',
            description='For cascade testing',
            story_id=story.id
        )
        db.session.add(character)
        
        # Add a setting
        setting = Setting(
            name='Test Setting',
            description='For cascade testing',
            story_id=story.id
        )
        db.session.add(setting)
        
        # Add a story element
        element = StoryElement(
            element_type='test',
            content='Test content',
            position=1,
            story_id=story.id
        )
        db.session.add(element)
        
        # Add progress
        progress = Progress(
            user_id=user.id,
            story_id=story.id,
            current_step='test_step',
            data='{"test": "data"}'
        )
        db.session.add(progress)
        db.session.commit()
        
        # Get IDs for later verification
        character_id = character.id
        setting_id = setting.id
        element_id = element.id
        progress_id = progress.id
        
        # Delete the story
        db.session.delete(story)
        db.session.commit()
        
        # Verify cascade delete
        assert Character.query.get(character_id) is None
        assert Setting.query.get(setting_id) is None
        assert StoryElement.query.get(element_id) is None
        assert Progress.query.get(progress_id) is None


class TestCharacterModel:
    """Test suite for Character model."""
    
    def test_character_creation(self, db):
        """Test creating a character with valid data."""
        # Create a user and story first
        user = User(
            username='charuser',
            email='char@example.com',
            password=generate_password_hash('password123'),
            age_group='7-9'
        )
        db.session.add(user)
        db.session.commit()
        
        story = Story(
            title='Character Test Story',
            description='For character testing',
            age_group='7-9',
            user_id=user.id
        )
        db.session.add(story)
        db.session.commit()
        
        # Create a character
        character = Character(
            name='Test Character',
            description='A character for testing',
            traits='brave,smart,kind',
            story_id=story.id
        )
        db.session.add(character)
        db.session.commit()
        
        # Retrieve and verify
        saved_character = Character.query.filter_by(name='Test Character').first()
        assert saved_character is not None
        assert saved_character.description == 'A character for testing'
        assert saved_character.traits == 'brave,smart,kind'
        assert saved_character.story_id == story.id


class TestSettingModel:
    """Test suite for Setting model."""
    
    def test_setting_creation(self, db):
        """Test creating a setting with valid data."""
        # Create a user and story first
        user = User(
            username='settinguser',
            email='setting@example.com',
            password=generate_password_hash('password123'),
            age_group='7-9'
        )
        db.session.add(user)
        db.session.commit()
        
        story = Story(
            title='Setting Test Story',
            description='For setting testing',
            age_group='7-9',
            user_id=user.id
        )
        db.session.add(story)
        db.session.commit()
        
        # Create a setting
        setting = Setting(
            name='Test Setting',
            description='A setting for testing',
            time_period='medieval',
            story_id=story.id
        )
        db.session.add(setting)
        db.session.commit()
        
        # Retrieve and verify
        saved_setting = Setting.query.filter_by(name='Test Setting').first()
        assert saved_setting is not None
        assert saved_setting.description == 'A setting for testing'
        assert saved_setting.time_period == 'medieval'
        assert saved_setting.story_id == story.id


class TestProgressModel:
    """Test suite for Progress model."""
    
    def test_progress_creation(self, db):
        """Test creating progress with valid data."""
        # Create a user and story first
        user = User(
            username='progressuser',
            email='progress@example.com',
            password=generate_password_hash('password123'),
            age_group='7-9'
        )
        db.session.add(user)
        db.session.commit()
        
        story = Story(
            title='Progress Test Story',
            description='For progress testing',
            age_group='7-9',
            user_id=user.id
        )
        db.session.add(story)
        db.session.commit()
        
        # Create progress
        progress = Progress(
            user_id=user.id,
            story_id=story.id,
            current_step='character_creation',
            data='{"character_name":"Test Hero","character_traits":["brave","smart"]}'
        )
        db.session.add(progress)
        db.session.commit()
        
        # Retrieve and verify
        saved_progress = Progress.query.filter_by(user_id=user.id, story_id=story.id).first()
        assert saved_progress is not None
        assert saved_progress.current_step == 'character_creation'
        assert '"character_name":"Test Hero"' in saved_progress.data
        assert saved_progress.user_id == user.id
        assert saved_progress.story_id == story.id
    
    def test_progress_update(self, db):
        """Test updating progress."""
        # Create a user and story first
        user = User(
            username='updateuser',
            email='update@example.com',
            password=generate_password_hash('password123'),
            age_group='7-9'
        )
        db.session.add(user)
        db.session.commit()
        
        story = Story(
            title='Update Test Story',
            description='For update testing',
            age_group='7-9',
            user_id=user.id
        )
        db.session.add(story)
        db.session.commit()
        
        # Create initial progress
        progress = Progress(
            user_id=user.id,
            story_id=story.id,
            current_step='character_creation',
            data='{"character_name":"Initial Hero"}'
        )
        db.session.add(progress)
        db.session.commit()
        
        # Update progress
        progress.current_step = 'setting_creation'
        progress.data = '{"character_name":"Initial Hero","setting_name":"Magic Forest"}'
        db.session.commit()
        
        # Retrieve and verify
        updated_progress = Progress.query.filter_by(user_id=user.id, story_id=story.id).first()
        assert updated_progress.current_step == 'setting_creation'
        assert '"setting_name":"Magic Forest"' in updated_progress.data


class TestAchievementModel:
    """Test suite for Achievement model."""
    
    def test_achievement_creation(self, db):
        """Test creating an achievement with valid data."""
        achievement = Achievement(
            name='Test Achievement',
            description='An achievement for testing',
            badge_image='test_badge.png',
            points=25
        )
        db.session.add(achievement)
        db.session.commit()
        
        # Retrieve and verify
        saved_achievement = Achievement.query.filter_by(name='Test Achievement').first()
        assert saved_achievement is not None
        assert saved_achievement.description == 'An achievement for testing'
        assert saved_achievement.badge_image == 'test_badge.png'
        assert saved_achievement.points == 25


class TestStoryElementModel:
    """Test suite for StoryElement model."""
    
    def test_story_element_creation(self, db):
        """Test creating a story element with valid data."""
        # Create a user and story first
        user = User(
            username='elementuser',
            email='element@example.com',
            password=generate_password_hash('password123'),
            age_group='7-9'
        )
        db.session.add(user)
        db.session.commit()
        
        story = Story(
            title='Element Test Story',
            description='For element testing',
            age_group='7-9',
            user_id=user.id
        )
        db.session.add(story)
        db.session.commit()
        
        # Create a story element
        element = StoryElement(
            element_type='introduction',
            content='Once upon a time in a land far away...',
            position=1,
            story_id=story.id
        )
        db.session.add(element)
        db.session.commit()
        
        # Retrieve and verify
        saved_element = StoryElement.query.filter_by(story_id=story.id, position=1).first()
        assert saved_element is not None
        assert saved_element.element_type == 'introduction'
        assert saved_element.content == 'Once upon a time in a land far away...'
        assert saved_element.position == 1
    
    def test_story_element_ordering(self, db):
        """Test ordering of story elements by position."""
        # Create a user and story first
        user = User(
            username='orderuser',
            email='order@example.com',
            password=generate_password_hash('password123'),
            age_group='7-9'
        )
        db.session.add(user)
        db.session.commit()
        
        story = Story(
            title='Order Test Story',
            description='For ordering testing',
            age_group='7-9',
            user_id=user.id
        )
        db.session.add(story)
        db.session.commit()
        
        # Create story elements in non-sequential order
        element3 = StoryElement(
            element_type='climax',
            content='The hero faced the dragon...',
            position=3,
            story_id=story.id
        )
        
        element1 = StoryElement(
            element_type='introduction',
            content='Once upon a time...',
            position=1,
            story_id=story.id
        )
        
        element2 = StoryElement(
            element_type='rising_action',
            content='The journey began...',
            position=2,
            story_id=story.id
        )
        
        db.session.add_all([element3, element1, element2])
        db.session.commit()
        
        # Query elements ordered by position
        elements = StoryElement.query.filter_by(story_id=story.id).order_by(StoryElement.position).all()
        
        # Verify order
        assert len(elements) == 3
        assert elements[0].element_type == 'introduction'
        assert elements[1].element_type == 'rising_action'
        assert elements[2].element_type == 'climax'
