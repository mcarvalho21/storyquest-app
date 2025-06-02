from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from src.models import db, Story, Challenge, Achievement, User
from datetime import datetime, timedelta
import logging

# Get logger
logger = logging.getLogger('storyquest')

viral_bp = Blueprint('viral_bp', __name__)

@viral_bp.route('/share/<int:story_id>', methods=['GET', 'POST'])
def share_story(story_id):
    """Share a story on social media"""
    if 'user_id' not in session:
        flash('Please log in to share stories', 'warning')
        return redirect(url_for('auth_bp.login'))
    
    story = Story.get_by_id(story_id)
    if not story:
        flash('Story not found', 'danger')
        return redirect(url_for('dashboard_bp.index'))
    
    # Check if user owns this story
    if story.user_id != session['user_id']:
        flash('You do not have permission to share this story', 'danger')
        return redirect(url_for('dashboard_bp.index'))
    
    # Handle POST request for sharing
    if request.method == 'POST':
        share_type = request.form.get('share_type', 'public')
        share_message = request.form.get('share_message', '')
        
        # Set story as public
        story.is_public = True
        story.is_shared = True
        story.share_message = share_message
        story.share_date = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Story {story_id} shared by user {session['user_id']} with type {share_type}")
        
        # Check if user earns an achievement for sharing
        check_sharing_achievements(session['user_id'])
        
        flash('Your story has been shared successfully!', 'success')
    
    # Generate share URL
    share_url = url_for('viral_bp.view_shared_story', story_id=story_id, _external=True)
    
    return render_template('viral/share.html', story=story, share_url=share_url)

@viral_bp.route('/shared/story/<int:story_id>')
def view_shared_story(story_id):
    """View a shared story"""
    story = Story.get_by_id(story_id)
    if not story:
        flash('Story not found', 'danger')
        return redirect(url_for('main.index'))
    
    # Check if story is public
    if not story.is_public:
        flash('This story is not available for public viewing', 'warning')
        return redirect(url_for('main.index'))
    
    # Increment view count
    story.view_count = story.view_count + 1 if story.view_count else 1
    db.session.commit()
    
    return render_template('viral/view_shared_story.html', story=story)

@viral_bp.route('/challenges')
def challenges():
    """Display weekly challenges"""
    # Get active challenges
    active_challenges = Challenge.query.filter(
        Challenge.start_date <= datetime.utcnow(),
        Challenge.end_date >= datetime.utcnow(),
        Challenge.is_active == True
    ).all()
    
    # Get upcoming challenges
    upcoming_challenges = Challenge.query.filter(
        Challenge.start_date > datetime.utcnow(),
        Challenge.is_active == True
    ).order_by(Challenge.start_date).limit(3).all()
    
    # Get past challenges
    past_challenges = Challenge.query.filter(
        Challenge.end_date < datetime.utcnow()
    ).order_by(Challenge.end_date.desc()).limit(5).all()
    
    return render_template('viral/challenges.html', 
                          active_challenges=active_challenges,
                          upcoming_challenges=upcoming_challenges,
                          past_challenges=past_challenges)

@viral_bp.route('/challenge/<int:challenge_id>')
def view_challenge(challenge_id):
    """View a specific challenge"""
    challenge = db.session.get(Challenge, challenge_id)
    if not challenge:
        flash('Challenge not found', 'danger')
        return redirect(url_for('viral_bp.challenges'))
    
    # Get stories submitted for this challenge
    stories = Story.query.filter_by(challenge_id=challenge_id, is_public=True).all()
    
    # Check if user is logged in
    user_id = session.get('user_id')
    user_stories = []
    if user_id:
        # Get user's stories that could be submitted
        user_stories = Story.query.filter_by(
            user_id=user_id,
            challenge_id=None
        ).all()
    
    return render_template('viral/challenge_detail.html', 
                          challenge=challenge, 
                          stories=stories,
                          user_stories=user_stories,
                          now=datetime.utcnow())

