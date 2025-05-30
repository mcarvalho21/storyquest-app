from flask import Blueprint, render_template, request, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Display the homepage."""
    return render_template('main/index.html')

@main_bp.route('/explore')
def explore():
    """Display the explore page."""
    return render_template('main/explore.html')

@main_bp.route('/gallery')
def gallery():
    """Display the story gallery."""
    return render_template('main/gallery.html')

@main_bp.route('/challenges')
def challenges():
    """Display the weekly challenges."""
    return render_template('main/challenges.html')

@main_bp.route('/how-it-works')
def how_it_works():
    """Display the how it works page."""
    return render_template('main/how_it_works.html')

@main_bp.route('/about')
def about():
    """Display the about page."""
    return render_template('main/about.html')

@main_bp.route('/privacy')
def privacy():
    """Display the privacy policy."""
    return render_template('main/privacy.html')

@main_bp.route('/parental-controls')
def parental_controls():
    """Display the parental controls page."""
    return render_template('main/parental_controls.html')
