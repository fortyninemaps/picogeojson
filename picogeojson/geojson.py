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
_INDENT = None
if os.environ.get("PICOGEOJSON_PYJSON", "0") == "1":
    print("Using 'json' module because PICOGEOJSON_PYJSON is set")
    import json
else:
    try:
        import ujson as json
        _INDENT = 0
    except ImportError:
        import json

from .types import (Point, LineString, Polygon,
                    MultiPoint, MultiLineString, MultiPolygon,
                    GeometryCollection, Feature, FeatureCollection)

from .antimeridian import antimeridian_cut
from .orientation import is_counterclockwise
from .bbox import geom_bbox, geometry_collection_bbox, feature_bbox, feature_collection_bbox
from .result import GeoJSONResult

DEFAULTCRS = {"type": "name",
              "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}

class Deserializer(object):

    def __init__(self, defaultcrs=DEFAULTCRS):
        """ Parses GeoJSON strings and returns namedtuples. Strings can be
        passed by file using deserializer.fromfile() or by value using
        deserializer.fromstring().
        """
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

class Serializer(object):
    """ Class for converting GeoJSON named tuples to GeoJSON.

    Usage:

        serializer = GeoJSONSerializer(antimeridian_cutting=True)
        json_string = serializer(named_tuple)

    *antimeridian_cutting* indicates whether geometries spanning the dateline
    should be split, possibly changing type in the process (e.g. LineString to
    MultiLineString)

    *enforce_poly_winding* ensures that serialized Polygon and MultiPolygon
    instances have counterclockwise external boundaries and clockwise internal
    boundaries (holes)

    *write_bbox* causes geometries and features to have a `bbox` member
    """

    def __init__(self, antimeridian_cutting=True, enforce_poly_winding=True, write_bbox=True):
        self.antimeridian_cutting = antimeridian_cutting
        self.enforce_poly_winding = enforce_poly_winding
        self.write_bbox = write_bbox
        return

    def __call__(self, geom, indent=_INDENT):
        return json.dumps(self.geojson_asdict(geom), indent=indent)

    def geojson_asdict(self, geom, parent_crs=None):
        if isinstance(geom, Feature):
            return self.feature_asdict(geom, parent_crs=parent_crs)
        elif isinstance(geom, GeometryCollection):
            return self.geometry_collection_asdict(geom)
        elif isinstance(geom, FeatureCollection):
            return self.feature_collection_asdict(geom)
        else:
            return self._geometry_asdict(geom, parent_crs=parent_crs)

    @staticmethod
    def crsdict(crs=None, urn=None, href="", linktype="proj4"):
        """ Return a dictionary that can be serialized as a GeoJSON coordinate
        system mapping using a *urn* or a *crs* instance.

        In the case of a linked CRS, the link address and type can be specified
        using the `href` and `linktype` keyword arguments.

        For more details, see the GeoJSON specification at:
        http://geojson.org/geojson-spec.html#coordinate-reference-system-objects
        """
        if urn is not None:
            return {'type': 'name',
                    'properties': {'name': urn}}
        elif crs is not None:
            if hasattr(crs, "jsonhref") and hasattr(crs, "jsontype"):
                d = {'type': 'link',
                     'properties': {'href': crs.jsonname,
                                    'type': crs.jsontype}}
            elif hasattr(crs, "jsonname"):
                d = {'type': 'name',
                     'properties': {'name': crs.jsonname}}
            else:
                d = {'type': 'link',
                     'properties': {'href': href,
                                    'type': linktype}}
            return d
        else:
            return None

    def _geometry_asdict(self, geom, parent_crs=None):
        if geom.crs is not None and geom.crs == parent_crs:
            crs = None
        elif geom.crs is None or isinstance(geom.crs, dict):
            crs = geom.crs
        else:
            crs = self.crsdict(geom.crs)

        if self.antimeridian_cutting:
            if type(geom).__name__ in ("LineString", "Polygon", "MultiLineString",
                                        "MultiPolygon", "GeometryCollection",
                                        "Feature", "FeatureCollection"):
                geom = antimeridian_cut(geom)

        d = {"type": type(geom).__name__,
             "coordinates": geom.coordinates}

        if self.enforce_poly_winding:
            if type(geom).__name__ == "Polygon":
                cx = d["coordinates"]
                for i, ring in enumerate(cx):
                    if bool(i) is is_counterclockwise(ring):
                        cx[i] = ring[::-1]
            elif type(geom).__name__ == "MultiPolygon":
                for j, cx in enumerate(d["coordinates"]):
                    for i, ring in enumerate(cx):
                        if bool(i) is is_counterclockwise(ring):
                            cx[i] = ring[::-1]

        if self.write_bbox:
            d["bbox"] = geom_bbox(geom)

        if crs is not None:
            d["crs"] = crs
        return d

    def feature_asdict(self, feature, parent_crs=None):
        d = {"type": "Feature",
             "geometry": self.geojson_asdict(feature.geometry, parent_crs=feature.crs),
             "properties": feature.properties}
        if feature.id is not None:
            d["id"] = feature.id
        if feature.crs is not None and feature.crs != parent_crs:
            d["crs"] = feature.crs

        if self.write_bbox:
            d["bbox"] = feature_bbox(feature)
        return d

    def geometry_collection_asdict(self, coll):
        d = {"type": "GeometryCollection",
             "geometries": [self.geojson_asdict(g, parent_crs=coll.crs)
                            for g in coll.geometries]}

        if self.write_bbox:
            d["bbox"] = geometry_collection_bbox(coll)

        if coll.crs is not None:
            d["crs"] = coll.crs
        return d

    def feature_collection_asdict(self, coll):
        d = {"type": "FeatureCollection",
             "features": [self.feature_asdict(f, parent_crs=coll.crs)
                          for f in coll.features]}

        if self.write_bbox:
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

def fromfile(f, **kw):
    d = Deserializer(**kw)
    return d.fromfile(f)

def fromstring(s, **kw):
    d = Deserializer(**kw)
    return d.fromstring(s)

def result_fromfile(f, **kw):
    d = Deserializer(**kw)
    return GeoJSONResult(d.fromfile(f))

def result_fromstring(s, **kw):
    d = Deserializer(**kw)
    return GeoJSONResult(d.fromstring(s))

def tostring(geom, **kw):
    s = Serializer(**kw)
    return s(geom)

# Aliases for python-geojson compatibility
loads = fromstring
dumps = tostring
