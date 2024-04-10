from setuptools import setup, find_packages

setup(
    name='awsEsToBQ',
    packages=find_packages(),
    install_requires=['build','elasticsearch==7.17.9']
)