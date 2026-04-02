
try:
    import tensorflow as tf
    print(f"TensorFlow: {tf.__version__}")
    from tensorflow import keras
    print(f"tf.keras version: {keras.__version__}")
except Exception as e:
    print(f"Error importing tf.keras: {e}")
