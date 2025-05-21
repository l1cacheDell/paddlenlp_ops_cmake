#!/bin/bash

rm -rf ./build
rm -rf ./*.egg-info
rm -rf ./dist

python setup_cmake.py install