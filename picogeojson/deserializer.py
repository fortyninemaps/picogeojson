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

from .crs import DEFAULTCRS

from .map import Map

from .docstrings import docstring_insert

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
        geoms = [self._deserialize(g) for g in o["geometries"]]
        return GeometryCollection(geoms, crs)

    def _parseFeature(self, o):
        crs = o.get("crs", self.defaultcrs)
        geom = self._deserialize(o["geometry"])
        prop = o["properties"]
        fid = o.get("id", None)
        return Feature(geom, prop, fid, crs)

    def _parseFeatureCollection(self, o):
        crs = o.get("crs", self.defaultcrs)
        features = [self._parseFeature(f) for f in o["features"]]
        return FeatureCollection(features, crs)

    def _deserialize(self, d):
        t = d["type"]
        if t == "FeatureCollection":
            raw = self._parseFeatureCollection(d)
        elif t == "Feature":
            raw = self._parseFeature(d)
        elif t == "Point":
            raw = self._parsePoint(d)
        elif t == "MultiPoint":
            raw = self._parseMultiPoint(d)
        elif t == "LineString":
            raw = self._parseLineString(d)
        elif t == "MultiLineString":
            raw = self._parseMultiLineString(d)
        elif t == "Polygon":
            raw = self._parsePolygon(d)
        elif t == "MultiPolygon":
            raw = self._parseMultiPolygon(d)
        elif t == "GeometryCollection":
            raw = self._parseGeometryCollection(d)
        else:
            raise TypeError("Unrecognized type {0}".format(t))
        return raw

    def deserialize(self, d):
        return Map(self._deserialize(d))

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

