"""
Test Brand Integration Across All Personas

This test verifies that all personas (architect, contractor, constructor, designer)
can correctly access and use the brand assets located at src/presentation/brand.
"""
import pytest
from pathlib import Path
import subprocess
import sys

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import config


class TestBrandIntegration:
    """Test that all personas can access the brand correctly."""
    
    def test_config_brand_path_exists(self):
        """Test that the BRAND_DIR in config points to existing directory."""
        assert config.BRAND_DIR.exists(), f"Brand directory not found at {config.BRAND_DIR}"
        
    def test_brand_essential_files_exist(self):
        """Test that essential brand files exist."""
        essential_files = [
            'mission.txt',
            'vision.md', 
            'problem_statement.md',
            'theme.scss',
            'jennai-logo.png'
        ]
        
        for file_name in essential_files:
            file_path = config.BRAND_DIR / file_name
            assert file_path.exists(), f"Essential brand file missing: {file_name} at {file_path}"
    
    def test_architect_can_access_brand(self):
        """Test that architect (main_routes.py) can load brand content."""
        # Import the brand loading function
        from src.presentation.api_server.flask_app.routes.main_routes import load_brand_content
        
        brand_content = load_brand_content()
        
        # Verify all expected content is loaded
        assert 'mission_statement' in brand_content
        assert 'vision_statement' in brand_content
        assert 'problem_statement' in brand_content
        
        # Verify content is not empty
        assert brand_content['mission_statement'].strip(), "Mission statement is empty"
        assert brand_content['vision_statement'].strip(), "Vision statement is empty"
        assert brand_content['problem_statement'].strip(), "Problem statement is empty"
        
    def test_designer_can_inject_brand_assets(self):
        """Test that designer persona can inject brand assets."""
        # Run the inject brand assets script
        result = subprocess.run([
            sys.executable, 
            str(PROJECT_ROOT / "admin" / "inject_brand_assets.py"),
            "--target", "flask"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Brand asset injection failed: {result.stderr}"
        
        # Verify key assets were copied
        flask_img_dir = config.PRESENTATION_DIR / "api_server" / "flask_app" / "static" / "img"
        flask_css_dir = config.PRESENTATION_DIR / "api_server" / "flask_app" / "static" / "css"
        
        expected_assets = [
            flask_img_dir / "jennai-logo.png",
            flask_img_dir / "favicon.ico", 
            flask_css_dir / "_variables.scss"
        ]
        
        for asset_path in expected_assets:
            assert asset_path.exists(), f"Expected asset not found: {asset_path}"
    
    def test_constructor_can_compile_brand_theme(self):
        """Test that constructor can compile the brand theme."""
        # Run the SCSS compilation
        result = subprocess.run([
            sys.executable,
            str(PROJECT_ROOT / "admin" / "compile_scss.py"), 
            "--target", "flask"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"SCSS compilation failed: {result.stderr}"
        
        # Verify CSS was generated
        css_file = config.PRESENTATION_DIR / "api_server" / "flask_app" / "static" / "css" / "main.css"
        assert css_file.exists(), "Compiled CSS file not found"
        
        # Verify CSS contains brand theme content
        css_content = css_file.read_text()
        assert len(css_content.strip()) > 0, "Generated CSS is empty"
        
    def test_contractor_can_validate_brand_status(self):
        """Test that contractor can check brand status via admin console."""
        # Import the check_apps functionality
        from admin.check_apps import check_app_status
        
        # Check Flask app status (which depends on brand assets)
        flask_status = check_app_status("flask")
        
        # If Flask app exists, brand assets should be properly integrated
        if flask_status.get("exists", False):
            assert flask_status.get("health_check", False), "Flask app health check failed - brand may not be integrated"
    
    def test_brand_favicon_exists(self):
        """Test that brand favicon files exist in correct location."""
        favicon_dir = config.BRAND_DIR / "favicon_io"
        assert favicon_dir.exists(), "Favicon directory not found"
        
        favicon_file = favicon_dir / "favicon.ico"
        assert favicon_file.exists(), "favicon.ico not found in brand directory"
    
    def test_brand_theme_is_valid_scss(self):
        """Test that the brand theme SCSS is valid."""
        theme_file = config.BRAND_DIR / "theme.scss"
        assert theme_file.exists(), "theme.scss not found"
        
        theme_content = theme_file.read_text()
        
        # Basic SCSS validation - should contain variables and imports
        assert "$" in theme_content, "SCSS variables not found in theme"
        assert "font" in theme_content.lower(), "Font definitions not found in theme"
        assert "color" in theme_content.lower(), "Color definitions not found in theme"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
