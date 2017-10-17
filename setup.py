from setuptools import setup
import sys
sys.path.append('test')

setup (name = 'eosUtils',
    version = '0.9',
    description = 'EOS Utilities Package',
    author = 'Dominic Mazzoni',
    author_email = 'dominic.mazzoni@jpl.nasa.gov',
    maintainer = 'Gerald Manipon',
    maintainer_email = 'pymonger@gmail.com',
    url = 'https://github.com/hysds/eosUtils',
    packages=['eosUtils'],
    package_data={
    	'': ['*.pkl']
    },
    test_suite="runAllTests.getAllTestsTestSuite",
)
