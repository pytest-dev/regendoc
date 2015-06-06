from setuptools import setup

args = dict(
    name='regendoc',
    use_scm_version=True,
    description='a tool to check/update simple file/shell '
                'examples in documentation',
    url='http://bitbucket.org/pytest-dev/regendoc/',
    author='Ronny Pfannschmidt',
    author_email='opensource@ronnypfannschmidt.de',
    packages=['regendoc'],
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
