from collections import namedtuple

Point = namedtuple('Point', ['coordinates', 'crs'])
Point.__new__.__defaults__ = (None,)

MultiPoint = namedtuple('MultiPoint', ['coordinates', 'crs'])
MultiPoint.__new__.__defaults__ = (None,)

LineString = namedtuple('LineString', ['coordinates', 'crs'])
LineString.__new__.__defaults__ = (None,)

MultiLineString = namedtuple('MultiLineString', ['coordinates', 'crs'])
MultiLineString.__new__.__defaults__ = (None,)

Polygon = namedtuple('Polygon', ['coordinates', 'crs'])
Polygon.__new__.__defaults__ = (None,)

MultiPolygon = namedtuple('MultiPolygon', ['coordinates', 'crs'])
MultiPolygon.__new__.__defaults__ = (None,)

GeometryCollection = namedtuple('GeometryCollection', ['geometries', 'crs'])
GeometryCollection.__new__.__defaults__ = (None,)

Feature = namedtuple('Feature', ['geometry', 'properties', 'id', 'crs'])
Feature.__new__.__defaults__ = (None, None)

FeatureCollection = namedtuple('FeatureCollection', ['features', 'crs'])
FeatureCollection.__new__.__defaults__ = (None,)


