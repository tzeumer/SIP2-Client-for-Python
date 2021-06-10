from setuptools import setup

setup (
    name='Sip2',
    version='1.1',
    description='SIP2 Python Client: Simple Interchange Protocol Client for Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Tobias Zeumer',
    author_email='tzeumer@verweisungsform.de',
    url='https://github.com/tzeumer/SIP2-Client-for-Python',
    license='MIT',
    packages=['Sip2'],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries',
    ],
)