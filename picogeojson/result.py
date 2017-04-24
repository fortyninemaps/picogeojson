from .types import Point, LineString, Polygon

class GeoJSONResult(object):

    def __init__(self, obj):
        self.obj = obj
        return

    def points(self):
        objs = [self.obj]
        while len(objs) != 0:
            obj = objs.pop()
            if type(obj).__name__ == "Point":
                yield obj
            elif type(obj).__name__ == "GeometryCollection":
                for geom in obj.geometries:
                    objs.append(geom)

    def linestrings(self):
        objs = [self.obj]
        while len(objs) != 0:
            obj = objs.pop()
            if type(obj).__name__ == "LineString":
                yield obj
            elif type(obj).__name__ == "GeometryCollection":
                for geom in obj.geometries:
                    objs.append(geom)

    def polygons(self):
        objs = [self.obj]
        while len(objs) != 0:
            obj = objs.pop()
            if type(obj).__name__ == "Polygon":
                yield obj
            elif type(obj).__name__ == "GeometryCollection":
                for geom in obj.geometries:
                    objs.append(geom)


