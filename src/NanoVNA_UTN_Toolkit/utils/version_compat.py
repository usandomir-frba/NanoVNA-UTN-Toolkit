"""Version compatibility module to handle different Version class implementations."""
import logging
from typing import Optional, Union, Tuple, List, Any
from functools import total_ordering
from .version import Version as OriginalVersion

logger = logging.getLogger(__name__)

@total_ordering
class Version(OriginalVersion):
    """Wrapper class to handle version compatibility with rich comparison support."""
    
    def __new__(cls, major_or_version_str, minor=None, revision=None, note=None):
        """Create a Version instance from either a version string or individual components."""
        if isinstance(major_or_version_str, str) and minor is None:
            # Parse version string using the original NamedTuple parse method
            original = OriginalVersion.parse(major_or_version_str)
            # Create new instance of our wrapper class with the parsed values
            return super(Version, cls).__new__(cls, original.major, original.minor, original.revision, original.note)
        else:
            # Create from components
            major = major_or_version_str
            minor = minor if minor is not None else 0
            revision = revision if revision is not None else 0
            note = note if note is not None else ''
            return super(Version, cls).__new__(cls, major, minor, revision, note)
    
    @classmethod
    def build(cls, major: int, minor: int, revision: int = 0, note: str = '') -> 'Version':
        """Create a Version instance from individual version components.
        
        This is a compatibility wrapper that ensures the build method always receives
        at least major and minor version numbers, with optional revision and note.
        """
        return cls(major, minor, revision, note)
    
    @classmethod
    def parse(cls, version_str: str) -> 'Version':
        """Parse a version string and return a Version object.
        
        This method is added for compatibility with code that expects a parse method.
        """
        return cls(version_str)
    
    def __eq__(self, other) -> bool:
        """Check if this version is equal to another version."""
        if not isinstance(other, (Version, str)):
            return NotImplemented
        if isinstance(other, str):
            other = Version.parse(other)
        return (self.major, self.minor, self.revision) == (other.major, other.minor, other.revision)
    
    def __lt__(self, other) -> bool:
        """Check if this version is less than another version."""
        if not isinstance(other, (Version, str)):
            return NotImplemented
        if isinstance(other, str):
            other = Version.parse(other)
        return (self.major, self.minor, self.revision) < (other.major, other.minor, other.revision)
    
    def __repr__(self) -> str:
        """Return a string representation of the version."""
        return f"Version('{self.major}.{self.minor}.{self.revision}{self.note}')"
    
    def __hash__(self) -> int:
        """Return a hash of the version."""
        return hash((self.major, self.minor, self.revision, self.note))

# Create a build_version function that can be used as a drop-in replacement for Version.build
def build_version(major: int, minor: int, revision: int = 0, note: str = '') -> Version:
    """Create a Version instance from individual version components.
    
    This function provides a consistent way to create Version instances
    across different parts of the application.
    """
    return Version(major, minor, revision, note)


def build_utn_version(major: int, minor: int, revision: int = 0, note: str = '') -> OriginalVersion:
    """Create a UTN Version object (NamedTuple) directly.
    
    This function creates a version object with the specified components using
    the original NamedTuple Version class.
    
    Args:
        major: Major version number
        minor: Minor version number
        revision: Revision number (default: 0)
        note: Version note (default: '')
        
    Returns:
        A Version instance compatible with the UTN Toolkit
    """
    try:
        # Ensure we have valid integers
        major = int(major) if major is not None else 0
        minor = int(minor) if minor is not None else 0
        revision = int(revision) if revision is not None else 0
        note = str(note) if note is not None else ''
        
        # Create and return the version object directly using the NamedTuple constructor
        version = OriginalVersion(major, minor, revision, note)
        logger.debug("Created UTN version: %s", version)
        return version
        
    except (ValueError, TypeError) as e:
        logger.warning("Invalid version component: %s, using defaults (0.0.0)", e)
        return OriginalVersion(0, 0, 0, '')
        
    except Exception as e:
        logger.error("Unexpected error in build_utn_version: %s", str(e), exc_info=False)
        return OriginalVersion(0, 0, 0, '')


def convert_to_utn_version(version: Union[str, OriginalVersion, Version]) -> OriginalVersion:
    """Convert any version object to the UTN Version format.
    
    Args:
        version: A version string or Version object
        
    Returns:
        A UTN Version instance (NamedTuple)
    """
    if isinstance(version, OriginalVersion):
        return version
    
    if isinstance(version, Version):
        return OriginalVersion(version.major, version.minor, version.revision, version.note)
    
    # Handle string input
    return OriginalVersion.parse(version)

# Alias for backward compatibility
parse_version = Version.parse

# Update the module's __all__ to expose all functions and classes
__all__ = ['Version', 'build_version', 'build_utn_version', 'convert_to_utn_version', 'parse_version']