@viral_bp.route('/submit_challenge', methods=['POST'])
def submit_to_challenge():
    """Submit a story to a challenge"""
    if 'user_id' not in session:
        flash('Please log in to submit to challenges', 'warning')
        return redirect(url_for('auth_bp.login'))
    
    challenge_id = request.form.get('challenge_id')
    story_id = request.form.get('story_id')
    
    challenge = db.session.get(Challenge, challenge_id)
    if not challenge:
        flash('Challenge not found', 'danger')
        return redirect(url_for('viral_bp.challenges'))
        
    story = Story.get_by_id(story_id)
    if not story:
        flash('Story not found', 'danger')
        return redirect(url_for('dashboard_bp.index'))
    
    # Check if user owns this story
    if story.user_id != session['user_id']:
        flash('You do not have permission to submit this story', 'danger')
        return redirect(url_for('dashboard_bp.index'))
    
    # Check if challenge is still active
    if challenge.end_date < datetime.utcnow():
        flash('This challenge has ended', 'warning')
        return redirect(url_for('viral_bp.challenges'))
    
    # Submit story to challenge
    story.challenge_id = challenge_id
    story.is_public = True  # Make story public when submitting to challenge
    story.submission_date = datetime.utcnow()
    db.session.commit()
    
    logger.info(f"Story {story_id} submitted to challenge {challenge_id} by user {session['user_id']}")
    
    # Check if user earns an achievement for submitting to a challenge
    check_challenge_achievements(session['user_id'])
    
    flash('Story submitted to challenge successfully!', 'success')
    return redirect(url_for('viral_bp.view_challenge', challenge_id=challenge_id))

@viral_bp.route('/leaderboard')
def leaderboard():
    """Display user leaderboard"""
    # Get users with the most points from achievements
    top_users = db.session.query(
        User, db.func.sum(Achievement.points).label('total_points')
    ).join(User.achievements).group_by(User.id).order_by(db.desc('total_points')).limit(10).all()
    
    # Get users with the most stories
    most_stories = db.session.query(
        User, db.func.count(Story.id).label('story_count')
    ).join(Story).group_by(User.id).order_by(db.desc('story_count')).limit(10).all()
    
    # Get users with the most challenge wins
    challenge_winners = db.session.query(
        User, db.func.count(Story.id).label('win_count')
    ).join(Story).filter(Story.is_challenge_winner == True).group_by(User.id).order_by(db.desc('win_count')).limit(10).all()
    
    return render_template('viral/leaderboard.html', 
                          top_users=top_users,
                          most_stories=most_stories,
                          challenge_winners=challenge_winners)

@viral_bp.route('/featured')
def featured_stories():
    """Display featured stories"""
    # Get featured stories (public stories with most views/likes)
    featured = Story.get_featured_stories(6)
    
    return render_template('viral/featured.html', featured_stories=featured)

