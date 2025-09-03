"""
Device information parser utilities.
"""
import re


def parse_device_info(info_text):
    """Parse device information from firmware string."""
    info = {
        'board': 'Unknown',
        'version': 'Unknown',
        'build_time': 'Unknown',
        'copyright': '',
        'architecture': 'Unknown',
        'platform': 'Unknown',
        'parameters': {},
        'full_text': info_text or ''
    }
    
    if not info_text:
        return info
    
    lines = info_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Parse different fields
        if line.startswith('Board:'):
            info['board'] = line.replace('Board:', '').strip()
        elif line.startswith('Version:'):
            version_line = line.replace('Version:', '').strip()
            # Extract just the version number/info
            info['version'] = version_line
            
            # Parse parameters from version line if present
            if '[' in version_line and ']' in version_line:
                param_part = version_line[version_line.find('[') + 1:version_line.find(']')]
                params = {}
                for param in param_part.split(', '):
                    if ':' in param:
                        key, value = param.split(':', 1)
                        params[key.strip()] = value.strip()
                    else:
                        # Handle parameters like "p:101" 
                        if param.strip():
                            params[param.strip()] = ''
                info['parameters'] = params
                
        elif line.startswith('Build Time:'):
            info['build_time'] = line.replace('Build Time:', '').strip()
        elif line.startswith('Architecture:'):
            info['architecture'] = line.replace('Architecture:', '').strip()
        elif line.startswith('Platform:'):
            info['platform'] = line.replace('Platform:', '').strip()
        elif 'Copyright' in line:
            info['copyright'] = line
    
    return info
