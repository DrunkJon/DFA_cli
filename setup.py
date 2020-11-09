from setuptools import setup

setup(
    name='DFA',
    version='1.0',
    py_modules=['DFA'],
    install_requires=[
      'Click',
    ],
    entry_points='''
        [console_scripts]
        dfa=dfa:cli
    '''
)
