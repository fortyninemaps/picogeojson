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

class FuncTests(unittest.TestCase):

    def test_point_transform(self):
        def shift1(cx):
            return (cx[0]+1, cx[1]+1)
        pt = pico.Point((1, 2)).transform(shift1)
        self.assertEqual(pt.coordinates, (2, 3))

    def test_linestring_transform(self):
        def shift1(cx):
            return (cx[0]+1, cx[1]+1)
        ls = pico.LineString([(1, 2), (-3, 5)]).transform(shift1)
        self.assertEqual(ls.coordinates, [(2, 3), (-2, 6)])

    def test_multipolygon_transform(self):
        def shift1(cx):
            return (cx[0]+1, cx[1]+1)
        ls = pico.MultiPolygon(
                [
                    [[(1, 2), (-3, 5), (0, 0), (1, 2)]],
                    [[(-1, -2), (3, -5), (0, 0), (-1, -2)]],
                ]
        ).transform(shift1)
        self.assertEqual(ls.coordinates,
                [
                    [[(2, 3), (-2, 6), (1, 1), (2, 3)]],
                    [[(0, -1), (4, -4), (1, 1), (0, -1)]],
                ])

    def test_feature_collection_add(self):
        fc0 = pico.FeatureCollection([pico.Point([1,2]), pico.LineString([(0, 1), (1, 3), (2, 2)])])
        fc1 = pico.FeatureCollection([])
        fc2 = pico.FeatureCollection([pico.Polygon([[(0, 0), (0, 2), (1, 1), (0, 0)]]),
                                      pico.Point([1,2])])

        aggregate = fc0 + fc1 + fc2
        self.assertEqual(aggregate.features,
                         [pico.Point([1,2]),
                          pico.LineString([(0, 1), (1, 3), (2, 2)]),
                          pico.Polygon([[(0, 0), (0, 2), (1, 1), (0, 0)]]),
                          pico.Point([1,2])])

    def test_geometrycollection_map(self):
        gc = pico.GeometryCollection([
            pico.Polygon([[(0, 0), (1, 1), (0, 2), (0, 0)]]),
            pico.Polygon([[(0, 0), (2, 2), (0, 4), (0, 0)]]),
            pico.Polygon([[(0, 0), (-1, -1), (0, -2), (0, 0)]])
        ])

        def to_linestring(geometry):
            return pico.LineString(geometry.coordinates[0])

        expected = pico.GeometryCollection([
            pico.LineString([(0, 0), (1, 1), (0, 2), (0, 0)]),
            pico.LineString([(0, 0), (2, 2), (0, 4), (0, 0)]),
            pico.LineString([(0, 0), (-1, -1), (0, -2), (0, 0)])
        ])

        self.assertEqual(gc.map(to_linestring), expected)

    def test_geometrycollection_flatmap(self):
        gc = pico.GeometryCollection([
            pico.MultiPoint([(0, 0), (1, 1), (0, 2), (0, 0)]),
            pico.MultiPoint([(0, 0), (2, 2), (0, 4), (0, 0)])
        ])

        def to_points(geometry):
            return pico.GeometryCollection(
                [pico.Point(xy) for xy in geometry.coordinates]
            )

        expected = pico.GeometryCollection([
            pico.Point((0, 0)), pico.Point((1, 1)), pico.Point((0, 2)), pico.Point((0, 0)),
            pico.Point((0, 0)), pico.Point((2, 2)), pico.Point((0, 4)), pico.Point((0, 0))
        ])

        self.assertEqual(gc.flatmap(to_points), expected)

    def test_featurecollection_map(self):
        fc = pico.FeatureCollection([
            pico.Feature(pico.Polygon([[(0, 0), (1, 1), (0, 2), (0, 0)]]), {}),
            pico.Feature(pico.Polygon([[(0, 0), (2, 2), (0, 4), (0, 0)]]), {}),
            pico.Feature(pico.Polygon([[(0, 0), (-1, -1), (0, -2), (0, 0)]]), {})
        ])

        def to_linestring(feature):
            return pico.Feature(pico.LineString(feature.geometry.coordinates[0]), {"converted": True})

        expected = pico.FeatureCollection([
            pico.Feature(pico.LineString([(0, 0), (1, 1), (0, 2), (0, 0)]), {"converted": True}),
            pico.Feature(pico.LineString([(0, 0), (2, 2), (0, 4), (0, 0)]), {"converted": True}),
            pico.Feature(pico.LineString([(0, 0), (-1, -1), (0, -2), (0, 0)]), {"converted": True})
        ])

        self.assertEqual(fc.map(to_linestring), expected)

    def test_featurecollection_flatmap(self):
        gc = pico.FeatureCollection([
            pico.Feature(pico.MultiPoint([(0, 0), (1, 1), (0, 2), (0, 0)]), {"group": 1}),
            pico.Feature(pico.MultiPoint([(0, 0), (2, 2), (0, 4), (0, 0)]), {"group": 2})
        ])

        def to_points(feature):
            return pico.FeatureCollection(
                [pico.Feature(pico.Point(xy), feature.properties)
                 for xy in feature.geometry.coordinates]
            )

        expected = pico.FeatureCollection([
            pico.Feature(pico.Point((0, 0)), {"group": 1}), pico.Feature(pico.Point((1, 1)), {"group": 1}),
            pico.Feature(pico.Point((0, 2)), {"group": 1}), pico.Feature(pico.Point((0, 0)), {"group": 1}),
            pico.Feature(pico.Point((0, 0)), {"group": 2}), pico.Feature(pico.Point((2, 2)), {"group": 2}),
            pico.Feature(pico.Point((0, 4)), {"group": 2}), pico.Feature(pico.Point((0, 0)), {"group": 2})
        ])

        self.assertEqual(gc.flatmap(to_points), expected)


if __name__ == "__main__":
    unittest.main()
