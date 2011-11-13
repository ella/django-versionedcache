from setuptools import setup, find_packages
import versionedcache

version = "%d.%d.%d" % versionedcache.VERSION

setup(
    name = 'django-versionedcache',
    version = version,
    description = 'django versioned cache',
    long_description = '\n'.join((
        'django versioned cache',
        '',
        'version aware memcache backend for django',
    )),
    author = 'centrum holdings s.r.o',
    license = 'BSD',

    packages = find_packages(
        where = '.',
        exclude = ('docs', 'tests')
    ),

    include_package_data = True,

    entry_points={
    },

    install_requires = [
        'setuptools>=0.6b1',
        'Django>=1.1',
    ],
)

