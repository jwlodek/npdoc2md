import setuptools

# Use README for long description
with open('README.md', 'r') as readme_fp:
    long_description = readme_fp.read()

# py_cui setup
setuptools.setup(
    name='npdoc2md',
    description='Scripts for autogenerating markdown docs from numpy-style docstrings.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.0.1',
    author='Jakub Wlodek',
    author_email='jwlodek.dev@gmail.com',
    license='MIT',
    url='https://github.com/jwlodek/npdoc2md',
    entry_points={
        'console_scripts': [
            'npdoc2md = npdoc2md:main',
            'code2npdoc = code2npdoc:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='markdown numpy docs autogenerate script',
    python_requires='>=3.5',
)