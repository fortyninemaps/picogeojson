from .types import Feature

class GeoJSONResult(object):

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

    def _feature_getter(self, geom_type):
        objs = [self.obj]
        while len(objs) != 0:
            obj = objs.pop()
            if (type(obj).__name__ == "Feature" and
                    type(obj.geometry).__name__ == geom_type):
                yield obj
            elif type(obj).__name__ == "FeatureCollection":
                for feat in obj.features:
                    objs.append(feat)

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

    @property
    def point_features(self):
        """ Returns a generator yielding all Feature objects with a Point
        geometry in the result. """
        return self._feature_getter("Point")

    @property
    def linestring_features(self):
        """ Returns a generator yielding all Feature objects with a LineString
        geometry in the result. """
        return self._feature_getter("LineString")

    @property
    def polygon_features(self):
        """ Returns a generator yielding all Feature objects with a Polygon
        geometry in the result. """
        return self._feature_getter("Polygon")

    @property
    def multipoint_features(self):
        """ Returns a generator yielding all Feature objects with a MultiPoint
        geometry in the result. """
        return self._feature_getter("MultiPoint")

    @property
    def multilinestring_features(self):
        """ Returns a generator yielding all Feature objects with a
        MultiLineString geometry in the result. """
        return self._feature_getter("MultiLineString")

    @property
    def multipolygon_features(self):
        """ Returns a generator yielding all Feature objects with a MultiPolygon
        geometry in the result. """
        return self._feature_getter("MultiPolygon")

    @property
    def geometrycollection_features(self):
        """ Returns a generator yielding all Feature objects with a
        GeometryCollection geometry in the result. """
        return self._feature_getter("GeometryCollection")

