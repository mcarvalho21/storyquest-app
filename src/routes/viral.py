from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from src.models import db, Story, User
import json
from datetime import datetime

viral_bp = Blueprint('viral', __name__)

@viral_bp.route('/gallery')
def gallery():
    """Public gallery of shared stories"""
    # Get public stories, newest first
    public_stories = Story.query.filter_by(is_public=True).order_by(Story.updated_at.desc()).limit(20).all()
    
    # Get featured stories (could be curated by admins or based on popularity)
    featured_stories = Story.query.filter_by(is_public=True).order_by(Story.updated_at.desc()).limit(5).all()
    
    return render_template('viral/gallery.html', 
                          public_stories=public_stories,
                          featured_stories=featured_stories)

@viral_bp.route('/challenge')
def challenges():
    """Weekly storytelling challenges"""
    # In a real app, these would be from a database
    current_challenges = [
        {
            'id': 1,
            'title': 'Space Adventure',
            'description': 'Create a story about exploring a new planet!',
            'end_date': '2025-06-07',
            'age_groups': ['4-6', '7-9', '10-12']
        },
        {
            'id': 2,
            'title': 'Magical Forest',
            'description': 'Tell a tale about magical creatures in an enchanted forest.',
            'end_date': '2025-06-14',
            'age_groups': ['4-6', '7-9', '10-12']
        },
        {
            'id': 3,
            'title': 'Ocean Adventure',
            'description': 'Create an underwater adventure with sea creatures!',
            'end_date': '2025-06-21',
            'age_groups': ['7-9', '10-12']
        }
    ]
    
    return render_template('viral/challenges.html', challenges=current_challenges)

@viral_bp.route('/share/<int:story_id>', methods=['GET', 'POST'])
def share_story(story_id):
    """Share a story on social media or via email"""
    if 'user_id' not in session:
        flash('Please log in to share stories', 'warning')
        return redirect(url_for('auth.login'))
    
    story = Story.query.get_or_404(story_id)
    
    # Check if user owns this story
    if story.user_id != session['user_id']:
        flash('You do not have permission to share this story', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        # Make story public if it's not already
        if not story.is_public:
            story.is_public = True
            db.session.commit()
        
        share_method = request.form.get('share_method')
        
        # Generate share URL
        share_url = url_for('story.view', story_id=story_id, _external=True)
        
        if share_method == 'email':
            # In a real app, this would send an email
            recipient = request.form.get('recipient')
            flash(f'Story shared via email to {recipient}!', 'success')
            return redirect(url_for('story.view', story_id=story_id))
        
        elif share_method == 'social':
            # In a real app, this would integrate with social media APIs
            platform = request.form.get('platform')
            flash(f'Story shared on {platform}!', 'success')
            return redirect(url_for('story.view', story_id=story_id))
    
    return render_template('viral/share.html', story=story)

@viral_bp.route('/parental-controls', methods=['GET', 'POST'])
def parental_controls():
    """Parental control settings"""
    if 'user_id' not in session:
        flash('Please log in to access parental controls', 'warning')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        # In a real app, these settings would be stored in a separate table
        settings = {
            'content_filter': request.form.get('content_filter', 'strict'),
            'sharing_permission': request.form.get('sharing_permission', 'ask'),
            'collaboration': request.form.get('collaboration', 'friends'),
            'max_daily_time': request.form.get('max_daily_time', '60')
        }
        
        # Store settings as JSON in user attributes or a separate table
        # For this demo, we'll just show a success message
        flash('Parental control settings updated successfully!', 'success')
        return redirect(url_for('dashboard.index'))
    
    # In a real app, we would retrieve the actual settings
    current_settings = {
        'content_filter': 'strict',
        'sharing_permission': 'ask',
        'collaboration': 'friends',
        'max_daily_time': '60'
    }
    
    return render_template('viral/parental_controls.html', settings=current_settings)

@viral_bp.route('/seasonal')
def seasonal_themes():
    """Seasonal themes and elements"""
    # Determine current season/holiday
    # For demo purposes, we'll hardcode summer
    current_season = 'summer'
    
    seasonal_elements = {
        'summer': {
            'characters': ['Surfer', 'Lifeguard', 'Ice Cream Vendor'],
            'settings': ['Beach', 'Waterpark', 'Summer Camp'],
            'plot_elements': ['Swimming Race', 'Sandcastle Contest', 'Summer Storm']
        },
        'halloween': {
            'characters': ['Friendly Ghost', 'Silly Witch', 'Pumpkin Person'],
            'settings': ['Pumpkin Patch', 'Costume Party', 'Trick-or-Treat Lane'],
            'plot_elements': ['Candy Hunt', 'Costume Contest', 'Spooky (but not scary) Mystery']
        },
        'winter': {
            'characters': ['Snowman', 'Reindeer', 'Gift Giver'],
            'settings': ['Snowy Forest', 'Ice Skating Rink', 'Cozy Cabin'],
            'plot_elements': ['Snowball Fight', 'Winter Festival', 'Lost Mitten Adventure']
        }
    }
    
    return render_template('viral/seasonal.html', 
                          season=current_season, 
                          elements=seasonal_elements[current_season])
