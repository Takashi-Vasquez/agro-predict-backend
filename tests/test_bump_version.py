"""
Unit tests for bump_version.py
"""
import os
import tempfile
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bump_version import bump_version as bump_version_fn, VersionBumpContext, read_version, write_version


def _setup_version_file(content: str) -> tuple[Path, str]:
    """Helper to create temp version file and return path and original VERSION_FILE."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content + "\n")
        temp_path = Path(f.name)
    
    import bump_version
    original_file = bump_version.VERSION_FILE
    bump_version.VERSION_FILE = temp_path
    return temp_path, original_file


def _cleanup_version_file(temp_path: Path, original_file: str):
    """Cleanup version file and restore original."""
    import bump_version
    bump_version.VERSION_FILE = original_file
    if temp_path.exists():
        os.unlink(temp_path)


def test_bump_patch():
    """Test patch version bump (1.0.0 -> 1.0.1)"""
    temp_path, original_file = _setup_version_file("1.0.0")
    
    try:
        new_version = bump_version_fn("patch")
        assert new_version == "1.0.1"
        
        # Verify file was updated
        with open(temp_path, 'r') as f:
            assert f.read().strip() == "1.0.1"
    finally:
        _cleanup_version_file(temp_path, original_file)


def test_bump_minor():
    """Test minor version bump (1.0.1 -> 1.1.0)"""
    temp_path, original_file = _setup_version_file("1.0.1")
    
    try:
        new_version = bump_version_fn("minor")
        assert new_version == "1.1.0"
        
        with open(temp_path, 'r') as f:
            assert f.read().strip() == "1.1.0"
    finally:
        _cleanup_version_file(temp_path, original_file)


def test_bump_major():
    """Test major version bump (1.1.0 -> 2.0.0)"""
    temp_path, original_file = _setup_version_file("1.1.0")
    
    try:
        new_version = bump_version_fn("major")
        assert new_version == "2.0.0"
        
        with open(temp_path, 'r') as f:
            assert f.read().strip() == "2.0.0"
    finally:
        _cleanup_version_file(temp_path, original_file)


def test_bump_case_insensitive():
    """Test that bump level is case insensitive"""
    temp_path, original_file = _setup_version_file("1.0.0")
    
    try:
        # Test uppercase
        new_version = bump_version_fn("PATCH")
        assert new_version == "1.0.1"
        
        # Test mixed case
        new_version = bump_version_fn("Minor")
        assert new_version == "1.1.0"
    finally:
        _cleanup_version_file(temp_path, original_file)


def test_missing_file_creates_default():
    """Test that missing version file defaults to 1.0.0"""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir) / "version.txt"
        
        import bump_version
        original_file = bump_version.VERSION_FILE
        bump_version.VERSION_FILE = temp_path
        
        try:
            # File doesn't exist, should default to 1.0.0
            version = read_version()
            assert version == "1.0.0"
            
            # Bump should work
            new_version = bump_version_fn("patch")
            assert new_version == "1.0.1"
            
            # File should be created
            assert temp_path.exists()
        finally:
            bump_version.VERSION_FILE = original_file


def test_invalid_level_raises_error():
    """Test that invalid bump level raises ValueError"""
    temp_path, original_file = _setup_version_file("1.0.0")
    
    try:
        try:
            bump_version_fn("invalid")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Invalid bump level" in str(e)
    finally:
        _cleanup_version_file(temp_path, original_file)


def test_invalid_version_format_raises_error():
    """Test that invalid version format raises ValueError"""
    temp_path, original_file = _setup_version_file("invalid")
    
    try:
        try:
            bump_version_fn("patch")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Invalid version format" in str(e)
    finally:
        _cleanup_version_file(temp_path, original_file)


def test_context_manager_commits_on_success():
    """Test VersionBumpContext commits version on successful exit"""
    temp_path, original_file = _setup_version_file("1.0.0")
    
    try:
        with VersionBumpContext("minor") as new_version:
            assert new_version == "1.1.0"
            # Simulate successful operation
            pass
        
        # Version should be committed
        with open(temp_path, 'r') as f:
            assert f.read().strip() == "1.1.0"
    finally:
        _cleanup_version_file(temp_path, original_file)


def test_context_manager_rollbacks_on_exception():
    """Test VersionBumpContext rolls back version on exception"""
    temp_path, original_file = _setup_version_file("1.0.0")
    
    try:
        try:
            with VersionBumpContext("minor") as new_version:
                assert new_version == "1.1.0"
                raise ValueError("Simulated error")
        except ValueError:
            pass  # Expected
        
        # Version should be rolled back
        with open(temp_path, 'r') as f:
            assert f.read().strip() == "1.0.0"
    finally:
        _cleanup_version_file(temp_path, original_file)


def test_version_bump_sequence():
    """Test a sequence of version bumps"""
    temp_path, original_file = _setup_version_file("1.0.0")
    
    try:
        assert bump_version_fn("patch") == "1.0.1"
        assert bump_version_fn("patch") == "1.0.2"
        assert bump_version_fn("minor") == "1.1.0"
        assert bump_version_fn("patch") == "1.1.1"
        assert bump_version_fn("major") == "2.0.0"
        assert bump_version_fn("minor") == "2.1.0"
        assert bump_version_fn("patch") == "2.1.1"
        
        with open(temp_path, 'r') as f:
            assert f.read().strip() == "2.1.1"
    finally:
        _cleanup_version_file(temp_path, original_file)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])