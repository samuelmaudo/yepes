# -*- coding:utf-8 -*-

from __future__ import unicode_literals, with_statement

import os
import sys

from distutils.sysconfig import get_python_lib
from setuptools import setup, find_packages

# Warn if we are installing over top of an existing installation. This can
# cause issues where files that were deleted from a more recent Yepes are
# still present in site-packages.
overlay_warning = False
if 'install' in sys.argv:
    lib_paths = [get_python_lib()]
    if lib_paths[0].startswith('/usr/lib/'):
        # We have to try also with an explicit prefix of /usr/local in order to
        # catch Debian's custom user site-packages directory.
        lib_paths.append(get_python_lib(prefix='/usr/local'))

    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path, 'yepes'))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break


# Dynamically calculate the version based on yepes.VERSION.
version = __import__('yepes').get_version()


setup(
    name='Yepes',
    version=version,
    url='http://www.samuelmaudo.com/yepes/',
    author='Samuel Maudo García',
    author_email='samuelmaudo@gmail.com',
    description='An extensive set of tools for Django projects.',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)


if overlay_warning:
    sys.stderr.write("""

========
WARNING!
========

You have just installed Yepes over top of an existing
installation, without removing it first. Because of this,
your install may now include extraneous files from a
previous version that have since been removed from
Yepes. This is known to cause a variety of problems. You
should manually remove the

{existing_path}

directory and re-install Yepes.

""".format(existing_path=existing_path))

