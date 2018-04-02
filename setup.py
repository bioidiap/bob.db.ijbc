#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements
install_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='bob.db.ijbc',
    version=version,
    description='IJB-C Database Access API for Bob',
    url='https://gitlab.idiap.ch/bob/bob.db.ijbb',
    license='BSD',
    author='Manuel Gunther',
    author_email='siebenkopf@googlemail.com',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires = install_requires,

    entry_points = {
      # bob database declaration
      'bob.db': [
        'ijbb = bob.db.ijbc.driver:Interface',
      ],

    },

    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      'Topic :: Database :: Front-Ends',
    ],
)
