"""
Overview
--------

The functions

- `fromstring()` and `fromfile()` return namedtuples from GeoJSON input
- `tostring()` returns GeoJSON from a namedtuple
- `result_fromstring()` and `result_fromfile()` return namedtuples wrapped as a
  GeoJSONResult so that values of a specific types can be safely extracted

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
from .orientation import is_counterclockwise
from .bbox import geom_bbox, geometry_collection_bbox, feature_bbox, feature_collection_bbox
from .result import GeoJSONResult

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

def check_closed_ring(geom):
    if type(geom).__name__ == "Polygon":
        for ring in geom.coordinates:
            if tuple(ring[0]) != tuple(ring[-1]):
                return False
    elif type(geom).__name__ == "MultiPolygon":
        for poly in geom.coordinates:
            for ring in poly:
                if tuple(ring[0]) != tuple(ring[-1]):
                    return False
    return True

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
        elif isinstance(f, str):
            with open(f) as f:
                return self.deserialize(json.load(f))
        else:
            raise TypeError("input must be a file object or a filename")

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
        return Polygon(d["coordinates"], crs)

    def _parseMultiPolygon(self, d):
        crs = d.get("crs", self.defaultcrs)
        return MultiPolygon(d["coordinates"], crs)

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
        MultiLineString)

    enforce_poly_winding:
        Ensures that serialized Polygon and MultiPolygon instances have
        counterclockwise external boundaries and clockwise internal boundaries
        (holes). Note that some visualization backends (notably SVG and HTML
        Canvas) take the opposing convention.

    write_bbox : bool
        Causes geometries and features to have a `bbox` member.
    """

@docstring_insert(serializer_args)
class Serializer(object):
    """ Class for converting GeoJSON named tuples to GeoJSON.

    Usage:

        serializer = GeoJSONSerializer(antimeridian_cutting=True)
        json_string = serializer(named_tuple)

    {}"""
    def __init__(self, antimeridian_cutting=True, enforce_poly_winding=True, write_bbox=True):
        self.antimeridian_cutting = antimeridian_cutting
        self.enforce_poly_winding = enforce_poly_winding
        self.write_bbox = write_bbox
        return

    def __call__(self, geom, indent=_INDENT):
        return json.dumps(self.geojson_asdict(geom), indent=indent)

    def geojson_asdict(self, geom, parent_crs=None, write_bbox=None):
        if write_bbox is None:
            write_bbox = self.write_bbox

        if isinstance(geom, Feature):
            return self.feature_asdict(geom, write_bbox, parent_crs=parent_crs)

        elif isinstance(geom, GeometryCollection):
            return self.geometry_collection_asdict(geom, write_bbox)

        elif isinstance(geom, FeatureCollection):
            return self.feature_collection_asdict(geom, write_bbox)

        else:   # bare single geometry
            if geom.crs is not None and geom.crs == parent_crs:
                crs = None
            else:
                crs = geom.crs


            if type(geom).__name__ in ("Polygon", "MultiPolygon"):
                if not check_closed_ring(geom):
                    raise ValueError("open polygon ring")

            if self.antimeridian_cutting:
                if type(geom).__name__ in ("LineString", "Polygon",
                                           "MultiLineString", "MultiPolygon",
                                           "GeometryCollection", "Feature",
                                           "FeatureCollection"):
                    geom = antimeridian_cut(geom)

            d = {"type": type(geom).__name__,
                 "coordinates": geom.coordinates}

            if self.enforce_poly_winding:
                if type(geom).__name__ == "Polygon":
                    d["coordinates"] = copy.deepcopy(d["coordinates"])
                    cx = d["coordinates"]
                    for i, ring in enumerate(cx):
                        if bool(i) is is_counterclockwise(ring):
                            cx[i] = ring[::-1]
                elif type(geom).__name__ == "MultiPolygon":
                    d["coordinates"] = copy.deepcopy(d["coordinates"])
                    for j, cx in enumerate(d["coordinates"]):
                        for i, ring in enumerate(cx):
                            if bool(i) is is_counterclockwise(ring):
                                d["coordinates"][j][i] = ring[::-1]

            if write_bbox:
                d["bbox"] = geom_bbox(geom)

            if crs is not None:
                d["crs"] = crs
            return d

    def feature_asdict(self, feature, write_bbox=None, parent_crs=None):
        if write_bbox is None:
            write_bbox = self.write_bbox

        d = {"type": "Feature",
             "geometry": self.geojson_asdict(feature.geometry, write_bbox=False, 
                                             parent_crs=feature.crs),
             "properties": feature.properties}
        if feature.id is not None:
            d["id"] = feature.id
        if feature.crs is not None and feature.crs != parent_crs:
            d["crs"] = feature.crs

        if write_bbox:
            d["bbox"] = feature_bbox(feature)
        return d

    def geometry_collection_asdict(self, coll, write_bbox=None):
        if write_bbox is None:
            write_bbox = self.write_bbox

        d = {"type": "GeometryCollection",
             "geometries": [self.geojson_asdict(g, write_bbox=False,
                                                parent_crs=coll.crs)
                            for g in coll.geometries]}

        if write_bbox:
            d["bbox"] = geometry_collection_bbox(coll)

        if coll.crs is not None:
            d["crs"] = coll.crs
        return d

    def feature_collection_asdict(self, coll, write_bbox):
        d = {"type": "FeatureCollection",
             "features": [self.feature_asdict(f, False, parent_crs=coll.crs)
                          for f in coll.features]}

        if write_bbox:
            d["bbox"] = feature_collection_bbox(coll)

        if coll.crs is not None:
            d["crs"] = coll.crs
        return d

def fixed_precision(A, prec=6):
    """ Recursively convert nested iterables or coordinates to nested lists at
    fixed precision. """
    if hasattr(A, '__iter__'):
        return [fixed_precision(el, prec=prec) for el in A]
    else:
        return round(A, prec)

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
    """ Read a JSON file and return a GeoJSONResult.
    {} """
    d = Deserializer(**kw)
    return GeoJSONResult(d.fromfile(f))

@docstring_insert(deserializer_args)
def result_fromstring(s, **kw):
    """ Read a JSON string and return a GeoJSONResult.
    {} """
    d = Deserializer(**kw)
    return GeoJSONResult(d.fromstring(s))

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
    else:
        with open(f, "w") as fobj:
            fobj.write(tostring(geom, **kw))

# Aliases for python-geojson compatibility
load = fromfile
dump = tofile
loads = fromstring
dumps = tostring
