#!/usr/bin/env python

import setuptools
import repo_mirror


requirements = ['boto3', 'pyyaml', 'urllib3', 'sh']
test_requirements = ['mock', 'nose', 'flake8', 'pytest']


setuptools.setup(
    name='pool',
    version=repo_mirror.__version__,
    description='Anaconda utility to generate airgap tarball files',
    author='Dave Kludt',
    author_email='dkludt@anaconda.com',
    install_requires=requirements,
    extras_require={
        'tests': test_requirements
    },
    entry_points={
        'console_scripts': [
            'pool=repo_mirror.pool:main'
        ]
    },
    packages=['repo_mirror'],
    zip_safe=False
)
