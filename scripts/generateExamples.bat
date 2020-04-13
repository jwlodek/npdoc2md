@echo OFF

cd ..
py npdoc2md.py -i . -o example -s setup.py __init__.py test_parsing.py
cd  scripts