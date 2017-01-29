import os.path
from setuptools import setup, find_packages

path = os.path.split(__file__)[0]
with open(os.path.join(path, "picogeojson/__init__.py")) as f:
    version = f.readline().split("=")[1].strip().strip('"')

setup(
        name="picogeojson",
        version=version,
        author="Nat Wilson",
        author_email="natw@fortyninemaps.com",
        license="MIT",
        install_requires = ["attrs>=16.3.0"],
        classifiers=[
            'Development Status :: 4 - Beta',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',

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
            'Programming Language :: Python :: 3.6',

            'Topic :: Scientific/Engineering :: GIS'
            ],
        keywords="minimal geojson",
        packages=find_packages(exclude=["tests"]),
        description="Minimal GeoJSON parser and emitter",
        long_description=""""
picogeojson
===========

|Build Status| |Coverage Status|

Straightforward and compliant GeoJSON parsing and serialization with
zero dependencies. Easily ingest or output GeoJSON adhering to the `IETF
proposed standard <https://tools.ietf.org/html/rfc7946>`__.

Documentation
-------------

GeoJSON strings or files are read using the ``fromstring()`` and
``fromfile()`` functions.

.. code:: python

    result = picogeojson(fromstring('{"type": "Point", "coordinates": [1.0, 3.0]}'))
    # -> Point(coordinates=[1.0, 3.0])

GeoJSON objects are constructed in Python and serialized with
``tostring()``.

.. code:: python

    picogeojson.tostring(
        picogeojson.Point([1.0, 3.0])
    )
    # -> {"coordinates": [1.0, 3.0], "type": "Point"}'

Keyword arguments can be passed to ``tostring()`` that - enforce
Polygon/MultiPolygon rotation direction, with counterclockwise for
external rings and clockwise for internal rings - split objects that
cross the international dateline into multipart objects, for easier
processing - alter

``Deserializer`` and ``Serializer`` objects are provided for
customization.

This is a standalone Python package extracted from the
`Karta <https://karta.fortyninemaps.com>`__ ``geojson`` submodule.

.. |Build Status| image:: https://travis-ci.org/fortyninemaps/picogeojson.svg?branch=master
   :target: https://travis-ci.org/fortyninemaps/picogeojson
.. |Coverage Status| image:: https://coveralls.io/repos/github/fortyninemaps/picogeojson/badge.svg?branch=master
   :target: https://coveralls.io/github/fortyninemaps/picogeojson?branch=master
"""
)
