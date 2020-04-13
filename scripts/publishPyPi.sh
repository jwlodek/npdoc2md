#!/bin/bash

cd ..
pip3 install setuptools twine wheel
pip3 install --upgrade setuptools twine wheel
python3 setup.py sdist bdist_wheel
twine upload dist/*