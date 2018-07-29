import attr
from collections import Iterable

from . import validators
from .orientation import is_counterclockwise
from .identity import identity

def as_nested_lists(obj):
    """ Convert all but the lowest level of iterables to lists. """
    if not isinstance(obj, Iterable) or not isinstance(obj[0], Iterable):
        return obj
    else:
        return [as_nested_lists(a) for a in obj]

def close_rings_inplace(obj):
    """ Ensure rings in a list of lists are closed. """
    if isinstance(obj, Iterable) and isinstance(obj[0], Iterable):
        if isinstance(obj[0][0], Iterable):
            # obj contains rings
            for part in obj:
                close_rings_inplace(part)
        else:
            # obj is a ring
            if obj[0] != obj[-1]:
                obj.append(obj[0])
    return obj

def as_closed_lists(obj):
    return close_rings_inplace(as_nested_lists(obj))

def polygon_converter(obj):
    """ Ensure that rings are closed and correctly oriented. """
    obj = close_rings_inplace(as_nested_lists(obj))
    for i, ring in enumerate(obj):
        if bool(i) is is_counterclockwise(ring):
            obj[i] = ring[::-1]
    return obj

def multipolygon_converter(obj):
    """ Ensure that rings closed and correctly oriented. """
    obj = close_rings_inplace(as_nested_lists(obj))
    for j, cx in enumerate(obj):
        for i, ring in enumerate(cx):
            if bool(i) is is_counterclockwise(ring):
                obj[j][i] = ring[::-1]
    return obj

def true(a):
    return True

class After(object):
    def after(self, func, cond=true):
        return func(self) if cond(self) else self

@attr.s(cmp=True, slots=True)
class Point(After):
    coordinates = attr.ib(validator=validators.depth1)
    crs = attr.ib(default=None)

    def transform(self, func):
        return Point(func(self.coordinates), self.crs)

@attr.s(cmp=True, slots=True)
class MultiPoint(After):
    coordinates = attr.ib(repr=False, convert=as_nested_lists, validator=validators.depth2)
    crs = attr.ib(default=None, repr=False)

    def transform(self, func):
        return MultiPoint(list(map(func, self.coordinates)), self.crs)

@attr.s(cmp=True, slots=True)
class LineString(After):
    coordinates = attr.ib(repr=False, convert=as_nested_lists, validator=validators.depth2)
    crs = attr.ib(default=None, repr=False)

    def transform(self, func):
        return LineString(list(map(func, self.coordinates)), self.crs)

@attr.s(cmp=True, slots=True)
class MultiLineString(After):
    coordinates = attr.ib(repr=False, convert=as_nested_lists, validator=validators.depth3)
    crs = attr.ib(default=None, repr=False)

    def transform(self, func):
        return MultiLineString([list(map(func, cx)) for cx in self.coordinates],
                               self.crs)

@attr.s(cmp=True, slots=True)
class Polygon(After):
    coordinates = attr.ib(repr=False, convert=polygon_converter, validator=validators.depth3)
    crs = attr.ib(default=None, repr=False)

    def transform(self, func):
        return Polygon([list(map(func, cx)) for cx in self.coordinates], self.crs)

@attr.s(cmp=True, slots=True)
class MultiPolygon(After):
    coordinates = attr.ib(repr=False, convert=multipolygon_converter, validator=validators.depth4)
    crs = attr.ib(default=None, repr=False)

    def transform(self, func):
        return MultiPolygon([[list(map(func, cx)) for cx in poly] for poly in self.coordinates],
                            self.crs)

@attr.s(cmp=True, slots=True)
class GeometryCollection(After):
    geometries = attr.ib(type=list, validator=validators.only_geometries)
    crs = attr.ib(default=None, repr=False)

    def __add__(self, other):
        return GeometryCollection(self.geometries + other.geometries, self.crs)

    def after(self, func, cond=true):
        geom = GeometryCollection([g.after(func, cond=cond) for g in self.geometries],
                                  crs=self.crs)
        return func(geom) if cond(self) else geom

    def transform(self, func):
        return GeometryCollection([g.transform(func) for g in self.geometries],
                                  crs=self.crs)

    def map(self, func):
        """ Apply a callable *func* that takes a Geometry and returns a
        Geometry.
        """
        return GeometryCollection(list(map(func, self.geometries)), crs=self.crs)

    def flatmap(self, func):
        """ Combine the results from a callable *func* that takes a Geometry and
        returns a GeometryCollection.
        """
        geometries = [geometry for geom in self.geometries
                               for geometry in func(geom).geometries]
        return GeometryCollection(geometries, crs=self.crs)

@attr.s(cmp=True, slots=True)
class Feature(After):
    geometry = attr.ib(validator=validators.is_geometry)
    properties = attr.ib()
    id = attr.ib(default=None, repr=False)
    crs = attr.ib(default=None, repr=False)

    def after(self, func, cond=true):
        f = Feature(self.geometry.after(func, cond=cond), self.properties,
                    id=self.id, crs=self.crs)
        return func(f) if cond(self) else f

    def transform(self, func):
        return Feature(self.geometry.transform(func), self.properties, self.id,
                       self.crs)

    def map_geometry(self, func):
        """ Apply a callable *func* that takes a Geometry and returns a
        Geometry.
        """
        return Feature(func(self.geometry), self.properties, self.id, self.crs)

    def map_properties(self, func):
        """ Apply a callable *func* that takes a properties dictionary and
        returns a new dictionary.
        """
        return Feature(self.geometry, func(self.properties), self.id, self.crs)

@attr.s(cmp=True, slots=True)
class FeatureCollection(After):
    features = attr.ib(type=list, validator=validators.only_features)
    crs = attr.ib(default=None, repr=False)

    def __add__(self, other):
        return FeatureCollection(self.features + other.features, self.crs)

    def after(self, func, cond=true):
        fc = FeatureCollection([f.after(func, cond=cond) for f in self.features],
                               crs=self.crs)
        return func(fc) if cond(self) else fc

    def transform(self, func):
        return FeatureCollection([f.transform(func) for f in self.features],
                                  crs=self.crs)

    def map(self, func):
        """ Apply a callable *func* that takes a Feature and returns a Feature.
        """
        return FeatureCollection(list(map(func, self.features)))

    def flatmap(self, func):
        """ Combine the results from a function *func* that takes a Feature and
        returns a FeatureCollection.
        """
        features = [feature for feat in self.features
                            for feature in func(feat).features]
        return FeatureCollection(features)
