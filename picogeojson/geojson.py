"""
Overview
--------

The functions

- `fromstring()` and `fromfile()` return namedtuples from GeoJSON input
- `tostring()` returns GeoJSON from a namedtuple
- `result_fromstring()` and `result_fromfile()` return namedtuples wrapped as a
  *Result* so that values of a specific types can be safely extracted

Additionally,

- `loads()` and `dumps()` are aliases for `fromstring()` and `tostring()`

The functions above use the lower-level classes

- `Deserializer` to convert GeoJSON strings or files to named tuples
- `Serializer` to validate and convert named tuples to GeoJSON strings
"""

import os
import copy

try:
    assert os.environ.get("PICOGEOJSON_PYJSON", "0") == "1"
    import ujson as json
    _INDENT = 0
except (AssertionError, ImportError):
    import json
    _INDENT = None

from .types import (Point, LineString, Polygon,
                    MultiPoint, MultiLineString, MultiPolygon,
                    GeometryCollection, Feature, FeatureCollection)

from .antimeridian import antimeridian_cut
from .bbox import (geom_bbox, geometry_collection_bbox,
                   feature_bbox, feature_collection_bbox)
from .result import Result

DEFAULTCRS = {"type": "name",
              "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}

def docstring_insert(*s):
    def wrapped(obj):
        try:
            obj.__doc__ = obj.__doc__.format(*s)
        except (AttributeError, TypeError):
            # class __doc__ attribute not writable in Python 2
            # and in PyPy an TypeError is raised rather than an AttributeError
            pass
        return obj
    return wrapped

deserializer_args = """
    Parameters
    ----------

    defaultcrs : dict, optional
        Default CRS member for incoming geometries. When inputs have no CRS
        member, this CRS is assumed. In accordance with RFC 7946, this is taken
        to be longitude and latitude on the WGS84 ellipsoid, however this
        behaviour may be altered by assigning to the DEFAULTCRS module
        variable.
    """

@docstring_insert(deserializer_args)
class Deserializer(object):
    """ Parses GeoJSON strings and returns namedtuples. Strings can be passed
    by file using deserializer.fromfile() or by value using
    deserializer.fromstring().

    {}"""
    def __init__(self, defaultcrs=None):
        if defaultcrs is None:
            defaultcrs = DEFAULTCRS
        self.defaultcrs = defaultcrs
        return

    def __call__(self, f):
        try:
            return self.fromstring(f)
        except (TypeError, ValueError):
            return self.fromfile(f)

    def fromstring(self, s):
        return self.deserialize(json.loads(s))

    def fromfile(self, f):
        if hasattr(f, 'read'):
            return self.deserialize(json.load(f))
        elif hasattr(f, 'open'):
            with f.open() as f:
                return self.deserialize(json.load(f))
        with open(f) as f:
            return self.deserialize(json.load(f))

    def _parsePoint(self, d):
        crs = d.get("crs", self.defaultcrs)
        return Point(d["coordinates"], crs)

    def _parseMultiPoint(self, d):
        crs = d.get("crs", self.defaultcrs)
        return MultiPoint(d["coordinates"], crs)

    def _parseLineString(self, d):
        crs = d.get("crs", self.defaultcrs)
        return LineString(d["coordinates"], crs)

    def _parseMultiLineString(self, d):
        crs = d.get("crs", self.defaultcrs)
        return MultiLineString(d["coordinates"], crs)

    def _parsePolygon(self, d):
        crs = d.get("crs", self.defaultcrs)
        coords = copy.copy(d["coordinates"])
        for i, ring in enumerate(coords):
            if ring[0] != ring[-1]:
                ring.append(ring[0])
        return Polygon(coords, crs)

    def _parseMultiPolygon(self, d):
        crs = d.get("crs", self.defaultcrs)
        coords = copy.deepcopy(d["coordinates"])
        for j, polygon in enumerate(coords):
            for i, ring in enumerate(polygon):
                if ring[0] != ring[-1]:
                    ring.append(ring[0])
        return MultiPolygon(coords, crs)

    def _parseGeometryCollection(self, o):
        crs = o.get("crs", self.defaultcrs)
        geoms = [self.deserialize(g) for g in o["geometries"]]
        return GeometryCollection(geoms, crs)

    def _parseFeature(self, o):
        crs = o.get("crs", self.defaultcrs)
        geom = self.deserialize(o["geometry"])
        prop = o["properties"]
        fid = o.get("id", None)
        return Feature(geom, prop, fid, crs)

    def _parseFeatureCollection(self, o):
        crs = o.get("crs", self.defaultcrs)
        features = [self._parseFeature(f) for f in o["features"]]
        return FeatureCollection(features, crs)

    def deserialize(self, d):
        t = d["type"]
        if t == "FeatureCollection":
            return self._parseFeatureCollection(d)
        elif t == "Feature":
            return self._parseFeature(d)
        elif t == "Point":
            return self._parsePoint(d)
        elif t == "MultiPoint":
            return self._parseMultiPoint(d)
        elif t == "LineString":
            return self._parseLineString(d)
        elif t == "MultiLineString":
            return self._parseMultiLineString(d)
        elif t == "Polygon":
            return self._parsePolygon(d)
        elif t == "MultiPolygon":
            return self._parseMultiPolygon(d)
        elif t == "GeometryCollection":
            return self._parseGeometryCollection(d)
        else:
            raise TypeError("Unrecognized type {0}".format(t))

serializer_args = """
    Parameters
    ----------
    antimeridian_cutting : bool
        Indicates whether geometries spanning the dateline should be split,
        possibly changing type in the process (e.g. LineString to
        MultiLineString) (default True).

    write_bbox : bool
        Attempt to write a `bbox` member (default True).

    write_crs : bool
        Causes geometries and features to have a `crs` member (default False).

    precision : int
        If set, restricts the precision after the decimal in the output
    """

@docstring_insert(serializer_args)
class Serializer(object):
    """ Class for converting GeoJSON named tuples to GeoJSON.

    Usage:

        serializer = GeoJSONSerializer(antimeridian_cutting=True)
        json_string = serializer(named_tuple)

    {}"""
    def __init__(self, antimeridian_cutting=True, write_bbox=True, write_crs=False, precision=None):
        self.antimeridian_cutting = antimeridian_cutting
        self.write_bbox = write_bbox
        self.write_crs = write_crs
        if precision is None:
            self.prepare_coords = identity
        else:
            self.prepare_coords = lambda cx: fixed_precision(cx, precision)
        return

    def __call__(self, geom, indent=_INDENT):
        return json.dumps(self.geojson_asdict(geom), indent=indent)

    def geojson_asdict(self, geom, root=True):

        if isinstance(geom, Feature):
            return self.feature_asdict(geom, root=True)

        elif isinstance(geom, GeometryCollection):
            return self.geometry_collection_asdict(geom, root=True)

        elif isinstance(geom, FeatureCollection):
            return self.feature_collection_asdict(geom, root=True)

        else:   # bare single geometry

            if self.antimeridian_cutting:
                if type(geom).__name__ in ("LineString", "Polygon",
                                           "MultiLineString", "MultiPolygon",
                                           "GeometryCollection", "Feature",
                                           "FeatureCollection"):
                    geom = antimeridian_cut(geom)

            d = {"type": type(geom).__name__,
                 "coordinates": self.prepare_coords(geom.coordinates)}

            if root and self.write_bbox:
                bb = geom_bbox(geom)
                if bb is not None:
                    d["bbox"] = bb

            if root and self.write_crs and (geom.crs is not None):
                d["crs"] = geom.crs
            return d

    def feature_asdict(self, feature, root=True):
        d = {"type": "Feature",
             "geometry": self.geojson_asdict(feature.geometry, root=False),
             "properties": feature.properties}

        if feature.id is not None:
            d["id"] = feature.id

        if root and self.write_bbox:
            bb = feature_bbox(feature)
            if bb is not None:
                d["bbox"] = bb

        if root and self.write_crs and (feature.crs is not None):
            d["crs"] = feature.crs
        return d

    def geometry_collection_asdict(self, coll, root=True):
        d = {"type": "GeometryCollection",
             "geometries": [self.geojson_asdict(g, root=False)
                            for g in coll.geometries]}

        if root and self.write_bbox:
            bb = geometry_collection_bbox(coll)
            if bb is not None:
                d["bbox"] = bb

        if root and self.write_crs and (coll.crs is not None):
            d["crs"] = coll.crs
        return d

    def feature_collection_asdict(self, coll, root=True):
        d = {"type": "FeatureCollection",
             "features": [self.feature_asdict(f, root=False) for f in coll.features]}

        if self.write_bbox:
            bb = feature_collection_bbox(coll)
            if bb is not None:
                d["bbox"] = bb

        if root and self.write_crs and (coll.crs is not None):
            d["crs"] = coll.crs
        return d

def identity(A):
    return A

def fixed_precision(A, prec=6):
    """ Recursively convert nested iterables or coordinates to nested lists at
    fixed precision. """
    if hasattr(A, '__iter__'):
        return [fixed_precision(el, prec=prec) for el in A]
    else:
        return round(A, prec)

@docstring_insert(deserializer_args)
def fromdict(dct, **kw):
    """ Read a dictionary and return the GeoJSON object.
    {} """
    d = Deserializer(**kw)
    return d.deserialize(dct)

@docstring_insert(deserializer_args)
def fromfile(f, **kw):
    """ Read a JSON file and return the GeoJSON object.
    {} """
    d = Deserializer(**kw)
    return d.fromfile(f)

@docstring_insert(deserializer_args)
def fromstring(s, **kw):
    """ Read a JSON string and return the GeoJSON object.
    {} """
    d = Deserializer(**kw)
    return d.fromstring(s)

@docstring_insert(deserializer_args)
def result_fromfile(f, **kw):
    """ Read a JSON file and return a *Result*.
    {} """
    d = Deserializer(**kw)
    return Result(d.fromfile(f))

@docstring_insert(deserializer_args)
def result_fromstring(s, **kw):
    """ Read a JSON string and return a *Result*.
    {} """
    d = Deserializer(**kw)
    return Result(d.fromstring(s))

@docstring_insert(serializer_args)
def todict(geom, **kw):
    """ Serialize *geom* to a dictionary.
    {} """
    s = Serializer(**kw)
    return s.geojson_asdict(geom)

@docstring_insert(serializer_args)
def tostring(geom, **kw):
    """ Serialize *geom* to a JSON string.
    {} """
    s = Serializer(**kw)
    return s(geom)

@docstring_insert(serializer_args)
def tofile(geom, f, **kw):
    """ Serialize *geom* to a file.
    {} """
    if hasattr(f, "write"):
        f.write(tostring(geom, **kw))
    elif hasattr(f, "open"):
        with f.open("w") as fobj:
            fobj.write(tostring(geom, **kw))
    else:
        with open(f, "w") as fobj:
            fobj.write(tostring(geom, **kw))

# Aliases for python-geojson compatibility
load = fromfile
dump = tofile
loads = fromstring
dumps = tostring
