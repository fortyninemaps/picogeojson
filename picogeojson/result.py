
class Result(object):

    def __init__(self, obj):
        self.obj = obj
        return

    def _geometry_getter(self, geom_type):
        objs = [self.obj]
        while len(objs) != 0:
            obj = objs.pop()
            if type(obj).__name__ == geom_type:
                yield obj
            elif type(obj).__name__ == "GeometryCollection":
                for geom in obj.geometries:
                    objs.append(geom)

    @property
    def points(self):
        """ Returns a generator yielding all Point objects in the result. """
        return self._geometry_getter("Point")

    @property
    def linestrings(self):
        """ Returns a generator yielding all LineString objects in the result. """
        return self._geometry_getter("LineString")

    @property
    def polygons(self):
        """ Returns a generator yielding all Polygon objects in the result. """
        return self._geometry_getter("Polygon")

    @property
    def multipoints(self):
        """ Returns a generator yielding all MultiPoint objects in the result. """
        return self._geometry_getter("MultiPoint")

    @property
    def multilinestrings(self):
        """ Returns a generator yielding all MultiLineString objects in the result. """
        return self._geometry_getter("MultiLineString")

    @property
    def multipolygons(self):
        """ Returns a generator yielding all MultiPolygon objects in the result. """
        return self._geometry_getter("MultiPolygon")

    def features(self, geometry_type=None, properties=None):
        """ Returns a generator for Features matching predicates.

        Parameters
        ----------
        geometry_type : str
            Type of Feature "geometry" member
        properties : dict
            Mapping of property to value that return values satisfy
        """
        if geometry_type is not None and not isinstance(geometry_type, str):
            raise TypeError("expected str geometry_type, got {}".format(type(geometry_type)))

        objs = [self.obj]
        while len(objs) != 0:
            obj = objs.pop()
            if type(obj).__name__ == "Feature":
                typematch = (geometry_type is None) or \
                        (type(obj.geometry).__name__ == geometry_type)
                propmatch = (properties is None) or \
                        (all(k in obj.properties for k in properties) and
                         all(obj.properties[k] == v for k, v in properties.items()))
                if typematch and propmatch:
                    yield(obj)
            elif type(obj).__name__ == "FeatureCollection":
                for feat in obj.features:
                    objs.append(feat)

GeoJSONResult = Result
