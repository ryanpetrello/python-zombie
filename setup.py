from setuptools import setup, find_packages, Command
import sys

__version__ = '0.2.0'
tests_require = []

if sys.version_info < (2, 7):
    tests_require += ['unittest2']


class Tox(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            import tox
        except ImportError:
            import sys
            sys.exit("tox is required to run tests.  $ pip install tox")
        tox.cmdline()

#
# determine requirements
#
setup(
    name="zombie",
    version=__version__,
    include_package_data=True,
    author="Ryan Petrello",
    author_email="ryan [at] ryanpetrello [dot] com",
    url="https://github.com/ryanpetrello/python-zombie",
    description="A Python driver for Zombie.js",
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['ez_setup', 'tests']),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Testing :: Traffic Generation'
    ],
    license="MIT",
    install_requires=[],
    tests_require=tests_require,
    cmdclass={'test': Tox}
)
