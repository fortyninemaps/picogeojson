# ensures that Polygon rings are counter-clockwise

def _isleft(p, p0, p1):
    return ((p1[0]-p0[0])*(p[1]-p0[1]) - (p[0]-p0[0])*(p1[1]-p0[1])) > 0

def is_counterclockwise(ring):
    incomplete_ring = ring[:-1]
    xmin = incomplete_ring[-1][0]
    ymin = incomplete_ring[-1][1]
    imin = -1
    for i, pt in enumerate(incomplete_ring[:-1]):
        if pt[1] < ymin or (pt[1] == ymin and pt[0] < xmin):
            imin = i
            ymin = pt[1]
            xmin = pt[0]

    return _isleft(incomplete_ring[imin-1], incomplete_ring[imin], incomplete_ring[imin+1])

