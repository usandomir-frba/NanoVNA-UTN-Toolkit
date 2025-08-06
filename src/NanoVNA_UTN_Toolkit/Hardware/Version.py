import re

class Version:
    """Simple version class for nanoVNA firmware versions."""
    
    def __init__(self, version_string: str = "0.0.0"):
        # Simple version string parsing (e.g., "1.2.3")
        parts = version_string.strip().split('.')
        self.major = int(parts[0]) if len(parts) > 0 else 0
        self.minor = int(parts[1]) if len(parts) > 1 else 0
        self.revision = int(parts[2]) if len(parts) > 2 else 0
        self.note = ''
        
        # Handle any additional notes (e.g., "-test" in "1.2.3-test")
        if len(parts) > 3 or (len(parts) > 2 and not str(self.revision).isdigit()):
            self.note = '.'.join(parts[2:])
            self.revision = 0
    
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
