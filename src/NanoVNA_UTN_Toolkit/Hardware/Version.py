import re
from typing import Optional, Union

class Version:
    """Version class for nanoVNA firmware versions with support for both string and component-based initialization."""
    
    def __init__(self, major: Union[str, int] = 0, minor: int = 0, revision: int = 0, note: str = ''):
        """Initialize a Version object.
        
        Can be initialized in two ways:
        1. From a version string: Version("1.2.3")
        2. From components: Version(1, 2, 3, 'note')
        """
        if isinstance(major, str):
            # String initialization (legacy support)
            version_str = major
            parts = version_str.strip().split('.')
            self.major = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 0
            self.minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
            self.revision = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
            self.note = note or ''
            
            # Handle any additional notes (e.g., "-test" in "1.2.3-test")
            if len(parts) > 3 or (len(parts) > 2 and not str(self.revision).isdigit()):
                note_parts = [note] if note else []
                note_parts.extend(parts[2:])
                self.note = ' '.join(note_parts).strip()
                self.revision = 0
        else:
            # Component initialization
            self.major = int(major) if major is not None else 0
            self.minor = int(minor) if minor is not None else 0
            self.revision = int(revision) if revision is not None else 0
            self.note = str(note) if note is not None else ''
    
    def __str__(self):
        if self.note:
            return f"{self.major}.{self.minor}.{self.revision}{self.note}"
        return f"{self.major}.{self.minor}.{self.revision}"
    
    def __lt__(self, other):
        if not isinstance(other, Version):
            other = Version(str(other))
        return (self.major, self.minor, self.revision) < (other.major, other.minor, other.revision)
    
    def __eq__(self, other):
        if not isinstance(other, Version):
            other = Version(str(other))
        return (self.major, self.minor, self.revision) == (other.major, other.minor, other.revision)
