from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from src.models import db, Story, StoryElement
import json
from datetime import datetime

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/save/<int:story_id>', methods=['POST'])
def save_progress(story_id):
    """Save user's progress in a story"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    story = Story.query.get_or_404(story_id)
    
    # Check if user owns this story
    if story.user_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Permission denied'})
    
    # Get progress data from request
    data = request.get_json()
    
    # Update story with latest progress
    story.updated_at = datetime.utcnow()
    
    # Save story content if provided
    if 'content' in data:
        story.content = json.dumps(data['content'])
    
    # Update story elements if provided
    if 'elements' in data:
        # Get existing elements
        existing_elements = {elem.position: elem for elem in 
                            StoryElement.query.filter_by(story_id=story_id).all()}
        
        # Update or create elements
        for idx, elem_data in enumerate(data['elements']):
            if idx in existing_elements:
                # Update existing element
                elem = existing_elements[idx]
                elem.element_type = elem_data['type']
                elem.content = json.dumps(elem_data['content'])
                elem.character_id = elem_data.get('character_id')
                elem.setting_id = elem_data.get('setting_id')
            else:
                # Create new element
                new_elem = StoryElement(
                    story_id=story_id,
                    element_type=elem_data['type'],
                    position=idx,
                    content=json.dumps(elem_data['content']),
                    character_id=elem_data.get('character_id'),
                    setting_id=elem_data.get('setting_id')
                )
                db.session.add(new_elem)
        
        # Remove elements that are no longer needed
        positions_to_keep = set(range(len(data['elements'])))
        for pos, elem in existing_elements.items():
            if pos not in positions_to_keep:
                db.session.delete(elem)
    
    # Save completion status if provided
    if 'is_complete' in data:
        story.is_complete = data['is_complete']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Progress saved successfully',
        'timestamp': story.updated_at.isoformat()
    })

@progress_bp.route('/resume/<int:story_id>')
def resume_progress(story_id):
    """Resume a story from saved progress"""
    if 'user_id' not in session:
        flash('Please log in to resume your story', 'warning')
        return redirect(url_for('auth.login'))
    
    story = Story.query.get_or_404(story_id)
    
    # Check if user owns this story or if it's public
    if not story.is_public and story.user_id != session['user_id']:
        flash('You do not have permission to view this story', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Get story elements
    elements = StoryElement.query.filter_by(story_id=story_id).order_by(StoryElement.position).all()
    
    # Parse content
    content = json.loads(story.content) if story.content else {}
    
    # Record that user is resuming this story
    if story.user_id == session['user_id']:
        # Could track analytics here
        pass
    
    return render_template('story/resume.html', 
                          story=story, 
                          elements=elements,
                          content=content,
                          is_owner=(story.user_id == session.get('user_id')))

@progress_bp.route('/autosave/<int:story_id>', methods=['POST'])
def autosave(story_id):
    """Automatically save story progress periodically"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    story = Story.query.get_or_404(story_id)
    
    # Check if user owns this story
    if story.user_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Permission denied'})
    
    # Get progress data from request
    data = request.get_json()
    
    # Update story with latest progress
    story.updated_at = datetime.utcnow()
    
    # Save minimal content for autosave
    if 'content' in data:
        story.content = json.dumps(data['content'])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Autosave successful',
        'timestamp': story.updated_at.isoformat()
    })
