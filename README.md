# picogeojson

[![Build Status](https://travis-ci.org/fortyninemaps/picogeojson.svg?branch=master)](https://travis-ci.org/fortyninemaps/picogeojson)

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

GeoJSON objects are constructed in Python using namedtuples.

```python
picogeojson.tostring(
    picogeojson.Point([1.0, 3.0])
)
# -> {"coordinates": [1.0, 3.0], "type": "Point"}'
```

Keyword arguments can be passed to `tostring` that
- enforce Polygon/MultiPolygon rotation direction, with counterclockwise for
  enternal rings and clockwise for internal rings
- split objects that cross the international dateline into multipart objects,
  for easier processing

For finer control, `Deserializer` and `Serializer` objects can be subclassed and
overloaded.

This is a standalone Python package extracted from the
[Karta](https://karta.fortyninemaps.com) `geojson` submodule.
