"""
Demo script showing device-specific sweep limits.
This demonstrates how different VNA devices have different sweep point limits.
"""

# Common VNA device classes and their limits
DEVICE_LIMITS = {
    "NanoVNA (Original)": {"min": 11, "max": 101},
    "NanoVNA-F": {"min": 11, "max": 101},
    "NanoVNA-H": {"min": 11, "max": 101},
    "NanoVNA-H4": {"min": 11, "max": 101},
    "NanoVNA-F V2": {"min": 11, "max": 301},
    "NanoVNA-F V3": {"min": 11, "max": 801},
    "NanoVNA-V2": {"min": 11, "max": 101},
    "SV4401A": {"min": 101, "max": 1001},
    "SV6301A": {"min": 101, "max": 1001},
    "JNCRadio VNA 3G": {"min": 11, "max": 1001},
    "LiteVNA64": {"min": 11, "max": 65535},
    "AVNA": {"min": 11, "max": 101},
    "TinySA": {"min": 11, "max": 101},
}

def print_device_limits():
    """Print a table of device limits."""
    print("VNA Device Sweep Points Limits")
    print("=" * 50)
    print(f"{'Device Name':<25} {'Min':<8} {'Max':<8}")
    print("-" * 50)
    
    for device_name, limits in DEVICE_LIMITS.items():
        print(f"{device_name:<25} {limits['min']:<8} {limits['max']:<8}")
    
    print("\nNote: These limits are automatically detected and applied")
    print("when the corresponding device is connected to the system.")

if __name__ == "__main__":
    print_device_limits()
