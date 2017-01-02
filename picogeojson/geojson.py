"""
GeoJSON drivers for Karta

Defines named tuples representing GeoJSON entities.

Overview
--------

`GeoJSONReader` converts GeoJSON strings to named tuples.

`GeoJSONSerializer` converts named tuples to GeoJSON strings.

`as_named_tuple` function converts karta.geometry classes to equivalent named
tuples.
"""

import json
from functools import reduce

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

    def __init__(self, finput, defaultcrs=DEFAULTCRS):
        """ Create a reader-object for a GeoJSON-containing file or StreamIO
        object. Use as::

            with open(`fnm`, 'r') as f:
                reader = GeoJSONReader(f)
        """
        if hasattr(finput, 'read'):
            self.jsondict = json.load(finput)
        elif isinstance(finput, str):
            try:
                self.jsondict = json.loads(finput)
            except ValueError:
                with open(finput) as f:
                    self.jsondict = json.load(f)
        else:
            raise TypeError("*finput* must be a file object, a JSON string, or "
                            "a filename string")

        self.defaultcrs = defaultcrs
        return

    def parsePoint(self, d):
        crs = d.get("crs", self.defaultcrs)
        return Point(d["coordinates"], crs)

    def parseMultiPoint(self, d):
        crs = d.get("crs", self.defaultcrs)
        return MultiPoint(d["coordinates"], crs)

    def parseLineString(self, d):
        crs = d.get("crs", self.defaultcrs)
        return LineString(d["coordinates"], crs)

    def parseMultiLineString(self, d):
        crs = d.get("crs", self.defaultcrs)
        return MultiLineString(d["coordinates"], crs)

    def parsePolygon(self, d):
        crs = d.get("crs", self.defaultcrs)
        return Polygon(d["coordinates"], crs)

    def parseMultiPolygon(self, d):
        crs = d.get("crs", self.defaultcrs)
        return MultiPolygon(d["coordinates"], crs)

    def parseGeometryCollection(self, o):
        crs = o.get("crs", self.defaultcrs)
        geoms = [self.parse(g) for g in o["geometries"]]
        return GeometryCollection(geoms, crs)

    def parseFeature(self, o):
        crs = o.get("crs", self.defaultcrs)
        geom = self.parse(o["geometry"])
        if isinstance(geom, GeometryCollection):
            n = 1
        else:
            n = len(geom.coordinates)
        prop = self.parseProperties(o["properties"], n)
        fid = o.get("id", None)
        return Feature(geom, prop, fid, crs)

    def parseFeatureCollection(self, o):
        crs = o.get("crs", self.defaultcrs)
        features = [self.parseFeature(f) for f in o["features"]]
        return FeatureCollection(features, crs)

    @staticmethod
    def parseProperties(prop, geomlen):
        d = {"scalar":{},
             "vector":{}}
        for key, value in prop.items():
            if geomlen > 1 and hasattr(value, "__iter__") and len(value) == geomlen:
                d["vector"][key] = value
            else:
                d["scalar"][key] = value
        return d

    def parse(self, d=None):
        if d is None:
            d = self.jsondict
        t = d["type"]
        if t == "FeatureCollection":
            return self.parseFeatureCollection(d)
        elif t == "Feature":
            return self.parseFeature(d)
        elif t == "Point":
            return self.parsePoint(d)
        elif t == "MultiPoint":
            return self.parseMultiPoint(d)
        elif t == "LineString":
            return self.parseLineString(d)
        elif t == "MultiLineString":
            return self.parseMultiLineString(d)
        elif t == "Polygon":
            return self.parsePolygon(d)
        elif t == "MultiPolygon":
            return self.parseMultiPolygon(d)
        elif t == "GeometryCollection":
            return self.parseGeometryCollection(d)
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
        elif isinstance(geom, Point):
            return self._geometry_asdict(geom, "Point")
        elif isinstance(geom, LineString):
            return self._geometry_asdict(geom, "LineString")
        elif isinstance(geom, Polygon):
            return self._geometry_asdict(geom, "Polygon")
        elif isinstance(geom, MultiPoint):
            return self._geometry_asdict(geom, "MultiPoint")
        elif isinstance(geom, MultiLineString):
            return self._geometry_asdict(geom, "MultiLineString")
        elif isinstance(geom, MultiPolygon):
            return self._geometry_asdict(geom, "MultiPolygon")
        elif isinstance(geom, GeometryCollection):
            return self.geometry_collection_asdict(geom)
        elif isinstance(geom, FeatureCollection):
            return self.feature_collection_asdict(geom)
        else:
            raise TypeError("cannot serialize type '{0}'".format(type(geom)))

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

    def _geometry_asdict(self, geom, name):
        if not isinstance(geom.crs, dict):
            crs = self.crsdict(geom.crs)
        else:
            crs = geom.crs
        d = {"type": name,
             "coordinates": geom.coordinates}

        if self.enforce_poly_winding:
            if name == "Polygon":
                cx = d["coordinates"]
                for i, ring in enumerate(cx):
                    if bool(i) is is_counterclockwise(ring):
                        cx[i] = ring[::-1]
            elif name == "MultiPolygon":
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

