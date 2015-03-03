from setuptools import setup

args = dict(
    name='RegenDoc',
    use_scm_version=True,
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
        'click',
    ],
    setup_requires=[
        'setuptools_scm',
    ]
)

if __name__ == '__main__':
    setup(**args)
