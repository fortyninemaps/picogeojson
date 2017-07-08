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
        install_requires = ["attrs>=17.0.0"],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Topic :: Scientific/Engineering :: GIS',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            ],
        keywords="minimal geojson",
        packages=find_packages(exclude=["tests"]),
        description="RFC-7946 compliant GeoJSON parser and emitter",
        long_description="""
picogeojson
===========

|Build Status| |Coverage Status|

Straightforward and compliant GeoJSON parsing and serialization with
zero dependencies. Easily ingest or output GeoJSON adhering to `RFC
7946 <https://tools.ietf.org/html/rfc7946>`__.

Usage
-----

GeoJSON files or strings are read using ``fromfile()`` or
``fromstring()`` (alias ``loads()``).

.. code:: python

    pt = picogeojson.fromstring('{"type": "Point", "coordinates": [1.0, 3.0]}')
    # -> Point(coordinates=[1.0, 3.0])

Sometimes a particular type of GeoJSON object is expected (e.g. from an
API GET request), but for safety the type needs to be checked.
Alternatively, the ``result_fromstring()`` function can be used, which
returns an object with safe accessors for specific GeoJSON types.

.. code:: python

    result = picogeojson.result_fromstring(api_response.decode("utf-8"))

    # Expecting one or more points or multipoints
    for geom in result.points:
        # do something with points
        # ...

    for geom in result.multilinestrings:
        # do something with multilinestrings
        # ...

This works for Features too, and we can filter by the ``.properties``
member.

.. code:: python

    result = picogeojson.result_fromstring(api_response.decode("utf-8"))

    for feature in result.features("Polygon", {"type": "Lake", "state": "Oregon"}):
        # do something with lakes in Oregon
        # ...

GeoJSON objects may be constructed in Python and composed (``merge()``)
or split (``burst()``).

.. code:: python

    points = [picogeojson.Point((1, 2)),
              picogeojson.Point((3, 4)),
              picogeojson.Point((5, 6))]

    merged_points = picogeojson.merge(points)
    # -> MultiPoint(coordinates=[(1, 2), (3, 4), (5, 6)])

    split_points = picogeojson.burst(merged_points)
    # -> [Point((1, 2)), Point((3, 4)), Point((5, 6))]

GeoJSON objects are serialized with ``tostring()`` (alias ``dumps()``).

.. code:: python

    picogeojson.tostring(
        picogeojson.Point([1.0, 3.0])
    )
    # -> {"coordinates": [1.0, 3.0], "type": "Point"}'

Keyword arguments can be passed to ``tostring()`` that - enforce
Polygon/MultiPolygon rotation direction, with counterclockwise for
external rings and clockwise for internal rings
(``enforce_poly_winding``) - split objects that cross the international
dateline into multipart objects, for easier processing
(``antimeridian_cutting``) - control whether a ``bbox`` member is
computed and added to the JSON output (``write_bbox``)

*picogeojson* will leverage
`ujson <https://pypi.python.org/pypi/ujson>`__ as a backend if it is
installed. Otherwise, it uses Python's built-in ``json`` module.

Performance
-----------

The read benchmark involves reading a list of earthquake features. The
write benchmark involves serializing the continent of Australia.

+---------------------+--------+----------+
| Module              | Read   | Write    |
+=====================+========+==========+
| json                | 1.49   | 2.00     |
+---------------------+--------+----------+
| geojson             | 6.74   | same     |
+---------------------+--------+----------+
| picogeojson         | 1.84   | same\*   |
+---------------------+--------+----------+
| picogeojson+ujson   | 1.63   | 0.31\*   |
+---------------------+--------+----------+

\*antimeridian cutting and polygon winding check set to ``False``

This is a standalone Python package extracted from the
`Karta <https://karta.fortyninemaps.com>`__ ``geojson`` submodule.

.. |Build Status| image:: https://travis-ci.org/fortyninemaps/picogeojson.svg?branch=master
   :target: https://travis-ci.org/fortyninemaps/picogeojson
.. |Coverage Status| image:: https://coveralls.io/repos/github/fortyninemaps/picogeojson/badge.svg?branch=master
   :target: https://coveralls.io/github/fortyninemaps/picogeojson?branch=master
"""
)
