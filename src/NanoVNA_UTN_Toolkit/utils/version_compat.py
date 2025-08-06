"""Version compatibility module to handle different Version class implementations."""
from typing import Optional, Union, Tuple, List, Any
from functools import total_ordering
from .version import Version as OriginalVersion

@total_ordering
class Version(OriginalVersion):
    """Wrapper class to handle version compatibility with rich comparison support."""
    
    @classmethod
    def build(cls, major: int, minor: int, revision: int = 0, note: str = '') -> 'Version':
        """Create a Version instance from individual version components.
        
        This is a compatibility wrapper that ensures the build method always receives
        at least major and minor version numbers, with optional revision and note.
        """
        return cls(f"{major}.{minor}.{revision}{note}")
    
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
            other = Version(other)
        return (self.major, self.minor, self.revision) == (other.major, other.minor, other.revision)
    
    def __lt__(self, other) -> bool:
        """Check if this version is less than another version."""
        if not isinstance(other, (Version, str)):
            return NotImplemented
        if isinstance(other, str):
            other = Version(other)
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
    return Version(f"{major}.{minor}.{revision}{note}")

# Alias for backward compatibility
parse_version = Version.parse

# Update the module's __all__ to expose the Version class and build_version function
__all__ = ['Version', 'build_version', 'parse_version']
