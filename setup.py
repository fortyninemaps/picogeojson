from setuptools import setup, find_packages
from picogeojson import __version__ as version

setup(
        name="picogeojson",
        version=version,
        description="A minimal geojson serializer and deserializer",
        author="Nat Wilson",
        author_email="natw@fortyninemaps.com",
        license="MIT",
        classifiers=[
            'Development Status :: 3 - Alpha',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: MIT License',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6'
            ],
        keywords="minimal geojson",
        packages=find_packages(exclude=["tests"])
)
