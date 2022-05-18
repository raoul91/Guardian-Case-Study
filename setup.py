from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name='GuardianApiCaseStudy',
    author='Louis Soares',
    version='0.1.0',
    packages=['sample', 'tests'],
    data_files=['data'],
    description="Guardian Api Case Study",
    long_description=long_description,
)
