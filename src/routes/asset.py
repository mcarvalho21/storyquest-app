from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from src.models import db, Character, Setting
import json
import os

asset_bp = Blueprint('asset', __name__)

@asset_bp.route('/characters', methods=['GET'])
def list_characters():
    """List all characters for the current user"""
    if 'user_id' not in session:
        flash('Please log in to view your characters', 'warning')
        return redirect(url_for('auth.login'))
    
    characters = Character.query.filter_by(user_id=session['user_id']).all()
    return render_template('asset/characters.html', characters=characters)

@asset_bp.route('/characters/create', methods=['GET', 'POST'])
def create_character():
    """Create a new character"""
    if 'user_id' not in session:
        flash('Please log in to create characters', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Handle character attributes
        attributes = {}
        attributes['personality'] = request.form.get('personality', '')
        attributes['appearance'] = request.form.get('appearance', '')
        attributes['likes'] = request.form.get('likes', '')
        attributes['dislikes'] = request.form.get('dislikes', '')
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename:
                # Save image
                filename = f"{session['user_id']}_{name.replace(' ', '_')}_{image.filename}"
                image_path = os.path.join('static', 'images', 'characters', filename)
                full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), image_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                image.save(full_path)
        
        # Create new character
        new_character = Character(
            name=name,
            description=description,
            attributes=json.dumps(attributes),
            image_path=image_path,
            user_id=session['user_id']
        )
        
        db.session.add(new_character)
        db.session.commit()
        
        flash('Character created successfully!', 'success')
        return redirect(url_for('asset.list_characters'))
    
    return render_template('asset/create_character.html')

@asset_bp.route('/characters/<int:character_id>/edit', methods=['GET', 'POST'])
def edit_character(character_id):
    """Edit an existing character"""
    if 'user_id' not in session:
        flash('Please log in to edit characters', 'warning')
        return redirect(url_for('auth.login'))
    
    character = Character.query.get_or_404(character_id)
    
    # Check if user owns this character
    if character.user_id != session['user_id']:
        flash('You do not have permission to edit this character', 'danger')
        return redirect(url_for('asset.list_characters'))
    
    # Parse attributes
    attributes = json.loads(character.attributes) if character.attributes else {}
    
    if request.method == 'POST':
        character.name = request.form.get('name')
        character.description = request.form.get('description')
        
        # Update attributes
        attributes['personality'] = request.form.get('personality', attributes.get('personality', ''))
        attributes['appearance'] = request.form.get('appearance', attributes.get('appearance', ''))
        attributes['likes'] = request.form.get('likes', attributes.get('likes', ''))
        attributes['dislikes'] = request.form.get('dislikes', attributes.get('dislikes', ''))
        character.attributes = json.dumps(attributes)
        
        # Handle image upload
        if 'image' in request.files:
            image = request.files['image']
            if image.filename:
                # Delete old image if exists
                if character.image_path:
                    old_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), character.image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # Save new image
                filename = f"{session['user_id']}_{character.name.replace(' ', '_')}_{image.filename}"
                image_path = os.path.join('static', 'images', 'characters', filename)
                full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), image_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                image.save(full_path)
                character.image_path = image_path
        
        db.session.commit()
        flash('Character updated successfully!', 'success')
        return redirect(url_for('asset.list_characters'))
    
    return render_template('asset/edit_character.html', character=character, attributes=attributes)

@asset_bp.route('/settings', methods=['GET'])
def list_settings():
    """List all settings for the current user"""
    if 'user_id' not in session:
        flash('Please log in to view your settings', 'warning')
        return redirect(url_for('auth.login'))
    
    settings = Setting.query.filter_by(user_id=session['user_id']).all()
    return render_template('asset/settings.html', settings=settings)

@asset_bp.route('/settings/create', methods=['GET', 'POST'])
def create_setting():
    """Create a new story setting"""
    if 'user_id' not in session:
        flash('Please log in to create settings', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Handle setting attributes
        attributes = {}
        attributes['time_period'] = request.form.get('time_period', '')
        attributes['location_type'] = request.form.get('location_type', '')
        attributes['mood'] = request.form.get('mood', '')
        attributes['weather'] = request.form.get('weather', '')
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename:
                # Save image
                filename = f"{session['user_id']}_{name.replace(' ', '_')}_{image.filename}"
                image_path = os.path.join('static', 'images', 'settings', filename)
                full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), image_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                image.save(full_path)
        
        # Create new setting
        new_setting = Setting(
            name=name,
            description=description,
            attributes=json.dumps(attributes),
            image_path=image_path,
            user_id=session['user_id']
        )
        
        db.session.add(new_setting)
        db.session.commit()
        
        flash('Setting created successfully!', 'success')
        return redirect(url_for('asset.list_settings'))
    
    return render_template('asset/create_setting.html')

@asset_bp.route('/settings/<int:setting_id>/edit', methods=['GET', 'POST'])
def edit_setting(setting_id):
    """Edit an existing setting"""
    if 'user_id' not in session:
        flash('Please log in to edit settings', 'warning')
        return redirect(url_for('auth.login'))
    
    setting = Setting.query.get_or_404(setting_id)
    
    # Check if user owns this setting
    if setting.user_id != session['user_id']:
        flash('You do not have permission to edit this setting', 'danger')
        return redirect(url_for('asset.list_settings'))
    
    # Parse attributes
    attributes = json.loads(setting.attributes) if setting.attributes else {}
    
    if request.method == 'POST':
        setting.name = request.form.get('name')
        setting.description = request.form.get('description')
        
        # Update attributes
        attributes['time_period'] = request.form.get('time_period', attributes.get('time_period', ''))
        attributes['location_type'] = request.form.get('location_type', attributes.get('location_type', ''))
        attributes['mood'] = request.form.get('mood', attributes.get('mood', ''))
        attributes['weather'] = request.form.get('weather', attributes.get('weather', ''))
        setting.attributes = json.dumps(attributes)
        
        # Handle image upload
        if 'image' in request.files:
            image = request.files['image']
            if image.filename:
                # Delete old image if exists
                if setting.image_path:
                    old_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), setting.image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # Save new image
                filename = f"{session['user_id']}_{setting.name.replace(' ', '_')}_{image.filename}"
                image_path = os.path.join('static', 'images', 'settings', filename)
                full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), image_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                image.save(full_path)
                setting.image_path = image_path
        
        db.session.commit()
        flash('Setting updated successfully!', 'success')
        return redirect(url_for('asset.list_settings'))
    
    return render_template('asset/edit_setting.html', setting=setting, attributes=attributes)
