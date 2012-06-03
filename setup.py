try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages  # noqa

#
# determine requirements
#
requirements = ['simplejson']

setup(
    name="pythonzombie",
    version="0.0.1a1",
    include_package_data=True,
    author="Ryan Petrello",
    author_email="ryan [at] ryanpetrello [dot] com",
    description="A Python driver for Zombie.js",
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['ez_setup', 'tests']),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python'
        'Programming Language :: Python :: 2',
        #'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.2',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Testing :: Traffic Generation'
    ],
    license="BSD",
    tests_require=['fudge'],
    test_suite='pythonzombie.tests',
    install_requires=requirements
)
