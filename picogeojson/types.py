import attr

@attr.s(cmp=False, slots=True)
class Point(object):
    coordinates = attr.ib()
    crs = attr.ib(default=None)

@attr.s(cmp=False, slots=True)
class MultiPoint(object):
    coordinates = attr.ib()
    crs = attr.ib(default=None)

@attr.s(cmp=False, slots=True)
class LineString(object):
    coordinates = attr.ib()
    crs = attr.ib(default=None)

@attr.s(cmp=False, slots=True)
class MultiLineString(object):
    coordinates = attr.ib()
    crs = attr.ib(default=None)

@attr.s(cmp=False, slots=True)
class Polygon(object):
    coordinates = attr.ib()
    crs = attr.ib(default=None)

@attr.s(cmp=False, slots=True)
class MultiPolygon(object):
    coordinates = attr.ib()
    crs = attr.ib(default=None)

@attr.s(cmp=False, slots=True)
class GeometryCollection(object):
    geometries = attr.ib()
    crs = attr.ib(default=None)

@attr.s(cmp=False, slots=True)
class Feature(object):
    geometry = attr.ib()
    properties = attr.ib()
    id = attr.ib(default=None)
    crs = attr.ib(default=None)

@attr.s(cmp=False, slots=True)
class FeatureCollection(object):
    features = attr.ib()
    crs = attr.ib(default=None)

