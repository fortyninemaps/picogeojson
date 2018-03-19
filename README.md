# picogeojson

[![Build Status](https://travis-ci.org/fortyninemaps/picogeojson.svg?branch=master)](https://travis-ci.org/fortyninemaps/picogeojson)
[![Coverage Status](https://coveralls.io/repos/github/fortyninemaps/picogeojson/badge.svg?branch=master)](https://coveralls.io/github/fortyninemaps/picogeojson?branch=master)

Straightforward and compliant GeoJSON parsing and serialization. Easily
ingest or output GeoJSON adhering to [RFC
7946](https://tools.ietf.org/html/rfc7946). Pure-Python.

## Encoding and Decoding

GeoJSON files or strings are read using `fromstring()` (alias
`loads()`), `fromfile()`,  or `fromdict()`.

```python
pt = picogeojson.fromstring('{"type": "Point", "coordinates": [1.0, 3.0]}')
# -> Point(coordinates=[1.0, 3.0])
```

GeoJSON objects are serialized with `tostring()` (alias `dumps()`),
`tofile()`, or `todict()`.

```python
picogeojson.tostring(
    picogeojson.Point([1.0, 3.0])
)
# -> {"coordinates": [1.0, 3.0], "type": "Point"}'
```

Keyword arguments can be passed to `tostring()` that
- enforce Polygon/MultiPolygon rotation direction, with counterclockwise for
  external rings and clockwise for internal rings (`enforce_poly_winding`)
- split objects that cross the international dateline into multipart objects,
  for easier processing (`antimeridian_cutting`)
- control whether `bbox` or `crs` objects are added to the JSON output
  (`write_bbox` and `write_crs`)

*picogeojson* will leverage [ujson](https://pypi.python.org/pypi/ujson) as a
backend if it is installed. Otherwise, it uses Python's built-in `json` module.

## Extractors

Using a blob of GeoJSON from a source you don't control is can be tedious -
there's a lot of error checking to be performed to see what exactly an API
request gave you. For that reason, *picogeojson* includes "extractors", which
are classes that wrap an unknown GeoJSON object and perform all the unfun due
diligence in the background.

```python
result = picogeojson.result_fromstring(response_from_a_strangers_api.text)

# Expecting one or more points or multipoints
for geom in result.points:
    # do something with points
    # ...

for geom in result.multilinestrings:
    # do something with multilinestrings
    # ...
```

This works for Features too, and we can filter by the `.properties` member.

```python
result = picogeojson.result_fromstring(json_from_some_guys_van.decode("utf-8"))

for feature in result.features("Polygon", {"type": "Lake", "state": "Oregon"}):
    # do something with lakes in Oregon
    # ...
```

## Applying transformations

Say you have a collection of GeoJSON objects and you want to apply a
computation to its elements - such as reprojecting coordinates or altering
Feature properties. Rather than unpack and repack the GeoJSON classes, use
`.map`.

```python
gc = GeometryCollection(...)

# A GeometryCollection's .map takes a function that takes a geometry and returns a geometry
def geometry_projector(geometry):
    ...
    return projected_geometry

projected_gc = gc.map(geometry_projector)
```

What if the mapping isn't 1-to-1, e.g. the function could return zero or
multiple objects? Use `.flatmap`!

```python
map_data = FeatureCollection(...)

# A GeometryCollection's .map takes a function that takes a geometry and returns a geometry
def remove_all_the_roads(feature):
    if feature.properties["type"] == "road":
        return FeatureCollection([])
    return FeatureCollection([feature])

roadless_map_data = map_data.flatmap(remove_all_the_roads)
```

Features also provide `.map_geometry` and a `.map_properties` methods. And of
course, all of these can be chained.

## Miscellaneous

GeoJSON objects may be constructed in Python and composed (`merge()`) or split
(`burst()`).

```python
points = [picogeojson.Point((1, 2)),
          picogeojson.Point((3, 4)),
          picogeojson.Point((5, 6))]

merged_points = picogeojson.merge(points)
# -> MultiPoint(coordinates=[(1, 2), (3, 4), (5, 6)])

split_points = picogeojson.burst(merged_points)
# -> [Point((1, 2)), Point((3, 4)), Point((5, 6))]
```

## Performance

These benchmarks are pretty flawed, and performance mostly depends on the
underlying JSON library. Still, it looks like *picogeojson* holds its own.
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
