# picogeojson

[![Build Status](https://travis-ci.org/fortyninemaps/picogeojson.svg?branch=master)](https://travis-ci.org/fortyninemaps/picogeojson)
[![Coverage Status](https://coveralls.io/repos/github/fortyninemaps/picogeojson/badge.svg?branch=master)](https://coveralls.io/github/fortyninemaps/picogeojson?branch=master)

Straightforward and compliant GeoJSON parsing and serialization with zero
dependencies. Easily ingest or output GeoJSON adhering to the
[IETF proposed standard](https://tools.ietf.org/html/rfc7946).

## Documentation

GeoJSON strings or files are read using the `fromstring()` and `fromfile()`
functions.

```python
result = picogeojson(fromstring('{"type": "Point", "coordinates": [1.0, 3.0]}'))
# -> Point(coordinates=[1.0, 3.0])
```

GeoJSON objects are constructed in Python and serialized with `tostring()`.

```python
picogeojson.tostring(
    picogeojson.Point([1.0, 3.0])
)
# -> {"coordinates": [1.0, 3.0], "type": "Point"}'
```

Keyword arguments can be passed to `tostring()` that
- enforce Polygon/MultiPolygon rotation direction, with counterclockwise for
  external rings and clockwise for internal rings
- split objects that cross the international dateline into multipart objects,
  for easier processing
- alter

`Deserializer` and `Serializer` objects are provided for customization.

This is a standalone Python package extracted from the
[Karta](https://karta.fortyninemaps.com) `geojson` submodule.
