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
    name='voodoo',
    version=find_version("voodoo", "__init__.py"),
    author='Akretion',
    author_email='contact@akretion.com',
    url='https://github.com/akretion/voodoo-cli/',
    description='Environement builder for Odoo',
    license="AGPLv3+",
    long_description=open('README.md').read(),
    install_requires=[
        r.strip() for r in open('requirement.txt').read().splitlines() ],
    entry_points="""
    [console_scripts]
    voodoo=voodoo.main:main
    """,
    include_package_data=True,
    packages = find_packages() + ['voodoo'],
    package_dir={'config': ''},
    package_data={'': ['config/service.yml', 'config/.kitchen.yml', 'config/Berksfile']},
    zip_safe=False,
)
