pip install python-dateutil
pip insatll requests
pip install ninja
pip install eventlet
pip install python-socketio

CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 pip install \
  --upgrade \
  --force-reinstall \
  --no-cache-dir \
  llama-cpp-python


