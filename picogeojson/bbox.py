# -*- coding: utf-8 -*-

def geom_bbox(geom):
    if type(geom).__name__ == "Point":
        ndim = len(geom.coordinates)
        bbx = [geom.coordinates[i%ndim] for i in range(2*ndim)]
    elif type(geom).__name__ == "LineString":
        bbx = coordstring_bbox(geom.coordinates)
    elif type(geom).__name__ == "Polygon":
        bbx = coordstring_bbox(geom.coordinates[0])
    elif type(geom).__name__ == "MultiPoint":
        bbx = coordstring_bbox(geom.coordinates)
    elif type(geom).__name__ == "MultiLineString":
        bbxs = [coordstring_bbox(ls) for ls in geom.coordinates]
        bbx = [min(bb[0] for bb in bbxs), min(bb[1] for bb in bbxs),
               max(bb[2] for bb in bbxs), max(bb[3] for bb in bbxs)]
    elif type(geom).__name__ == "MultiPolygon":
        bbxs = [coordstring_bbox(poly[0]) for poly in geom.coordinates]
        bbx = [min(bb[0] for bb in bbxs), min(bb[1] for bb in bbxs),
               max(bb[2] for bb in bbxs), max(bb[3] for bb in bbxs)]
    elif type(geom).__name__ == "GeometryCollection":
        bbx = geometry_collection_bbox(geom)
    else:
        raise TypeError("type '{}' is not a geometry with a bbox".format(type(geom).__name__))
    return bbx

def feature_bbox(feature):
    return geom_bbox(feature.geometry)

def geometry_collection_bbox(coll):
    bbxs = [geom_bbox(g) for g in coll.geometries]
    ndim = len(bbxs[0])//2
    bbx = [0 for _ in range(2*ndim)]
    for dim in range(ndim):
        bbx[dim] = min(bb[dim] for bb in bbxs)
        bbx[dim+ndim] = max(bb[dim+ndim] for bb in bbxs)
    return bbx

def feature_collection_bbox(coll):
    bbxs = [feature_bbox(feature) for feature in coll.features]
    ndim = len(bbxs[0])//2
    bbx = [0 for _ in range(2*ndim)]
    for dim in range(ndim):
        bbx[dim] = min(bb[dim] for bb in bbxs)
        bbx[dim+ndim] = max(bb[dim+ndim] for bb in bbxs)
    return bbx

def coordstring_bbox(coordinates):
    """ Given a string of coodinates, return the bounds as a *2×N* length list,
    where *N* is the number of dimensions (at least two).

    The bounding list is structured `xmin, ymin[, ...], xmax, ymax[, ...]`.
    """
    ndim = len(coordinates[0])
    bbx = [0 for _ in range(2*ndim)]
    components = [[a[i] for a in coordinates] for i in range(ndim)]
    for i, comp in enumerate(components):
        bbx[i] = min(comp)
        bbx[i+ndim] = max(comp)
    return bbx

