from setuptools import setup

setup(
    name='artifacts',
    version='0.0.1',
    description='Django Artifacts is a library for managing and deploying assets like JavaScript and SASS bundles in Django.',
    url='https://github.com/parisk/django-artifacts',
    author='Paris Kasidiaris, SourceLair PC',
    author_email='paris@sourcelair.com',
    license='MIT',
    packages=['artifacts'],
    install_requires=[
        'django',
    ]
)
