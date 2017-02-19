# Implements antimeridian cutting
import itertools
from .types import (LineString, MultiLineString,
                    Polygon, MultiPolygon,
                    GeometryCollection,
                    Feature, FeatureCollection)

PRECISION = 1e-8

def _seg_crosses(x0, x1):
    return abs(x0-x1) > 180

def _split(pt0, pt1):
    # compute offset from antimeridian
    dx0 = float(abs((pt0[0] + 360) % 360 - 180))
    dx1 = float(abs((pt1[0] + 360) % 360 - 180))
    return round((dx0*pt0[1] + dx1*pt1[1])/(dx0+dx1), 8)

def _split_coordinate_string(coordinates):
    parts = []
    coords = [coordinates[0]]
    for i in range(len(coordinates)-1):
        pt0 = coordinates[i]
        pt1 = coordinates[i+1]
        if _seg_crosses(pt0[0], pt1[0]):
            ymerid = _split(pt0, pt1)
            if pt0[0]>0:
                # moving east
                coords.append((180, ymerid))
            else:
                coords.append((-180+PRECISION, ymerid))
            parts.append(coords)
            if pt0[0]>0:
                # moving east
                coords = [(-180+PRECISION, ymerid), pt1]
            else:
                coords = [(180, ymerid), pt1]
        else:
            coords.append(pt1)
    parts.append(coords)
    return parts

def _close_ring(coordinates):
    if coordinates[0] != coordinates[-1]:
        coordinates.append(coordinates[0])
    return coordinates

def _split_ring(ring):
    parts = _split_coordinate_string(ring)
    if len(parts) != 1 and parts[0][0] != 180:
        p = parts.pop()
        parts[0].extend(p)
    return [_close_ring(p) for p in parts]

def contains(poly0, poly1):
    """ Does poly0 contain poly1?
    As an initial implementation, returns True if any vertex of poly1 is within
    poly0.
    """
    # check for bounding box overlap
    bb0 = (min(p[0] for p in poly0), min(p[1] for p in poly0),
           max(p[0] for p in poly0), max(p[1] for p in poly0))
    bb1 = (min(p[0] for p in poly1), min(p[1] for p in poly1),
           max(p[0] for p in poly1), max(p[1] for p in poly1))
    if ((bb0[0] > bb1[2])
            or (bb0[2] < bb1[0])
            or (bb0[1] > bb1[3])
            or (bb0[3] < bb1[1])):
        return False

    # check each vertex
    def _isleft(p, p0, p1):
        return ((p1[0]-p0[0])*(p[1]-p0[1]) - (p[0]-p0[0])*(p1[1]-p0[1])) > 0

    for p in poly1:
        wn = 0
        for i in range(len(poly0)-1):
            p0 = poly0[i]
            p1 = poly0[i+1]
            if p0[1] <= p[1] < p1[1]:       # upward crossing
                if _isleft(p, p0, p1):
                    wn += 1
            elif p0[1] >= p[1] > p1[1]:
                if not _isleft(p, p0, p1):
                    wn -= 1
        if wn != 0:
            return True
    return False

def _crosses_antimeridian(coordinates):
    """ Determines whether a geometry or feature crosses the antimeridian by
    searching exhaustively.
    """
    for c0, c1 in zip(coordinates[:-1], coordinates[1:]):
        if _seg_crosses(c0[0], c1[0]):
            return True
    return False

def antimeridian_cut(obj):
    """ Given a multiple vertex GeoJSON object, *antimeridian_cut* splits the
    object wherever it crosses the antimeridian. If a split occurs, the return
    type is according to:

        given a             returns a
        ------------------  ------------------
        LineString          MultiLineString
        Polygon             MultiPolygon
        MultiLineString     MultiLineString
        MultiPolygon        MultiPolygon
        GeometryCollection  GeometryCollection
        Feature             Feature
        FeatureCollection   FeatureCollection

    If no split is required, the original argument is returned.
    """
    if isinstance(obj, LineString):
        if _crosses_antimeridian(obj.coordinates):
            parts = _split_coordinate_string(obj.coordinates)
            return MultiLineString(parts, obj.crs)
        else:
            return obj
    elif isinstance(obj, Polygon):
        if _crosses_antimeridian(obj.coordinates[0]):
            outer_rings = _split_ring(obj.coordinates[0])
            if len(obj.coordinates) != 1:
                inner_rings = list(itertools.chain(*[_split_ring(hole)
                                    for hole in obj.coordinates[1:]]))
            else:
                inner_rings = []
            parts = []
            for ring in outer_rings:
                part = [ring]
                for hole in inner_rings:
                    if contains(ring, hole):
                        part.append(hole)
                parts.append(part)
            return MultiPolygon(parts, obj.crs)
        else:
            return obj
    elif isinstance(obj, MultiLineString):
        parts = []
        for ls in obj.coordinates:
            if _crosses_antimeridian(ls):
                parts.extend(_split_coordinate_string(ls))
            else:
                parts.append(ls)
        return MultiLineString(parts, obj.crs)
    elif isinstance(obj, MultiPolygon):
        parts = [antimeridian_cut(Polygon(c)) for c in obj.coordinates]
        return MultiPolygon([p.coordinates for p in parts], obj.crs)
    elif isinstance(obj, GeometryCollection):
        parts = [antimeridian_cut(geom) for geom in obj.geometries]
        return GeometryCollection(parts, obj.crs)
    elif isinstance(obj, Feature):
        return Feature(antimeridian_cut(obj.geometry), obj.properties,
                       obj.id, obj.crs)
    elif isinstance(obj, FeatureCollection):
        return FeatureCollection([antimeridian_cut(f) for f in obj.features],
                                 obj.crs)
