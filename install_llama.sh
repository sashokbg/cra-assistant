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


CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 pip install --upgrade --no-cache --force-reinstall  'llama-cpp-python==0.2.85' 'llama-cpp-python[server]==0.2.85'
