from setuptools import setup, find_packages
import versionedcache

version = "%d.%d.%d" % versionedcache.VERSION

setup(
    name = 'versionedcache',
    version = version,
    description = 'django base library',
    long_description = '\n'.join((
        'django base library',
        'template for other libs',
    )),
    author = 'centrum holdings s.r.o',
    license = 'BSD',

    packages = find_packages(
        where = '.',
        exclude = ('docs', 'tests')
    ),

    include_package_data = True,

    entry_points={
        'setuptools.file_finders': ['dummy = setuptools_entry:dummylsfiles'],
    },

    install_requires = [
        'setuptools>=0.6b1',
    ],
)

