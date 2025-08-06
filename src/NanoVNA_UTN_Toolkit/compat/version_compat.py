"""
Version compatibility layer for NanoVNA-UTN-Toolkit.
This module provides version compatibility functions to work with different versions
of the NanoVNASaver library.
"""

import logging
import inspect
from typing import Union, Tuple, Any
from ..Hardware.Version import Version as OriginalVersion
from ..utils.version import Version as UTNVersion

logger = logging.getLogger(__name__)


def build_version(*args, **kwargs) -> UTNVersion:
    """Create a version object compatible with the UTN Toolkit.
    
    This function is a compatibility wrapper that can handle different call signatures:
    - build_version(major, minor, revision=0, note='')
    - build_version(major, minor, note='')
    - build_version(major, minor)
    
    Args:
        *args: Version components (major, minor, [revision, [note]])
        **kwargs: Keyword arguments (revision, note)
        
    Returns:
        A Version instance compatible with the UTN Toolkit
    """
    # Log the call for debugging
    logger.debug(f"build_version called with args: {args}, kwargs: {kwargs}")
    
    # Get the frame that called this function
    caller_frame = inspect.currentframe().f_back
    caller_info = f"{caller_frame.f_code.co_filename}:{caller_frame.f_lineno}" if caller_frame else "unknown"
    logger.debug(f"Called from: {caller_info}")
    
    try:
        # Default values
        major = 0
        minor = 0
        revision = 0
        note = ''
        
        # Handle different call patterns
        if len(args) >= 2:
            major, minor = args[0], args[1]
            if len(args) >= 3 and isinstance(args[2], str):
                # Called as build_version(major, minor, note)
                revision = 0
                note = args[2]
            elif len(args) >= 3:
                # Called as build_version(major, minor, revision, [note])
                revision = args[2]
                note = args[3] if len(args) >= 4 else ''
            else:
                # Called as build_version(major, minor)
                revision = 0
                note = ''
        elif args:
            # Handle single argument (version string)
            if len(args) == 1 and isinstance(args[0], str):
                return UTNVersion(args[0])
        
        # Override with any keyword arguments
        if 'major' in kwargs:
            major = kwargs['major']
        if 'minor' in kwargs:
            minor = kwargs['minor']
        if 'revision' in kwargs:
            revision = kwargs['revision']
        if 'note' in kwargs:
            note = kwargs['note']
        
        # Ensure we have valid integers
        try:
            major = int(major) if major is not None else 0
            minor = int(minor) if minor is not None else 0
            revision = int(revision) if revision is not None else 0
            note = str(note) if note is not None else ''
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid version component: {e}, using defaults (0.0.0)")
            major, minor, revision, note = 0, 0, 0, ''
        
        # Create version string
        version_str = f"{major}.{minor}"
        if revision != 0 or note:
            version_str += f".{revision}"
        if note:
            version_str += f"-{note}"
        
        logger.debug(f"Creating version: {version_str}")
        return UTNVersion(version_str)
        
    except Exception as e:
        logger.exception(f"Error in build_version: {e}")
        # Return a default version on error
        return UTNVersion("0.0.0")


def convert_to_utn_version(version: Union[str, OriginalVersion, UTNVersion]) -> UTNVersion:
    """Convert any version object to the UTN Version format.
    
    Args:
        version: A version string or Version object
        
    Returns:
        A UTN Version instance
    """
    if isinstance(version, UTNVersion):
        return version
    
    if isinstance(version, OriginalVersion):
        return UTNVersion.build(version.major, version.minor, version.revision, getattr(version, 'note', ''))
    
    # Handle string input
    return UTNVersion(version)


def get_version_components(version: Union[str, OriginalVersion, UTNVersion]) -> Tuple[int, int, int, str]:
    """Get version components from any version object.
    
    Args:
        version: A version string or Version object
        
    Returns:
        A tuple of (major, minor, revision, note)
    """
    if isinstance(version, (OriginalVersion, UTNVersion)):
        return (version.major, version.minor, version.revision, getattr(version, 'note', ''))
    
    # Handle string input
    v = UTNVersion(version)
    return (v.major, v.minor, v.revision, v.note)
