#! /bin/bash

target=$1
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

sudo cp -r $script_dir/libxlnk_cma.h $target/usr/include
sudo cp -r $script_dir/vfiocma.cpp $target/root
