try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
from distutils.core import Command

#
# determine requirements
#
requirements = [
    'simplejson',
    'fudge'
]

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'pythonzombie/tests/run.py'])
        raise SystemExit(errno)

setup(
    name                    = "pythonzombie",
    version                 = "0.0.1a1",
    include_package_data    = True,
    # The problem is here - he did not include *.js files - how do i include them correctly?
    # 
    # This is what i thought of, but its wrong.
    #
    package_data            = {'pythonzombie.proxy': ['*.js']},
    #
    author                  = "Ryan Petrello",
    author_email            = "ryan [at] ryanpetrello [dot] com",
    description             = "A Python driver for Zombie.js",
    long_description        = open('README.rst').read(),
    packages                = find_packages(exclude=['ez_setup', 'tests']),
    classifiers             = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    license                 = "BSD",
    install_requires        = requirements,
    cmdclass                = {'test': PyTest}
)
