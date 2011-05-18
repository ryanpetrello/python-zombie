try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

#
# determine requirements
#
requirements = []

setup(
    name                    = "pythonzombie",
    version                 = "0.0.1a1",
    include_package_data    = True,
                            
    # metadata              
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
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    license                 = "BSD",
                            
    install_requires        = requirements,
)
