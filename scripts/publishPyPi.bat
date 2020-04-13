cd ..
py -m pip install setuptools twine wheel
py -m pip install --upgrade setuptools twine wheel
py setup.py sdist bdist_wheel
twine upload dist/*
cd scripts