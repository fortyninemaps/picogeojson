# Implements antimeridian cutting

import itertools

from .types import (LineString, MultiLineString,
                    Polygon, MultiPolygon,
                    GeometryCollection,
                    Feature, FeatureCollection)

def crosses_antimeridian(obj):
    """ Determines whether a geometry or feature crosses the antimeridian be
    searching exhaustively.
    """
    def _seg_crosses(x0, x1):
        return abs(x0-x1) > 180

    if isinstance(obj, LineString):
        for i in range(len(obj.coordinates)-1):
            if _seg_crosses(obj.coordinates[i][0], obj.coordinates[i+1][0]):
                return True
    elif isinstance(obj, MultiLineString):
        for coords in obj.coordinates:
            for i in range(len(coords)-1):
                if _seg_crosses(coords[i][0], coords[i+1][0]):
                    return True
    if isinstance(obj, Polygon):
        coords = obj.coordinates[0]
        for coords in obj.coordinates:
            for i in range(len(coords)-1):
                if _seg_crosses(coords[i][0], coords[i+1][0]):
                    return True
    elif isinstance(obj, MultiPolygon):
        for coords in obj.coordinates:
            for i in range(len(coords[0])-1):
                if _seg_crosses(coords[0][i][0], coords[0][i+1][0]):
                    return True
    elif isinstance(obj, GeometryCollection):
        for geom in obj.geometries:
            if crosses_antimeridian(geom):
                return True
    elif isinstance(obj, Feature):
        return crosses_antimeridian(obj.geometry)
    elif isinstance(obj, FeatureCollection):
        for feature in obj.features:
            if crosses_antimeridian(feature.geometry):
                return True
    return False

def antimeridian_cut(obj):
    """ Given a multiple vertex GeoJSON object, *cut_antimeridian* splits the
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

    def _seg_crosses(x0, x1):
        return abs(x0-x1) > 180

    def _split(pt0, pt1):
        # compute offset from antimeridian
        dx0 = abs((pt0[0] + 360) % 360 - 180)
        dx1 = abs((pt1[0] + 360) % 360 - 180)
        return (180, round((dx0*pt0[1] + dx1*pt1[1])/(dx0+dx1), 8))

    def _split_coordinates(coordinates):
        parts = []
        coords = [obj.coordinates[0]]
        for i in range(len(obj.coordinates)-1):
            pt0 = obj.coordinates[i]
            pt1 = obj.coordinates[i+1]
            if _seg_crosses(pt0[0], pt1[0]):
                px = _split(pt0, pt1)
                coords.append(px)
                parts.append(coords)
                coords = [(-179.99999999, px[1]), pt1]
            else:
                coords.append(pt1)
        parts.append(coords)
        return parts

    if crosses_antimeridian(obj):
        if isinstance(obj, LineString):
            parts = _split_coordinates(obj.coordinates)
            return MultiLineString(parts, obj.crs)
        elif isinstance(obj, Polygon):

            return MultiPolygon(parts, obj.crs)
        elif isinstance(obj, MultiLineString):

            return MultiLineString(parts, obj.crs)
        elif isinstance(obj, MultiPolygon):

            return MultiPolygon(parts, obj.crs)
        elif isinstance(obj, GeometryCollection):
            parts = list(itertools.chain(*[cut_antimeridian(geom)
                                           for geom in obj.geometries]))
            return GeometryCollection(parts, obj.crs)
        elif isinstance(obj, Feature):
            return Feature(cut_antimeridian(obj.geometry), obj.properties,
                           obj.id, obj.crs)
        elif isinstance(obj, FeatureCollection):
            return FeatureCollection([cut_antimeridian(f) for f in obj.features],
                                     obj.crs)
    else:
        return obj