@viral_bp.route('/story/<int:story_id>/like', methods=['POST'])
def like_story(story_id):
    """Like a story"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    user_id = session['user_id']
    story = Story.get_by_id(story_id)
    if not story:
        return jsonify({'success': False, 'error': 'Story not found'})
    
    # Check if user has already liked this story
    # In a real app, we would have a likes table to track this
    # For now, we'll just increment the like count
    
    story.like_count = story.like_count + 1 if story.like_count else 1
    db.session.commit()
    
    logger.info(f"Story {story_id} liked by user {user_id}")
    
    # Check if story author earns an achievement for likes
    if story.like_count in [10, 50, 100]:
        check_like_achievements(story.user_id, story.like_count)
    
    return jsonify({'success': True, 'likes': story.like_count})

@viral_bp.route('/shared')
def shared_stories():
    """Display shared stories"""
    # Get shared stories
    shared_stories = Story.query.filter_by(is_public=True, is_shared=True).order_by(Story.share_date.desc() if Story.share_date else Story.updated_at.desc()).all()
    
    # Debug logging
    logger.debug(f"Shared stories count: {len(shared_stories)}")
    for story in shared_stories:
        logger.debug(f"Shared story: {story.id} - {story.title} - Public: {story.is_public} - Shared: {story.is_shared}")
    
    return render_template('viral/shared.html', shared_stories=shared_stories)

@viral_bp.route('/achievements')
def achievements():
    """Display user achievements"""
    if 'user_id' not in session:
        flash('Please log in to view your achievements', 'warning')
        return redirect(url_for('auth_bp.login'))
    
    user = User.get_by_id(session['user_id'])
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    # Get available achievements that user hasn't earned yet
    available_achievements = Achievement.get_available_achievements(user)
    
    # Get user's progress toward achievements
    progress = {}
    
    # Story count achievements
    story_count = Story.query.filter_by(user_id=user.id).count()
    progress['story_count'] = story_count
    
    # Challenge participation
    challenge_count = Story.query.filter(
        Story.user_id == user.id,
        Story.challenge_id != None
    ).count()
    progress['challenge_count'] = challenge_count
    
    # Sharing count
    sharing_count = Story.query.filter_by(
        user_id=user.id,
        is_shared=True
    ).count()
    progress['sharing_count'] = sharing_count
    
    return render_template('viral/achievements.html', 
                          user=user,
                          available_achievements=available_achievements,
                          progress=progress)

@viral_bp.route('/award_achievement', methods=['POST'])
def award_achievement():
    """Award an achievement to a user"""
    if 'user_id' not in session:
        flash('Please log in to manage achievements', 'warning')
        return redirect(url_for('auth_bp.login'))
    
    user_id = request.form.get('user_id')
    achievement_id = request.form.get('achievement_id')
    
    # Check if user has permission (admin or self)
    if int(user_id) != session['user_id'] and not session.get('is_admin'):
        flash('You do not have permission to award achievements', 'danger')
        return redirect(url_for('dashboard_bp.index'))
    
    user = User.get_by_id(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('dashboard_bp.index'))
        
    achievement = Achievement.get_by_id(achievement_id)
    if not achievement:
        flash('Achievement not found', 'danger')
        return redirect(url_for('viral_bp.achievements'))
    
    # Check if user already has this achievement
    if achievement in user.achievements:
        flash('User already has this achievement', 'info')
    else:
        user.achievements.append(achievement)
        db.session.commit()
        logger.info(f"Achievement {achievement_id} awarded to user {user_id}")
        flash('Achievement awarded successfully!', 'success')
    
    return redirect(url_for('viral_bp.achievements'))

# Helper functions for achievement checks

def check_sharing_achievements(user_id):
    """Check and award achievements related to story sharing"""
    user = User.get_by_id(user_id)
    if not user:
        logger.error(f"User {user_id} not found when checking sharing achievements")
        return
    
    # Count how many stories the user has shared
    sharing_count = Story.query.filter_by(
        user_id=user_id,
        is_shared=True
    ).count()
    
    # Award achievements based on sharing count
    if sharing_count == 1:
        award_achievement_by_name(user, "First Share")
    elif sharing_count == 5:
        award_achievement_by_name(user, "Sharing Enthusiast")
    elif sharing_count == 10:
        award_achievement_by_name(user, "Social Storyteller")

def check_challenge_achievements(user_id):
    """Check and award achievements related to challenge participation"""
    user = User.get_by_id(user_id)
    if not user:
        logger.error(f"User {user_id} not found when checking challenge achievements")
        return
    
    # Count how many challenges the user has participated in
    challenge_count = Story.query.filter(
        Story.user_id == user_id,
        Story.challenge_id != None
    ).count()
    
    # Award achievements based on challenge count
    if challenge_count == 1:
        award_achievement_by_name(user, "Challenge Accepted")
    elif challenge_count == 5:
        award_achievement_by_name(user, "Challenge Seeker")
    elif challenge_count == 10:
        award_achievement_by_name(user, "Challenge Master")

def check_like_achievements(user_id, like_count):
    """Check and award achievements related to story likes"""
    user = User.get_by_id(user_id)
    if not user:
        logger.error(f"User {user_id} not found when checking like achievements")
        return
    
    # Award achievements based on like count
    if like_count == 10:
        award_achievement_by_name(user, "Popular Story")
    elif like_count == 50:
        award_achievement_by_name(user, "Trending Story")
    elif like_count == 100:
        award_achievement_by_name(user, "Viral Story")

def award_achievement_by_name(user, achievement_name):
    """Award an achievement to a user by achievement name"""
    achievement = Achievement.get_by_name(achievement_name)
    
    if not achievement:
        logger.warning(f"Attempted to award non-existent achievement: {achievement_name}")
        return False
    
    # Check if user already has this achievement
    if achievement in user.achievements:
        return False
    
    user.achievements.append(achievement)
    db.session.commit()
    logger.info(f"Achievement '{achievement_name}' awarded to user {user.id}")
    return True
