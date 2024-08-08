#!/bin/bash
set -ex

dnf -y install protobuf protobuf-compiler protobuf-devel
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
export PATH="$HOME/.cargo/bin:$PATH"

# Compile wheels
for PYBIN in /opt/python/cp{310,311,312}*/bin; do
    rm -rf /io/build/
    "${PYBIN}/pip" install -U setuptools setuptools-rust wheel
    "${PYBIN}/pip" wheel /io/ -w /io/dist/ --no-deps
done

# Bundle external shared libraries into the wheels
for whl in /io/dist/*{310,311,312}*.whl; do
    auditwheel repair "$whl" -w /io/dist/
done

for whl in /io/dist/*{310,311,312}-linux_x86_64.whl; do
  rm "$whl"
done
