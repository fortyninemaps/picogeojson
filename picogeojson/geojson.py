"""
Overview
--------

The functions

- `fromstring()` and `fromfile()` return namedtuples from GeoJSON input.
- `tostring()` returns GeoJSON from a namedtuple.

Likewise,

- `Deserializer` converts GeoJSON strings or files to named tuples.
- `Serializer` validates and converts named tuples to GeoJSON strings.
"""

import json
from .types import (Point, LineString, Polygon,
                    MultiPoint, MultiLineString, MultiPolygon,
                    GeometryCollection, Feature, FeatureCollection)

from .antimeridian import antimeridian_cut
from .orientation import is_counterclockwise

DEFAULTCRS = {"type": "name",
              "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}

class NumpyAwareJSONEncoder(json.JSONEncoder):
    """ Numpy-specific numbers prior to 1.9 don't inherit from Python numeric
    ABCs. This class is a hack to coerce numpy values into Python types for
    JSON serialization. """

    def default(self, o):
        if not hasattr(o, "dtype") or (hasattr(o, "__len__") and (len(o) != 1)):
            return json.JSONEncoder.default(self, o)
        elif o.dtype in ("int8", "int16", "int32", "int64"):
            return int(o)
        elif o.dtype in ("float16", "float32", "float64", "float128"):
            return float(o)
        elif o.dtype in ("complex64", "complex128", "complex256"):
            return complex(o)
        else:
            raise TypeError("not a recognized type")

class Deserializer(object):

    def __init__(self, defaultcrs=DEFAULTCRS):
        """ Parses GeoJSON strings and returns namedtuples. Strings can be
        passed by file using deserializer.fromfile() or by value using
        deserializer.fromstring().
        """
        self.jsondict = {}
        self.defaultcrs = defaultcrs
        return

    def __call__(self, f):
        try:
            return self.fromstring(f)
        except ValueError:
            return self.fromfile(f)

    def fromstring(self, s):
        self.jsondict = json.loads(s)
        return self.deserialize()

    def fromfile(self, f):
        if hasattr(f, 'read'):
            self.jsondict = json.load(f)
            return self.deserialize()
        elif isinstance(f, str):
            with open(f) as f:
                self.jsondict = json.load(f)
            return self.deserialize()
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

    def deserialize(self, d=None):
        if d is None:
            d = self.jsondict
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

    *enforce_poly_winding* ensures that serialized Polygons and MultiPolygons
    have counterclockwise external boundaries and clockwise internal boundaries
    (holes)
    """

    def __init__(self, antimeridian_cutting=True, enforce_poly_winding=True):
        self.antimeridian_cutting = antimeridian_cutting
        self.enforce_poly_winding = enforce_poly_winding
        return

    def __call__(self, geom, indent=None):
        return json.dumps(self.geometry_asdict(geom), indent=indent,
                          cls=NumpyAwareJSONEncoder)

    def geometry_asdict(self, geom):
        if isinstance(geom, Feature):
            return self.feature_asdict(geom)
        elif isinstance(geom, GeometryCollection):
            return self.geometry_collection_asdict(geom)
        elif isinstance(geom, FeatureCollection):
            return self.feature_collection_asdict(geom)
        else:
            return self._geometry_asdict(geom)

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

    def _geometry_asdict(self, geom):
        if not isinstance(geom.crs, dict):
            crs = self.crsdict(geom.crs)
        else:
            crs = geom.crs

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

        if crs is not None:
            d["crs"] = crs
        return d

    def feature_asdict(self, feature):
        d = {"type": "Feature",
             "geometry": self.geometry_asdict(feature.geometry),
             "properties": feature.properties}
        if feature.id is not None:
            d["id"] = feature.id
        if feature.crs is not None:
            d["crs"] = feature.crs
        return d

    def geometry_collection_asdict(self, gcollection):
        d = {"type": "GeometryCollection",
             "geometries": [self.geometry_asdict(g) for g in gcollection.geometries]}
        if gcollection.crs is not None:
            d["crs"] = gcollection.crs
        return d

    def feature_collection_asdict(self, fcollection):
        d = {"type": "FeatureCollection",
             "features": [self.feature_asdict(f) for f in fcollection.features]}
        if fcollection.crs is not None:
            d["crs"] = fcollection.crs
        return d

def asfixedlist(A):
    """ Recursively convert nested iterables or coordinates to nested lists at
    fixed precision. """
    if hasattr(A, '__iter__'):
        return [asfixedlist(el) for el in A]
    else:
        return round(A, 6)

def fromfile(f, **kw):
    d = Deserializer(**kw)
    return d.fromfile(f)

def fromstring(s, **kw):
    d = Deserializer(**kw)
    return d.fromstring(s)

def tostring(geom, **kw):
    s = Serializer(**kw)
    return s(geom)
