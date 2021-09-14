import os

import ujson

from .types import GeometryCollection, Feature, FeatureCollection

from .antimeridian import antimeridian_cut
from .bbox import (geom_bbox, geometry_collection_bbox,
                   feature_bbox, feature_collection_bbox)

from .identity import identity

from .docstrings import docstring_insert

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

    def __call__(self, geom):
        return ujson.dumps(self.geojson_asdict(geom), indent=0)

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
                    d["bbox"] = self.prepare_coords(bb)

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


def fixed_precision(A, prec=6):
    """ Recursively convert nested iterables or coordinates to nested lists at
    fixed precision. """
    if hasattr(A, '__iter__'):
        return [fixed_precision(el, prec=prec) for el in A]
    else:
        return round(A, prec)

