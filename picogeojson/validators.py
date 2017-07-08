# Point
def depth1(cls, attribute, value):
    if not hasattr(value, "__getitem__") or hasattr(value[0], "__getitem__"):
        raise TypeError("require 1-dimensional coordinate list")

# LineString
def depth2(cls, attribute, value):
    if not (depth1 and hasattr(value[0], "__getitem__")):
        raise TypeError("require 2-dimensional coordinate list")

# Polygon, MultiLineString
def depth3(cls, attribute, value):
    if not (depth2 and hasattr(value[0][0], "__getitem__")):
        raise TypeError("require 3-dimensional coordinate list")

# MultiPolygon
def depth4(cls, attribute, value):
    if not (depth3 and hasattr(value[0][0][0], "__getitem__")):
        raise TypeError("require 4-dimensional coordinate list")


