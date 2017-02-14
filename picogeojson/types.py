import itertools
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

def merge(items):
    t0 = type(items[0]).__name__
    if all(type(g).__name__ == t0 for g in items[1:]):
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
            features = list(itertools.chain([f.features for f in items]))
            return FeatureCollection(features, crs=items[0].crs)
        else:
            raise TypeError()
    elif "Feature" not in (type(g).__name__ for g in items) and \
         "FeatureCollection" not in (type(g).__name__ for g in items):
        return GeometryCollection(items, crs=items[0].crs)
    elif all(type(g).__name__ in ("Feature", "FeatureCollection") for g in items):
        features = []
        for item in items:
            if type(item).__name__ == "Feature":
                features.append(item)
            else:
                features.extend(item.features)
        return FeatureCollection(features, crs=items[0].crs)
    else:
        raise TypeError("no rule to merge {}".format(set(type(g).__name__ for g in items)))

