import itertools
import attr
from collections import Iterable

from .orientation import is_counterclockwise
from .validators import depth1, depth2, depth3, depth4

def as_nested_lists(obj):
    """ Convert all but the lowest level of iterables to lists """
    if not isinstance(obj, Iterable) or not isinstance(obj[0], Iterable):
        return obj
    else:
        return [as_nested_lists(a) for a in obj]

def close_rings_inplace(obj):
    """ Identify rings in a list of lists and ensure that they're closed. """
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
    obj = close_rings_inplace(as_nested_lists(obj))
    for i, ring in enumerate(obj):
        if bool(i) is is_counterclockwise(ring):
            obj[i] = ring[::-1]
    return obj

def multipolygon_converter(obj):
    obj = close_rings_inplace(as_nested_lists(obj))
    for j, cx in enumerate(obj):
        for i, ring in enumerate(cx):
            if bool(i) is is_counterclockwise(ring):
                obj[j][i] = ring[::-1]
    return obj

@attr.s(cmp=True, slots=True)
class Point(object):
    coordinates = attr.ib(validator=depth1)
    crs = attr.ib(default=None)

    def transform(self, func):
        return Point(func(self.coordinates), self.crs)

@attr.s(cmp=True, slots=True)
class MultiPoint(object):
    coordinates = attr.ib(repr=False, convert=as_nested_lists, validator=depth2)
    crs = attr.ib(default=None, repr=False)

    def transform(self, func):
        return MultiPoint(list(map(func, self.coordinates)), self.crs)

@attr.s(cmp=True, slots=True)
class LineString(object):
    coordinates = attr.ib(repr=False, convert=as_nested_lists, validator=depth2)
    crs = attr.ib(default=None, repr=False)

    def transform(self, func):
        return LineString(list(map(func, self.coordinates)), self.crs)

@attr.s(cmp=True, slots=True)
class MultiLineString(object):
    coordinates = attr.ib(repr=False, convert=as_nested_lists, validator=depth3)
    crs = attr.ib(default=None, repr=False)

    def transform(self, func):
        return MultiLineString([list(map(func, cx)) for cx in self.coordinates],
                               self.crs)

@attr.s(cmp=True, slots=True)
class Polygon(object):
    coordinates = attr.ib(repr=False, convert=polygon_converter, validator=depth3)
    crs = attr.ib(default=None, repr=False)

    def transform(self, func):
        return Polygon([list(map(func, cx)) for cx in self.coordinates], self.crs)

@attr.s(cmp=True, slots=True)
class MultiPolygon(object):
    coordinates = attr.ib(repr=False, convert=multipolygon_converter, validator=depth4)
    crs = attr.ib(default=None, repr=False)

    def transform(self, func):
        return MultiPolygon([[list(map(func, cx)) for cx in poly] for poly in self.coordinates],
                            self.crs)

@attr.s(cmp=True, slots=True)
class GeometryCollection(object):
    geometries = attr.ib(type=list)
    crs = attr.ib(default=None, repr=False)

    def __add__(self, other):
        return GeometryCollection(self.geometries + other.geometries, self.crs)

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
class Feature(object):
    geometry = attr.ib()
    properties = attr.ib()
    id = attr.ib(default=None, repr=False)
    crs = attr.ib(default=None, repr=False)

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
class FeatureCollection(object):
    features = attr.ib(type=list)
    crs = attr.ib(default=None, repr=False)

    def __add__(self, other):
        return FeatureCollection(self.features + other.features, self.crs)

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

def merge(items):
    """ Combine a list of GeoJSON objects into the single most specific type
    that retains all information.

    For example,

    - merging two Point objects creates a MultiPoint
    - merging a Point and a LineString creates a GeometryCollection
    - merging a multiple Features creates a FeatureCollection

    Raises

    - ValueError when the list contains nothing
    - TypeError when merging a Geometry and a Feature/FeatureCollection
    """
    items = list(items)

    if len(items) == 0:
        raise ValueError("zero-length iterable cannot be merged")
    elif len(items) == 1:
        return items[0]

    t0 = type(items[0]).__name__
    if all(type(g).__name__ == t0 for g in items[1:]):
        if items[0].crs is None and any(it.crs is not None for it in items[1:]):
            raise ValueError("all inputs must share the same CRS")
        elif any(items[0].crs != it.crs for it in items[1:]):
            raise ValueError("all inputs must share the same CRS")

        if t0 == "Point":
            return MultiPoint([g.coordinates for g in items], crs=items[0].crs)
        elif t0 == "LineString":
            return MultiLineString([g.coordinates for g in items], crs=items[0].crs)
        elif t0 == "Polygon":
            return MultiPolygon([g.coordinates for g in items], crs=items[0].crs)
        elif t0 == "GeometryCollection":
            return GeometryCollection(items, crs=items[0].crs)
        elif t0 == "Feature":
            return FeatureCollection(items, crs=items[0].crs)
        elif t0 == "FeatureCollection":
            features = itertools.chain.from_iterable([f.features for f in items])
            return FeatureCollection(list(features), crs=items[0].crs)
        else:
            raise TypeError("unhandled type '{}'".format(type(items[0]).__name__))
    elif "Feature" not in (type(g).__name__ for g in items) and \
         "FeatureCollection" not in (type(g).__name__ for g in items):
        return GeometryCollection(items)
    elif all(type(g).__name__ in ("Feature", "FeatureCollection") for g in items):
        features = []
        for item in items:
            if type(item).__name__ == "Feature":
                features.append(item)
            else:
                features.extend(item.features)
        return FeatureCollection(features)
    else:
        raise TypeError("no rule to merge {}".format(set(type(g).__name__ for g in items)))

def burst(item):
    """ Generator that breaks a composite GeoJSON type into atomic Points,
    LineStrings, Polygons, or Features. """
    if type(item).__name__ == "GeometryCollection":
        for geometry in item.geometries:
            for subgeometry in burst(geometry):
                subgeometry.crs = item.crs
                yield subgeometry

    elif type(item).__name__ == "FeatureCollection":
        for feature in item.features:
            if item.crs is not None:
                feature.crs = item.crs
            yield feature

    elif type(item).__name__ == "MultiPoint":
        for coords in item.coordinates:
            pt = Point(coords, crs=item.crs)
            yield pt

    elif type(item).__name__ == "MultiLineString":
        for coords in item.coordinates:
            geom = LineString(coords, crs=item.crs)
            yield geom

    elif type(item).__name__ == "MultiPolygon":
        for coords in item.coordinates:
            geom = Polygon(coords, crs=item.crs)
            yield geom

    else:
        yield item

