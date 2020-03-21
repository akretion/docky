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
    version_match = re.search(r"VERSION = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='docky',
    version=find_version("docky", "cmd", "base.py"),
    author='Akretion',
    author_email='contact@akretion.com',
    url='https://github.com/akretion/docky/',
    description='Make developpement with docker simply',
    license="AGPLv3+",
    long_description=open('README.rst').read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=[
        r.strip() for r in open('requirements.txt').read().splitlines()],
    entry_points="""
    [console_scripts]
    docky=docky.main:main
    dcpatched=docky.dcpatched:main
    """,
    include_package_data=True,
    packages=find_packages() + ['docky'],
    zip_safe=False,
)
