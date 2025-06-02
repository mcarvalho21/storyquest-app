import pytest
from flask import url_for
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(scope="module")
def selenium_driver():
    """Setup and teardown for Selenium WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()

def test_homepage_responsive(selenium_driver, app):
    """Test that the homepage is responsive."""
    with app.app_context():
        url = url_for('main.index', _external=True)
    
    # Test desktop view
    selenium_driver.set_window_size(1920, 1080)
    selenium_driver.get(url)
    
    # Check that the navigation is visible
    nav = selenium_driver.find_element(By.CLASS_NAME, "navbar")
    assert nav.is_displayed()
    
    # Check that the hero section is visible
    hero = selenium_driver.find_element(By.CLASS_NAME, "hero-section")
    assert hero.is_displayed()
    
    # Test tablet view
    selenium_driver.set_window_size(768, 1024)
    selenium_driver.get(url)
    
    # Check that the navigation is still visible
    nav = selenium_driver.find_element(By.CLASS_NAME, "navbar")
    assert nav.is_displayed()
    
    # Test mobile view
    selenium_driver.set_window_size(375, 667)
    selenium_driver.get(url)
    
    # Check that the mobile menu toggle is visible
    menu_toggle = selenium_driver.find_element(By.CLASS_NAME, "menu-toggle")
    assert menu_toggle.is_displayed()

def test_registration_form_validation(selenium_driver, app):
    """Test client-side validation on the registration form."""
    with app.app_context():
        url = url_for('auth_bp.register', _external=True)
    
    selenium_driver.get(url)
    
    # Try to submit without filling required fields
    submit_button = selenium_driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()
    
    # Check that validation messages are shown
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input:invalid"))
    )
    
    # Fill in the form
    username_field = selenium_driver.find_element(By.ID, "username")
    email_field = selenium_driver.find_element(By.ID, "email")
    password_field = selenium_driver.find_element(By.ID, "password")
    
    username_field.send_keys("seleniumtest")
    email_field.send_keys("selenium@example.com")
    password_field.send_keys("password123")
    
    # Submit the form
    submit_button.click()
    
    # Wait for redirect to dashboard
    WebDriverWait(selenium_driver, 10).until(
        EC.url_contains("dashboard")
    )
    
    # Check that we're on the dashboard page
    assert "dashboard" in selenium_driver.current_url

def test_story_creation_workflow(selenium_driver, app, authenticated_client):
    """Test the complete story creation workflow."""
    # This test requires an authenticated session
    # We'll need to set cookies from the authenticated_client
    
    with app.app_context():
        dashboard_url = url_for('dashboard_bp.index', _external=True)
        
    selenium_driver.get(dashboard_url)
    
    # Find and click the "Create New Story" button
    create_story_button = selenium_driver.find_element(By.LINK_TEXT, "Create New Story")
    create_story_button.click()
    
    # Wait for the story creation form
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_element_located((By.ID, "story-form"))
    )
    
    # Fill in the story details
    title_field = selenium_driver.find_element(By.ID, "title")
    description_field = selenium_driver.find_element(By.ID, "description")
    
    title_field.send_keys("Selenium Test Story")
    description_field.send_keys("This is a story created by Selenium for testing")
    
    # Submit the form
    submit_button = selenium_driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()
    
    # Wait for redirect to the story editor
    WebDriverWait(selenium_driver, 10).until(
        EC.url_contains("edit")
    )
    
    # Check that we're on the story editor page
    assert "edit" in selenium_driver.current_url
    
    # Check that the story title is displayed
    story_title = selenium_driver.find_element(By.CSS_SELECTOR, "h1")
    assert "Selenium Test Story" in story_title.text
