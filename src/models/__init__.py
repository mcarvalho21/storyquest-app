from src.models.user import db, User
from src.models.story import Story
from src.models.character import Character
from src.models.setting import Setting
from src.models.story_element import StoryElement
from src.models.achievement import Achievement
from src.models.progress import Progress
from src.models.challenge import Challenge

# Import all models here to make them available when importing from src.models
__all__ = ['db', 'User', 'Story', 'Character', 'Setting', 'StoryElement', 'Achievement', 'Progress', 'Challenge']
