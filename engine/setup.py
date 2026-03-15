from setuptools import setup, find_packages

from Settings.settings import APP_NAME, VERSION


setup(
    name=APP_NAME,
    version=VERSION,
    packages=find_packages(),
)
