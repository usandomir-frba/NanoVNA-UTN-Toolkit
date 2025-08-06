import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# Import and run the main function from the root main.py
try:
    import main
    main.main()
except ImportError as e:
    print(f"Error importing main module: {e}")
    print("Make sure you're running from the correct directory.")
    sys.exit(1)
