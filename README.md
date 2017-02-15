# picogeojson

[![Build Status](https://travis-ci.org/fortyninemaps/picogeojson.svg?branch=master)](https://travis-ci.org/fortyninemaps/picogeojson)
[![Coverage Status](https://coveralls.io/repos/github/fortyninemaps/picogeojson/badge.svg?branch=master)](https://coveralls.io/github/fortyninemaps/picogeojson?branch=master)

Straightforward and compliant GeoJSON parsing and serialization with zero
dependencies. Easily ingest or output GeoJSON adhering to the
[IETF proposed standard](https://tools.ietf.org/html/rfc7946).

## Usage

GeoJSON files or strings are read using `fromfile()` or `fromstring()` (alias
`loads()`).

```python
result = picogeojson(fromstring('{"type": "Point", "coordinates": [1.0, 3.0]}'))
# -> Point(coordinates=[1.0, 3.0])
```

GeoJSON objects may be constructed in Python and composed (`merge()`) or split
(`burst()`).

GeoJSON objects are serialized with `tostring()` (alias `dumps()`).

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
- control whether a `bbox` member is computed and added to the JSON output

`Deserializer` and `Serializer` objects are provided for customization.

*picogeojson* will leverage [ujson](https://pypi.python.org/pypi/ujson) as a
backend if it is installed. Otherwise, it uses Python's built-in `json` module.

## Performance

The read benchmark involves reading a list of earthquake features. The write
benchmark involves serializing the continent of Australia.


|Module             |Read   |Write  |
|-------------------|-------|-------|
|json               |1.49   |2.00   |
|geojson            |6.74   |same   |
|picogeojson        |1.84   |same\* |
|picogeojson+ujson  |1.63   |0.31\* |

\*antimeridian cutting and polygon winding check set to `False`

This is a standalone Python package extracted from the
[Karta](https://karta.fortyninemaps.com) `geojson` submodule.
