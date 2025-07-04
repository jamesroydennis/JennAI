#!/usr/bin/env python
"""
Test Brand Assets and Content
=============================

This test module validates that all required brand assets and content are present
and properly configured. This ensures the architect, designer, and other personas
have access to the brand materials they need.
"""

import sys
from pathlib import Path
import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import config


class TestBrandAssets:
    """Test that all brand assets are present and accessible."""
    
    def test_brand_directory_exists(self):
        """Test that the brand directory exists."""
        brand_dir = config.PRESENTATION_DIR / "brand"
        assert brand_dir.exists(), f"Brand directory does not exist at {brand_dir}"
        assert brand_dir.is_dir(), f"Brand path exists but is not a directory: {brand_dir}"
    
    def test_mission_statement_exists(self):
        """Test that mission statement exists and has content."""
        mission_file = config.PRESENTATION_DIR / "brand" / "mission.txt"
        assert mission_file.exists(), f"Mission statement file does not exist: {mission_file}"
        
        content = mission_file.read_text(encoding='utf-8').strip()
        assert content, "Mission statement file exists but is empty"
        assert len(content) > 10, "Mission statement appears too short to be meaningful"
    
    def test_vision_statement_exists(self):
        """Test that vision statement exists and has content."""
        vision_file = config.PRESENTATION_DIR / "brand" / "vision.md"
        assert vision_file.exists(), f"Vision statement file does not exist: {vision_file}"
        
        content = vision_file.read_text(encoding='utf-8').strip()
        assert content, "Vision statement file exists but is empty"
        assert len(content) > 50, "Vision statement appears too short to be meaningful"
        # Check for markdown formatting
        assert any(marker in content for marker in ['#', '##', '###', '**', '*']), \
            "Vision file should contain markdown formatting"
    
    def test_brand_theme_exists(self):
        """Test that brand theme SCSS file exists."""
        theme_file = config.PRESENTATION_DIR / "brand" / "theme.scss"
        assert theme_file.exists(), f"Brand theme file does not exist: {theme_file}"
        
        content = theme_file.read_text(encoding='utf-8')
        assert content, "Theme file exists but is empty"
        # Check for SCSS variables
        assert "$theme-" in content, "Theme file should contain theme variables"
        assert "$font-" in content, "Theme file should contain font variables"
    
    def test_logo_exists(self):
        """Test that logo file exists."""
        logo_file = config.PRESENTATION_DIR / "brand" / "jennai-logo.png"
        assert logo_file.exists(), f"Logo file does not exist: {logo_file}"
        assert logo_file.stat().st_size > 1000, "Logo file appears too small to be a valid image"
    
    def test_favicon_assets_exist(self):
        """Test that favicon assets exist."""
        favicon_dir = config.PRESENTATION_DIR / "brand" / "favicon_io"
        assert favicon_dir.exists(), f"Favicon directory does not exist: {favicon_dir}"
        
        required_favicon_files = [
            "favicon.ico",
            "favicon-16x16.png",
            "favicon-32x32.png",
            "apple-touch-icon.png"
        ]
        
        for favicon_file in required_favicon_files:
            favicon_path = favicon_dir / favicon_file
            assert favicon_path.exists(), f"Required favicon file missing: {favicon_path}"
    
    def test_brand_images_exist(self):
        """Test that key brand images exist."""
        brand_dir = config.PRESENTATION_DIR / "brand"
        
        # These are the key images that should be available for the website
        key_images = [
            "ai.jpg",
            "background.jpg",
            "circuit-dark.jpg",
            "person.jpg"
        ]
        
        for image_name in key_images:
            image_path = brand_dir / image_name
            assert image_path.exists(), f"Key brand image missing: {image_path}"
            assert image_path.stat().st_size > 5000, f"Image file appears too small: {image_path}"


class TestBrandIntegration:
    """Test that brand assets are properly integrated into the Flask app."""
    
    def test_flask_brand_routes_configured(self):
        """Test that Flask brand routes can access brand assets."""
        from src.presentation.api_server.flask_app.routes.brand_routes import brand_bp
        
        # Check that the blueprint is properly configured
        assert brand_bp.name == 'brand', "Brand blueprint not properly named"
        assert brand_bp.url_prefix == '/brand', "Brand blueprint URL prefix incorrect"
    
    def test_main_routes_load_brand_content(self):
        """Test that main routes can load brand content."""
        from src.presentation.api_server.flask_app.routes.main_routes import load_brand_content
        
        # Test that the function works and returns expected content
        brand_content = load_brand_content()
        
        assert isinstance(brand_content, dict), "Brand content should be a dictionary"
        assert 'mission_statement' in brand_content, "Mission statement should be in brand content"
        assert 'vision_statement' in brand_content, "Vision statement should be in brand content"
        
        # Check that content is actually loaded
        assert brand_content['mission_statement'], "Mission statement should not be empty"
        assert brand_content['vision_statement'], "Vision statement should not be empty"
    
    def test_flask_css_compiled(self):
        """Test that Flask CSS has been compiled from SCSS."""
        css_file = config.PRESENTATION_DIR / "api_server" / "flask_app" / "static" / "css" / "main.css"
        
        # This test will fail if SCSS hasn't been compiled, forcing proper setup
        assert css_file.exists(), f"Compiled CSS file does not exist: {css_file}. Run 'python admin/compile_scss.py --target flask'"
        
        content = css_file.read_text(encoding='utf-8')
        assert content.strip(), "CSS file exists but is empty"
        assert "body" in content, "CSS file should contain body styles"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
