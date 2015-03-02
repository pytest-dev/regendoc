from setuptools import setup

setup(
    name='RegenDoc',
    version='0.2.dev1',
    description='a tool to check/fix simple file/shell examples'
                ' in documentation',
    url='http://bitbucket.org/RonnyPfannschmidt/regendoc/',
    author='Ronny Pfannschmidt',
    author_email='Ronny.Pfannschmidt@gmx.de',
    py_modules=['regendoc'],
    entry_points={
        'console_scripts': [
            'regendoc = regendoc:main',
        ]},
    install_requires=[
        'py', 'argparse'
    ],
)
