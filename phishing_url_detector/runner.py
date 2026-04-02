
import os
import sys
import subprocess

# Set environment variable to force legacy behavior
env = os.environ.copy()
env['TF_USE_LEGACY_KERAS'] = '1'

print("Preparing to run training with TF_USE_LEGACY_KERAS=1...")

try:
    # Run the training script
    subprocess.run([sys.executable, "train_model.py"], env=env, check=True)
    print("Training process finished successfully.")
except subprocess.CalledProcessError as e:
    print(f"Training failed with exit code: {e.returncode}")
    sys.exit(e.returncode)
except Exception as e:
    print(f"Error executing training: {e}")
    sys.exit(1)
