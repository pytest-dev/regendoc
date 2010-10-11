from setuptools import setup

setup(
    name='RegenDoc',
    version='0.1',
    url='http://bitbucket.org/RonnyPfannschmidt/regendoc/',
    author='Ronny Pfannschmidt',
    author_email='Ronny.Pfannschmidt@gmx.de',
    py_modules=['regendoc'],
    entry_points={
        'console_scripts': [
            'regendoc = regendoc:main',
        ]},
)
