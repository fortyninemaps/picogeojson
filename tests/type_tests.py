import unittest

import picogeojson as pico

class InvalidCoordTests(unittest.TestCase):
    """ Geometries created with nonsensiscal coordinate arrays should raise a
    TypeError.
    """

    def test_bad_point(self):
        with self.assertRaises(TypeError):
            pico.Point(1, 2)

    def test_bad_linestring(self):
        with self.assertRaises(TypeError):
            pico.LineString([1, 2, 3, 4, 5, 6])

        with self.assertRaises(TypeError):
            pico.LineString([[(1, 2), (3, 4), (5, 6)]])

    def test_bad_polygon(self):
        with self.assertRaises(TypeError):
            pico.Polygon([(1, 2), (3, 4), (5, 6)])

    def test_bad_multipoint(self):
        with self.assertRaises(TypeError):
            pico.MultiPoint((1, 2), (3, 4), (5, 6))

    def test_bad_multilinestring(self):
        with self.assertRaises(TypeError):
            pico.MultiLineString([(1, 2), (3, 4), (5, 6)])

    def test_bad_multipolygon(self):
        with self.assertRaises(TypeError):
            pico.MultiPolygon([[(1, 2), (3, 4), (5, 6)]])

class ClosedRingTests(unittest.TestCase):
    """ Polygon geometries created from open rings should automatically close
    themselves. """

    def assertClosed(self, geom):
        if type(geom).__name__ == "Polygon":
            for ring in geom.coordinates:
                if tuple(ring[0]) != tuple(ring[-1]):
                    self.fail()
        elif type(geom).__name__ == "MultiPolygon":
            for poly in geom.coordinates:
                for ring in poly:
                    if tuple(ring[0]) != tuple(ring[-1]):
                        self.fail()

    def test_check_polygon_ring(self):
        polygon = pico.loads("""{"type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [2, 1]]]}""")
        self.assertClosed(polygon)

    def test_check_polygon_interior_ring(self):
        polygon = pico.loads("""{"type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [2, 1], [0, 0]],
                            [[0.5,0.5], [0.6,0.5], [0.6,0.7]]]}""")
        self.assertClosed(polygon)

    def test_check_multipolygon_ring(self):

        geom = pico.loads("""{"type": "MultiPolygon",
            "coordinates": [[[[0, 0], [1, 0], [2, 1]]],
                            [[[-4,-4], [5,-6], [2, 10]]]]}""")
        self.assertClosed(geom)

if __name__ == "__main__":
    unittest.main()
