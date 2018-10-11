#!/bin/bash

set -e
set -x

cd /root
g++ vfiocma.cpp -o libcma.so -shared -fPIC
cp libcma.so /usr/lib
rm libcma.so
rm vfiocma.cpp
