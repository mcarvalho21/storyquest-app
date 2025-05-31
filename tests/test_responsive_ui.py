import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import url_for

@pytest.fixture(scope="module")
def selenium_driver():
    """Setup and teardown for Selenium WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()

class TestResponsiveDesign:
    """Test suite for responsive design across different devices."""
    
    def test_homepage_desktop(self, selenium_driver, app):
        """Test homepage on desktop view (1920x1080)."""
        with app.app_context():
            url = url_for('main.index', _external=True)
        
        selenium_driver.set_window_size(1920, 1080)
        selenium_driver.get(url)
        
        # Check that the navigation is visible
        nav = selenium_driver.find_element(By.CLASS_NAME, "navbar")
        assert nav.is_displayed()
        
        # Check that the hero section is visible
        hero = selenium_driver.find_element(By.CLASS_NAME, "hero-section")
        assert hero.is_displayed()
        
        # Check that the features section is visible
        features = selenium_driver.find_element(By.CLASS_NAME, "features-section")
        assert features.is_displayed()
        
        # Check that the age groups section is visible
        age_groups = selenium_driver.find_element(By.CLASS_NAME, "age-groups-section")
        assert age_groups.is_displayed()
        
        # Check that the footer is visible
        footer = selenium_driver.find_element(By.TAG_NAME, "footer")
        assert footer.is_displayed()
    
    def test_homepage_tablet(self, selenium_driver, app):
        """Test homepage on tablet view (768x1024)."""
        with app.app_context():
            url = url_for('main.index', _external=True)
        
        selenium_driver.set_window_size(768, 1024)
        selenium_driver.get(url)
        
        # Check that the navigation is still visible
        nav = selenium_driver.find_element(By.CLASS_NAME, "navbar")
        assert nav.is_displayed()
        
        # Check that the hero section is visible and properly sized
        hero = selenium_driver.find_element(By.CLASS_NAME, "hero-section")
        assert hero.is_displayed()
        
        # Check that the features section is visible
        features = selenium_driver.find_element(By.CLASS_NAME, "features-section")
        assert features.is_displayed()
        
        # Verify that feature cards are stacked or resized appropriately
        feature_cards = selenium_driver.find_elements(By.CLASS_NAME, "feature-card")
        for card in feature_cards:
            assert card.is_displayed()
    
    def test_homepage_mobile(self, selenium_driver, app):
        """Test homepage on mobile view (375x667)."""
        with app.app_context():
            url = url_for('main.index', _external=True)
        
        selenium_driver.set_window_size(375, 667)
        selenium_driver.get(url)
        
        # Check that the mobile menu toggle is visible
        menu_toggle = selenium_driver.find_element(By.CLASS_NAME, "menu-toggle")
        assert menu_toggle.is_displayed()
        
        # Check that the main navigation is hidden or collapsed
        nav_menu = selenium_driver.find_element(By.CLASS_NAME, "nav-menu")
        assert not nav_menu.is_displayed() or "collapsed" in nav_menu.get_attribute("class")
        
        # Click the menu toggle to expand the menu
        menu_toggle.click()
        
        # Wait for the menu to expand
        WebDriverWait(selenium_driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "nav-menu"))
        )
        
        # Check that the menu is now visible
        nav_menu = selenium_driver.find_element(By.CLASS_NAME, "nav-menu")
        assert nav_menu.is_displayed()
        
        # Check that all menu items are visible
        menu_items = selenium_driver.find_elements(By.CSS_SELECTOR, ".nav-menu a")
        for item in menu_items:
            assert item.is_displayed()

class TestUserInteractions:
    """Test suite for user interactions across different devices."""
    
    def test_registration_form_desktop(self, selenium_driver, app):
        """Test registration form on desktop."""
        with app.app_context():
            url = url_for('auth_bp.register', _external=True)
        
        selenium_driver.set_window_size(1920, 1080)
        selenium_driver.get(url)
        
        # Check that all form fields are visible
        username_field = selenium_driver.find_element(By.ID, "username")
        email_field = selenium_driver.find_element(By.ID, "email")
        password_field = selenium_driver.find_element(By.ID, "password")
        age_group_select = selenium_driver.find_element(By.ID, "age_group")
        submit_button = selenium_driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        assert username_field.is_displayed()
        assert email_field.is_displayed()
        assert password_field.is_displayed()
        assert age_group_select.is_displayed()
        assert submit_button.is_displayed()
        
        # Test form validation
        submit_button.click()
        
        # Check that validation messages are shown
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input:invalid"))
        )
    
    def test_registration_form_mobile(self, selenium_driver, app):
        """Test registration form on mobile."""
        with app.app_context():
            url = url_for('auth_bp.register', _external=True)
        
        selenium_driver.set_window_size(375, 667)
        selenium_driver.get(url)
        
        # Check that all form fields are visible and properly sized
        username_field = selenium_driver.find_element(By.ID, "username")
        email_field = selenium_driver.find_element(By.ID, "email")
        password_field = selenium_driver.find_element(By.ID, "password")
        age_group_select = selenium_driver.find_element(By.ID, "age_group")
        submit_button = selenium_driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        assert username_field.is_displayed()
        assert email_field.is_displayed()
        assert password_field.is_displayed()
        assert age_group_select.is_displayed()
        assert submit_button.is_displayed()
        
        # Check that form elements are properly sized for mobile
        form_width = selenium_driver.find_element(By.TAG_NAME, "form").size['width']
        viewport_width = selenium_driver.execute_script("return window.innerWidth")
        
        # Form should take up most of the viewport width on mobile
        assert form_width >= viewport_width * 0.8
    
    def test_story_creation_form_responsive(self, selenium_driver, app, authenticated_client):
        """Test story creation form responsiveness."""
        with app.app_context():
            url = url_for('story_bp.create', _external=True)
        
        # Test on desktop
        selenium_driver.set_window_size(1920, 1080)
        selenium_driver.get(url)
        
        # Check form elements on desktop
        title_field = selenium_driver.find_element(By.ID, "title")
        description_field = selenium_driver.find_element(By.ID, "description")
        age_group_select = selenium_driver.find_element(By.ID, "age_group")
        
        assert title_field.is_displayed()
        assert description_field.is_displayed()
        assert age_group_select.is_displayed()
        
        # Test on mobile
        selenium_driver.set_window_size(375, 667)
        selenium_driver.get(url)
        
        # Check form elements on mobile
        title_field = selenium_driver.find_element(By.ID, "title")
        description_field = selenium_driver.find_element(By.ID, "description")
        age_group_select = selenium_driver.find_element(By.ID, "age_group")
        
        assert title_field.is_displayed()
        assert description_field.is_displayed()
        assert age_group_select.is_displayed()
        
        # Check that form elements are properly sized for mobile
        form_width = selenium_driver.find_element(By.TAG_NAME, "form").size['width']
        viewport_width = selenium_driver.execute_script("return window.innerWidth")
        
        # Form should take up most of the viewport width on mobile
        assert form_width >= viewport_width * 0.8

class TestAccessibility:
    """Test suite for accessibility features."""
    
    def test_keyboard_navigation(self, selenium_driver, app):
        """Test keyboard navigation on the homepage."""
        with app.app_context():
            url = url_for('main.index', _external=True)
        
        selenium_driver.get(url)
        
        # Send Tab key to navigate through elements
        body = selenium_driver.find_element(By.TAG_NAME, "body")
        body.send_keys('\ue004')  # Tab key
        
        # Check that focus is on the first focusable element (usually a link)
        active_element = selenium_driver.switch_to.active_element
        assert active_element.tag_name.lower() in ['a', 'button', 'input', 'select', 'textarea']
        
        # Continue tabbing and check that focus moves to next elements
        active_element.send_keys('\ue004')  # Tab key
        new_active_element = selenium_driver.switch_to.active_element
        assert new_active_element != active_element
    
    def test_color_contrast(self, selenium_driver, app):
        """Test color contrast for accessibility."""
        with app.app_context():
            url = url_for('main.index', _external=True)
        
        selenium_driver.get(url)
        
        # Run accessibility check using JavaScript
        # This is a simplified check - in a real environment, you might use
        # tools like axe-core or pa11y for more comprehensive testing
        contrast_issues = selenium_driver.execute_script("""
            const elements = document.querySelectorAll('*');
            const issues = [];
            
            for (const element of elements) {
                const style = window.getComputedStyle(element);
                const foreground = style.color;
                const background = style.backgroundColor;
                
                // Only check elements with text content
                if (element.textContent.trim() && 
                    foreground !== 'rgba(0, 0, 0, 0)' && 
                    background !== 'rgba(0, 0, 0, 0)') {
                    
                    // This is a simplified check - a real implementation would
                    // calculate actual contrast ratios
                    if (foreground === background) {
                        issues.push({
                            element: element.tagName,
                            text: element.textContent.substring(0, 20),
                            foreground,
                            background
                        });
                    }
                }
            }
            
            return issues;
        """)
        
        # There should be no contrast issues
        assert len(contrast_issues) == 0, f"Found contrast issues: {contrast_issues}"
    
    def test_image_alt_text(self, selenium_driver, app):
        """Test that all images have alt text."""
        with app.app_context():
            url = url_for('main.index', _external=True)
        
        selenium_driver.get(url)
        
        # Find all images
        images = selenium_driver.find_elements(By.TAG_NAME, "img")
        
        # Check that all images have alt text
        for img in images:
            alt_text = img.get_attribute("alt")
            assert alt_text is not None and alt_text != "", f"Image missing alt text: {img.get_attribute('src')}"

class TestCrossBrowserCompatibility:
    """Test suite for cross-browser compatibility.
    
    Note: In a real environment, you would run these tests on multiple browsers.
    For this example, we're simulating with Chrome only.
    """
    
    def test_homepage_rendering(self, selenium_driver, app):
        """Test homepage rendering."""
        with app.app_context():
            url = url_for('main.index', _external=True)
        
        selenium_driver.get(url)
        
        # Check that critical elements are present
        assert selenium_driver.find_element(By.CLASS_NAME, "navbar").is_displayed()
        assert selenium_driver.find_element(By.CLASS_NAME, "hero-section").is_displayed()
        assert selenium_driver.find_element(By.CLASS_NAME, "features-section").is_displayed()
        
        # Check for JavaScript errors
        js_errors = selenium_driver.execute_script("""
            return window.jsErrors || [];
        """)
        
        assert len(js_errors) == 0, f"JavaScript errors found: {js_errors}"
    
    def test_css_compatibility(self, selenium_driver, app):
        """Test CSS compatibility."""
        with app.app_context():
            url = url_for('main.index', _external=True)
        
        selenium_driver.get(url)
        
        # Check for CSS layout issues
        layout_issues = selenium_driver.execute_script("""
            const issues = [];
            const elements = document.querySelectorAll('*');
            
            for (const element of elements) {
                const rect = element.getBoundingClientRect();
                
                // Check for elements with zero width or height that should be visible
                if (element.offsetParent !== null && 
                    (rect.width === 0 || rect.height === 0) && 
                    window.getComputedStyle(element).display !== 'none' &&
                    window.getComputedStyle(element).visibility !== 'hidden') {
                    
                    issues.push({
                        element: element.tagName,
                        id: element.id,
                        class: element.className,
                        width: rect.width,
                        height: rect.height
                    });
                }
            }
            
            return issues;
        """)
        
        assert len(layout_issues) == 0, f"CSS layout issues found: {layout_issues}"
