''' Reflex setup.
'''

from distutils.core import setup

setup(name='Slate-bot',
    version='1.1',
    description='Python dAmn bot',
    author='photofroggy',
    author_email='froggywillneverdie@msn.com',
    url='http://www.github.com/photofroggy/Slate',
    packages=[
        'reflex',
        'dAmnViper',
        'dAmnViper.dA',
        'stutter',
        'slate',
        'slate.rules',
        'slate.rules.command',
        'extensions'
    ],
    platforms=['Any']
    '''classifiers=[
        'Natural Language :: English',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ],'''
    #long_description=""""""
)

# EOF
