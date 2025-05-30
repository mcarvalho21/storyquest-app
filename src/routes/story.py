from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from src.models import db, Story, Character, Setting, StoryElement
import json
from datetime import datetime

story_bp = Blueprint('story', __name__)

@story_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new story"""
    if 'user_id' not in session:
        flash('Please log in to create a story', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        age_group = request.form.get('age_group', session.get('age_group'))
        
        # Create new story
        new_story = Story(
            title=title,
            description=description,
            age_group=age_group,
            user_id=session['user_id']
        )
        
        db.session.add(new_story)
        db.session.commit()
        
        flash('Story created successfully!', 'success')
        return redirect(url_for('story.edit', story_id=new_story.id))
    
    return render_template('story/create.html')

@story_bp.route('/<int:story_id>/edit', methods=['GET', 'POST'])
def edit(story_id):
    """Edit an existing story"""
    if 'user_id' not in session:
        flash('Please log in to edit stories', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get the story
    story = Story.query.get_or_404(story_id)
    
    # Check if user owns this story
    if story.user_id != session['user_id']:
        flash('You do not have permission to edit this story', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Get story elements
    elements = StoryElement.query.filter_by(story_id=story_id).order_by(StoryElement.position).all()
    
    # Get available characters and settings
    characters = Character.query.filter_by(user_id=session['user_id']).all()
    settings = Setting.query.filter_by(user_id=session['user_id']).all()
    
    if request.method == 'POST':
        # Update story details
        story.title = request.form.get('title')
        story.description = request.form.get('description')
        story.updated_at = datetime.utcnow()
        
        # Handle story elements update (from AJAX)
        if request.is_json:
            data = request.get_json()
            if 'elements' in data:
                # Clear existing elements
                StoryElement.query.filter_by(story_id=story_id).delete()
                
                # Add new elements
                for idx, elem in enumerate(data['elements']):
                    new_element = StoryElement(
                        story_id=story_id,
                        element_type=elem['type'],
                        position=idx,
                        content=json.dumps(elem['content']),
                        character_id=elem.get('character_id'),
                        setting_id=elem.get('setting_id')
                    )
                    db.session.add(new_element)
                
                # Mark story as complete if specified
                if 'is_complete' in data:
                    story.is_complete = data['is_complete']
                
                db.session.commit()
                return jsonify({'success': True})
        
        db.session.commit()
        flash('Story updated successfully!', 'success')
        return redirect(url_for('story.view', story_id=story_id))
    
    return render_template('story/edit.html', 
                          story=story, 
                          elements=elements,
                          characters=characters,
                          settings=settings)

@story_bp.route('/<int:story_id>/view')
def view(story_id):
    """View a story"""
    story = Story.query.get_or_404(story_id)
    
    # Check if story is public or user owns it
    if not story.is_public and ('user_id' not in session or story.user_id != session['user_id']):
        flash('This story is private', 'warning')
        return redirect(url_for('main.index'))
    
    # Get story elements
    elements = StoryElement.query.filter_by(story_id=story_id).order_by(StoryElement.position).all()
    
    return render_template('story/view.html', story=story, elements=elements)

@story_bp.route('/<int:story_id>/share', methods=['POST'])
def share(story_id):
    """Share a story publicly"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    story = Story.query.get_or_404(story_id)
    
    # Check if user owns this story
    if story.user_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Permission denied'})
    
    # Toggle public status
    story.is_public = not story.is_public
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'is_public': story.is_public,
        'share_url': url_for('story.view', story_id=story_id, _external=True) if story.is_public else None
    })
