# picogeojson

[![Build Status](https://travis-ci.org/fortyninemaps/picogeojson.svg?branch=master)](https://travis-ci.org/fortyninemaps/picogeojson)
[![Coverage Status](https://coveralls.io/repos/github/fortyninemaps/picogeojson/badge.svg?branch=master)](https://coveralls.io/github/fortyninemaps/picogeojson?branch=master)

# picogeojson

*picogeojson* is a Python library for reading, writing, and working with
GeoJSON. It emphasizes standard compliance ([RFC
7946](https://tools.ietf.org/html/rfc7946)) and ergonomics. It is a pure-Python
module for ease of installation and distribution.

## Encoding and Decoding

GeoJSON files or strings are read using `fromstring()`, `fromfile()`,  or
`fromdict()`.

```python
picogeojson.fromstring('{"type": "Point", "coordinates": [1.0, 3.0]}')
# -> <picogeojson.map.Map object at ...>
```

GeoJSON objects are serialized with `tostring()`, `tofile()`, or `todict()`.

```python
picogeojson.tostring(
    picogeojson.Point([1.0, 3.0])
)
# -> {"coordinates": [1.0, 3.0], "type": "Point"}'
```

All of the serialization functions accept the following options:

**`antimeridian_cutting`**: *bool*: Cuts geometries at the 180th meridian so
that they plot well on standard world maps.

**`write_bbox`**: *bool*: Write an optional `bbox` member to the GeoJSON object.

**`write_crs`**: *bool*: Write a non-standard `crs` member for non-WGS84
longitude-latitude coordinates.

**`precision`**: *int*: Restrict the number of decimal digits in the written
coordinates (5 results in precision of 1 meter or better for longitude-latitude
coordinates).

When reading GeoJSON, *picogeojson* returns a *Map* object, which is a container
for GeoJSON. Useful methods on *Map* objects include:

**`Map.extract(geotype)`**: creates a generator for geometries of type
*geotype*, as in

```python
geojson = picogeojson.loads(...)

for linestring in geojson.extract(picogeojson.LineString):
    print(linestring)
```

**`Map.extract_features(geotype=None, properties=None)`**: similar to
`Map.extract`, this extract GeoJSON features, optionally filtering by
properties.

```python
geojson = picogeojson.loads(...)

for lake in geojson.features("Polygon", {"type": "Lake", "state": "Oregon"}):
    lakes_in_oregon.append(lake)
```

**`Map.map(function, geotype)`**: returns a new `Map` with *function* applied to
every contained GeoJSON geometry of type *geotype*.

**`Map.map_features(function, geotype)`**: returns a new `Map` with *function*
applied to every contained GeoJSON feature containing geometry *geotype* and
matching *properties*.

## Types and transformations

In order to create or work with GeoJSON, *picogeojson* defines constructors for
all GeoJSON types:

```python
pt = picogeojson.Point([1.0, 3.5])

polygon = picogeojson.Polygon([[[100.0, 20.0], [102.0, 19.7], [102.3, 23.0],
                                [100.1, 22.8], [100.0, 20.0]]])

feature = picojson.Feature(polygon, {"id": "example polygon"})
```

When constructing geometries, *picogeojson* takes care of ensuring that
coordinate rings are closed and oriented correctly and that coordinates are
nested to the correct depth.

The following methods are available:

| Type               | `.transform` | `.map` | `.flatmap` |
|--------------------|--------------|--------|------------|
| Point              | x            | -      | -          |
| LineString         | x            | -      | -          |
| Polygon            | x            | -      | -          |
| MultiPoint         | x            | -      | -          |
| MultiLineString    | x            | -      | -          |
| MultiPolygon       | x            | -      | -          |
| GeometryCollection | x            | x      | x          |
| Feature            | x            | x      | -          |
| FeatureCollection  | x            | x      | x          |

**`.transform`** operates on coordinates, returning a new geometry or feature
with a function applied to each coordinate pair.

**`.map`** applies a function to each member of a *GeometryCollection* or
*FeatureCollection*. *Feature*s have a `.map_geometry` and a `.map_properties`
that apply functions to the underlying geometry or properties dict,
respectively.

**`.flatmap`** applies a function to each member of a collection, constructing a
new collection by concatenating the result of each application.

## Miscellaneous

GeoJSON objects may be composed (`merge()`) or split (`burst()`).

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

*picogeojson* uses [ujson](https://pypi.org/project/ujson/) if available,
otherwise falling back on the standard library.

*The following benchmarks are old and likely inaccurate.*

The read benchmark involves reading a list of earthquake features. The write
benchmark involves serializing the continent of Australia.

|Module             |Read   |Write  |
|-------------------|-------|-------|
|json               |1.49   |2.00   |
|geojson            |6.74   |same   |
|picogeojson        |1.84   |same\* |
|picogeojson+ujson  |1.63   |0.31\* |

\*antimeridian cutting and polygon winding check set to `False`
