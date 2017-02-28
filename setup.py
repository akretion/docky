from setuptools import setup, find_packages
import codecs
import os
import re

def read(*parts):
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='voodoo-cli',
    version=find_version("voodoo", "main.py"),
    author='Akretion',
    author_email='contact@akretion.com',
    url='https://github.com/akretion/voodoo/',
    description='Environment builder for Odoo',
    license="AGPLv3+",
    long_description=open('README.rst').read(),
    install_requires=[
        r.strip() for r in open('requirements.txt').read().splitlines() ],
    entry_points="""
    [console_scripts]
    voodoo=voodoo.main:main
    """,
    include_package_data=True,
    packages = find_packages() + ['voodoo'],
    zip_safe=False,
)
