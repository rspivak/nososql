from setuptools import setup, find_packages

classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Software Development :: Interpreters
Operating System :: Unix
"""

long_description = """\
Overview
---------

This is an example of a simple Syntax-Directed Interpreter
for a subset of SQL called NO-SO-SQL :)

For simplicity reasons database is created and manipulated in memory.
"""

setup(
    name='nososql',
    version='0.1',
    url='http://github.com/rspivak/nososql',
    license='MIT',
    description='Syntax-Directed Interpreter for an SQL subset',
    author='Ruslan Spivak',
    author_email='ruslan.spivak@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['setuptools'],
    zip_safe=False,
    entry_points="""\
    [console_scripts]
    nososql = nososql.interpreter:main
    """,
    classifiers=filter(None, classifiers.split('\n')),
    long_description=long_description
    )
