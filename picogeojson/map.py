from . import Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon
from .types import true
from .serializer import Serializer

class Map(object):
    """ It's a monad! """

    def __init__(self, raw):
        self.raw = raw
        return

    def _geometry_getter(self, geom_type):
        objs = [self.raw]
        while len(objs) != 0:
            obj = objs.pop()
            if type(obj).__name__ == geom_type.__name__:
                yield obj
            elif type(obj).__name__ == "GeometryCollection":
                for geom in obj.geometries:
                    objs.append(geom)

    def after(self, func, cond=true):
        return Map(self.raw.after(func, cond))

    def map(self, func, typ, **kw):
        return self.after(
                func,
                lambda obj: type(obj).__name__ == typ.__name__,
        )

    def map_features(self, func, geometry_type=None, properties=None):
        return self.after(
                func,
                lambda obj: type(obj).__name__ == "Feature" and \
                        (geometry_type is None or type(obj.geometry) == geometry_type.__name__) and \
                        (properties is None or \
                            type(obj).__name__ == "Feature" and propmatch(obj.properties, properties)),
        )

    def extract(self, typ, **kw):
        return self._geometry_getter(typ, **kw)

    def extract_features(self, geometry_type=None, properties=None):
        """ Returns a generator for Features matching predicates.

        Parameters
        ----------
        geometry_type : str
            Type of Feature "geometry" member
        properties : dict
            Mapping of property to value that return values satisfy
        """
        if geometry_type is not None and not isinstance(geometry_type, type):
            raise TypeError("expected str geometry_type, got {}".format(type(geometry_type)))

        objs = [self.raw]
        while len(objs) != 0:
            obj = objs.pop()
            if type(obj).__name__ == "Feature":
                typematch = (geometry_type is None) or \
                        (type(obj.geometry).__name__ == geometry_type.__name__)
                if typematch and (properties is None or propmatch(obj.properties, properties)):
                    yield(obj)
            elif type(obj).__name__ == "FeatureCollection":
                for feat in obj.features:
                    objs.append(feat)

    @property
    def points(self):
        """ Returns a generator yielding all Point objects in the result. """
        return self._geometry_getter(Point)

    @property
    def linestrings(self):
        """ Returns a generator yielding all LineString objects in the result. """
        return self._geometry_getter(LineString)

    @property
    def polygons(self):
        """ Returns a generator yielding all Polygon objects in the result. """
        return self._geometry_getter(Polygon)

    @property
    def multipoints(self):
        """ Returns a generator yielding all MultiPoint objects in the result. """
        return self._geometry_getter(MultiPoint)

    @property
    def multilinestrings(self):
        """ Returns a generator yielding all MultiLineString objects in the result. """
        return self._geometry_getter(MultiLineString)

    @property
    def multipolygons(self):
        """ Returns a generator yielding all MultiPolygon objects in the result. """
        return self._geometry_getter(MultiPolygon)

def propmatch(testing, required):
    return all(k in testing for k in required) and \
           all(testing[k] == v for k, v in required.items())
