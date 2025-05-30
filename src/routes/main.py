from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage for the storytelling app"""
    return render_template('main/index.html')

@main_bp.route('/about')
def about():
    """About page with information about the app"""
    return render_template('main/about.html')

@main_bp.route('/how-it-works')
def how_it_works():
    """Tutorial page explaining how to use the app"""
    return render_template('main/how_it_works.html')

@main_bp.route('/age-select', methods=['GET', 'POST'])
def age_select():
    """Age selection page to customize experience"""
    if request.method == 'POST':
        age_group = request.form.get('age_group')
        if 'user_id' in session:
            # If logged in, save preference to user profile
            # This would update the user model in a real implementation
            session['age_group'] = age_group
            return redirect(url_for('dashboard.index'))
        else:
            # If not logged in, just store in session
            session['age_group'] = age_group
            return redirect(url_for('main.index'))
    
    return render_template('main/age_select.html')

@main_bp.route('/explore')
def explore():
    """Explore page with featured stories and elements"""
    # This would fetch from database in a real implementation
    featured_content = {
        'stories': [
            {'id': 1, 'title': 'The Magic Forest', 'description': 'An adventure in an enchanted forest'},
            {'id': 2, 'title': 'Space Explorers', 'description': 'Journey to the stars'},
            {'id': 3, 'title': 'Ocean Friends', 'description': 'Underwater adventures with sea creatures'}
        ],
        'characters': [
            {'id': 1, 'name': 'Captain Brave', 'description': 'A courageous explorer'},
            {'id': 2, 'name': 'Luna the Wizard', 'description': 'A wise and magical wizard'},
            {'id': 3, 'name': 'Bubbles the Dolphin', 'description': 'A friendly and helpful dolphin'}
        ],
        'settings': [
            {'id': 1, 'name': 'Enchanted Castle', 'description': 'A magical castle with secrets'},
            {'id': 2, 'name': 'Pirate Ship', 'description': 'A vessel for adventure on the high seas'},
            {'id': 3, 'name': 'Dinosaur Island', 'description': 'An island where dinosaurs still roam'}
        ]
    }
    
    return render_template('main/explore.html', featured=featured_content)
