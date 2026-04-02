
try:
    import numpy
    print(f"Numpy: {numpy.__version__}")
except Exception as e:
    print(f"Numpy error: {e}")

try:
    import ml_dtypes
    print(f"ml_dtypes: {ml_dtypes.__version__}")
except Exception as e:
    print(f"ml_dtypes error: {e}")

try:
    import tensorflow
    print(f"TensorFlow: {tensorflow.__version__}")
except Exception as e:
    print(f"TensorFlow error: {e}")
