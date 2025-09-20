"""Tests for PASVG file utilities."""

import pytest
import tempfile
import os
from pathlib import Path

from pasvg.utils.file_utils import FileUtils


class TestFileUtils:
    """Test FileUtils functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.file_utils = FileUtils()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_file_type(self):
        """Test file type detection."""
        test_cases = [
            ("test.py", "python"),
            ("test.js", "javascript"),
            ("test.html", "html"),
            ("test.css", "css"),
            ("test.json", "json"),
            ("test.yaml", "yaml"),
            ("test.yml", "yaml"),
            ("test.md", "markdown"),
            ("test.txt", "text"),
            ("test.png", "image"),
            ("test.jpg", "image"),
            ("unknown.xyz", "unknown")
        ]
        
        for filename, expected_type in test_cases:
            result = self.file_utils.detect_file_type(filename)
            assert result == expected_type, f"Expected {expected_type} for {filename}, got {result}"
    
    def test_detect_language(self):
        """Test programming language detection."""
        test_cases = [
            ("script.py", "python"),
            ("app.js", "javascript"),
            ("Component.jsx", "javascript"),
            ("style.css", "css"),
            ("index.html", "html"),
            ("config.json", "json"),
            ("data.yaml", "yaml"),
            ("README.md", "markdown"),
            ("Dockerfile", "dockerfile"),
            ("unknown.xyz", None)
        ]
        
        for filename, expected_lang in test_cases:
            result = self.file_utils.detect_language(filename)
            assert result == expected_lang, f"Expected {expected_lang} for {filename}, got {result}"
    
    def test_is_binary_file(self):
        """Test binary file detection."""
        # Create test files
        text_file = self.temp_dir / "test.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("This is a text file")
        
        binary_file = self.temp_dir / "test.bin"
        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03\xff\xfe')
        
        # Test detection
        assert not self.file_utils.is_binary_file(text_file)
        assert self.file_utils.is_binary_file(binary_file)
    
    def test_encode_binary_file(self):
        """Test binary file encoding."""
        # Create a small binary file
        binary_file = self.temp_dir / "test.bin"
        test_data = b'\x00\x01\x02\x03'
        with open(binary_file, 'wb') as f:
            f.write(test_data)
        
        encoded = self.file_utils.encode_binary_file(binary_file)
        
        # Verify it's base64 encoded
        import base64
        decoded = base64.b64decode(encoded)
        assert decoded == test_data
    
    def test_read_file_content(self):
        """Test file content reading."""
        # Test text file
        text_file = self.temp_dir / "test.txt"
        test_content = "Hello, PASVG!\nThis is a test file."
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        content, encoding = self.file_utils.read_file_content(text_file)
        assert content == test_content
        assert encoding == "utf-8"
        
        # Test binary file
        binary_file = self.temp_dir / "test.bin"
        test_data = b'\x00\x01\x02\x03'
        with open(binary_file, 'wb') as f:
            f.write(test_data)
        
        content, encoding = self.file_utils.read_file_content(binary_file)
        assert encoding == "base64"
        
        # Verify the base64 content can be decoded
        import base64
        decoded = base64.b64decode(content)
        assert decoded == test_data
    
    def test_write_file_content(self):
        """Test file content writing."""
        # Test text file
        text_file = self.temp_dir / "output.txt"
        test_content = "Hello, World!"
        
        self.file_utils.write_file_content(text_file, test_content)
        
        with open(text_file, 'r', encoding='utf-8') as f:
            read_content = f.read()
        
        assert read_content == test_content
        
        # Test binary file with base64 encoding
        binary_file = self.temp_dir / "output.bin"
        test_data = b'\x00\x01\x02\x03'
        import base64
        encoded_content = base64.b64encode(test_data).decode('ascii')
        
        self.file_utils.write_file_content(binary_file, encoded_content, encoding="base64")
        
        with open(binary_file, 'rb') as f:
            read_data = f.read()
        
        assert read_data == test_data
    
    def test_scan_directory(self):
        """Test directory scanning."""
        # Create test directory structure
        subdir = self.temp_dir / "subdir"
        subdir.mkdir()
        
        # Create test files
        (self.temp_dir / "file1.py").write_text("print('hello')")
        (self.temp_dir / "file2.js").write_text("console.log('hello');")
        (subdir / "file3.html").write_text("<h1>Hello</h1>")
        (self.temp_dir / ".hidden").write_text("hidden file")
        
        # Test scanning
        files = self.file_utils.scan_directory(self.temp_dir)
        
        # Should find 3 non-hidden files
        assert len(files) == 3
        
        # Get just the filenames from the paths to check for inclusion
        filenames = [os.path.basename(f.filename) for f in files]
        assert "file1.py" in filenames
        assert "file2.js" in filenames
        assert "file3.html" in filenames
        assert ".hidden" not in filenames  # Hidden files should be excluded
    
    def test_scan_directory_with_patterns(self):
        """Test directory scanning with include/exclude patterns."""
        # Create test files
        (self.temp_dir / "script.py").write_text("print('hello')")
        (self.temp_dir / "style.css").write_text("body { color: red; }")
        (self.temp_dir / "data.json").write_text('{"key": "value"}')
        (self.temp_dir / "README.md").write_text("# Title")
        
        # Test with include patterns
        python_files = self.file_utils.scan_directory(
            self.temp_dir, 
            include_patterns=["*.py"]
        )
        assert len(python_files) == 1
        assert python_files[0].name == "script.py"
        
        # Test with exclude patterns
        non_python_files = self.file_utils.scan_directory(
            self.temp_dir,
            exclude_patterns=["*.py"]
        )
        filenames = [f.name for f in non_python_files]
        assert "script.py" not in filenames
        assert "style.css" in filenames
        assert "data.json" in filenames
    
    def test_validate_file_path(self):
        """Test file path validation."""
        # Valid paths
        assert self.file_utils.validate_file_path("test.py")
        assert self.file_utils.validate_file_path("src/main.py")
        assert self.file_utils.validate_file_path("docs/README.md")
        
        # Invalid paths (should not contain certain characters)
        invalid_paths = [
            "../../../etc/passwd",  # Path traversal
            "test<file>.py",        # Invalid characters
            "test|file.py",
            "test?file.py",
            "con.txt",              # Windows reserved name
        ]
        
        for invalid_path in invalid_paths:
            assert not self.file_utils.validate_file_path(invalid_path)
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        test_cases = [
            ("normal_file.py", "normal_file.py"),
            ("file with spaces.txt", "file_with_spaces.txt"),
            ("file<>|?*.txt", "file_____.txt"),
            ("très_spécial.py", "très_spécial.py"),  # Unicode should be preserved
            ("file/with/path.txt", "file_with_path.txt"),
        ]
        
        for input_name, expected in test_cases:
            result = self.file_utils.sanitize_filename(input_name)
            assert result == expected, f"Expected {expected} for {input_name}, got {result}"
