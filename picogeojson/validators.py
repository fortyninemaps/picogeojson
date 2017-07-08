from numbers import Number

# Point
def depth1(cls, attr, val):
    if not hasattr(val, "__getitem__") or not isinstance(val[0], Number):
        raise TypeError("received {} but require position iterable".format(val))

# LineString
def depth2(cls, attr, val):
    depth1(cls, attr, val[0])
    if not hasattr(val[0], "__getitem__"):
        raise TypeError("received {} but require list of positions".format(val))

# Polygon, MultiLineString
def depth3(cls, attr, val):
    depth2(cls, attr, val[0])
    if not hasattr(val[0][0], "__getitem__"):
        raise TypeError("received {} but require list of position lists".format(val))

# MultiPolygon
def depth4(cls, attr, val):
    depth3(cls, attr, val[0])
    if not hasattr(val[0][0][0], "__getitem__"):
        raise TypeError("received {} but require list of position ring lists".format(val))


