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
    """ Combine a list of GeoJSON types into the single most specific type that
    retains all information. """
    items = list(items)
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
        geometries = []
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

