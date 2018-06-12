import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-simple-smyt-menu',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='Custom',
    description='A simple Django app for menus.',
    long_description=README,
    url='https://www.smyt.ru/',
    author='SMYT',
    author_email='mail@smyt.ru',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: Custom',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'django>=1.11,<2.0;python_version<"3.0"',
        'django>=1.11,<2.1;python_version>="3.0"',
        'mock;python_version<"3.3"',
    ],
)
