
import os
import sys

# Try WITHOUT legacy flag first to see if it works natively with Keras 3
# If it fails, we know we need the flag.

try:
    from app import load_model_components
    print("Testing model loading with default environment...")
    if load_model_components():
        print("Models loaded successfully!")
        sys.exit(0)
    else:
        print("Failed to load models.")
        sys.exit(1)
except Exception as e:
    print(f"Error loading models: {e}")
    sys.exit(1)
