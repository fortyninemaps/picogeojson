import unittest
from picogeojson import (Point, LineString, Polygon,
                         MultiPoint, MultiLineString, MultiPolygon,
                         GeometryCollection, Feature, FeatureCollection,
                         DEFAULTCRS)
from picogeojson.result import GeoJSONResult

class ResultTests(unittest.TestCase):

    def setUp(self):
        self.geometrycollection = \
                GeometryCollection(
                    [Point((1, 2)),
                     Polygon([[(10, 10), (10, 11), (9, 11), (9, 10), (10, 10)]]),
                     LineString([(1, 1), (2, 2), (3, 3)]),
                     GeometryCollection(
                         [Point((3, 4)),
                          MultiPolygon([[[(0, 0), (3, 0), (3, 3), (0, 3), (0, 0)],
                                         [(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)]],
                                        [[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]],
                                        [[(0, 0), (3, 0), (3, 3), (0, 3), (0, 0)],
                                         [(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)]],
                                        [[(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)],
                                         [(10, 10), (10, 20), (20, 20), (20, 10), (10, 10)],
                                         [(50, 50), (50, 55), (55, 60), (60, 50), (50, 50)]]]),
                          Point((5, 6)),
                          LineString([(1, 1), (2, 2), (3, 3)]),
                          Polygon([[(1, 1), (0, 2), (-1, 1), (1, 0), (1, 1)]])],
                         DEFAULTCRS),
                     MultiPoint([(7, 8), (9, 10)]),
                     LineString([(1, 1), (2, 2), (3, 3)]),
                     Point((11, 12)),
                     LineString([(1, 1), (2, 2), (3, 3)]),
                     FeatureCollection([
                     ]),
                     MultiLineString([[(1, 1), (2, 2), (3, 3)],
                                                  [(4, 4), (5, 5), (6, 6)]]),
                     ],
                    DEFAULTCRS)

        self.featurecollection = FeatureCollection([
            Feature(Point((-1, -2)), {"style": "stout"}),

            Feature(MultiPolygon([[[(0, 0), (3, 0), (3, 3), (0, 3), (0, 0)],
                                   [(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)]],
                                  [[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]],
                                  [[(0, 0), (3, 0), (3, 3), (0, 3), (0, 0)],
                                   [(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)]],
                                  [[(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)],
                                   [(10, 10), (10, 20), (20, 20), (20, 10), (10, 10)],
                                   [(50, 50), (50, 55), (55, 60), (60, 50), (50, 50)]]]),
                    {"style": "stout"}),
            Feature(LineString([(-1, -2), (-3, -4), (-5, -3)]),
                    {"style": "lager"}),
            Feature(Polygon([[(-1, -2), (-3, -4), (-5, -3), (-1, -2)]]),
                    {"style": "saison"}),
            Feature(MultiPoint([(-1, -2), (-3, -4), (-5, -3)]),
                    {"style": "kolsch"}),
            Feature(MultiLineString([[(0, 0), (1, 1), (2, 3)],
                                     [(5, 6), (1, 3), (4, 7)]]),
                    {"style": "pilsner"}),
        ], DEFAULTCRS)

    def test_get_points(self):
        result = GeoJSONResult(self.geometrycollection)
        count = 0
        for pt in result.points:
            self.assertTrue(isinstance(pt, Point))
            count += 1
        self.assertEqual(count, 4)

    def test_get_linestrings(self):
        result = GeoJSONResult(self.geometrycollection)
        count = 0
        for ls in result.linestrings:
            self.assertTrue(isinstance(ls, LineString))
            count += 1
        self.assertEqual(count, 4)

    def test_get_polygons(self):
        result = GeoJSONResult(self.geometrycollection)
        count = 0
        for pg in result.polygons:
            self.assertTrue(isinstance(pg, Polygon))
            count += 1
        self.assertEqual(count, 2)

    def test_get_multipoints(self):
        result = GeoJSONResult(self.geometrycollection)
        count = 0
        for mpt in result.multipoints:
            self.assertTrue(isinstance(mpt, MultiPoint))
            count += 1
        self.assertEqual(count, 1)

    def test_get_multilinestrings(self):
        result = GeoJSONResult(self.geometrycollection)
        count = 0
        for mls in result.multilinestrings:
            self.assertTrue(isinstance(mls, MultiLineString))
            count += 1
        self.assertEqual(count, 1)

    def test_get_multipolygons(self):
        result = GeoJSONResult(self.geometrycollection)
        count = 0
        for mpg in result.multipolygons:
            self.assertTrue(isinstance(mpg, MultiPolygon))
            count += 1
        self.assertEqual(count, 1)

    def test_get_point_features(self):
        result = GeoJSONResult(self.featurecollection)
        count = 0
        for f in result.features("Point"):
            self.assertTrue(isinstance(f, Feature))
            self.assertTrue(isinstance(f.geometry, Point))
            count += 1
        self.assertEqual(count, 1)

    def test_get_linestring_features(self):
        result = GeoJSONResult(self.featurecollection)
        count = 0
        for f in result.features("LineString"):
            self.assertTrue(isinstance(f, Feature))
            self.assertTrue(isinstance(f.geometry, LineString))
            count += 1
        self.assertEqual(count, 1)

    def test_get_polygon_features(self):
        result = GeoJSONResult(self.featurecollection)
        count = 0
        for f in result.features("Polygon"):
            self.assertTrue(isinstance(f, Feature))
            self.assertTrue(isinstance(f.geometry, Polygon))
            count += 1
        self.assertEqual(count, 1)

    def test_get_multipoint_features(self):
        result = GeoJSONResult(self.featurecollection)
        count = 0
        for f in result.features("MultiPoint"):
            self.assertTrue(isinstance(f, Feature))
            self.assertTrue(isinstance(f.geometry, MultiPoint))
            count += 1
        self.assertEqual(count, 1)

    def test_get_multilinestring_features(self):
        result = GeoJSONResult(self.featurecollection)
        count = 0
        for f in result.features("MultiLineString"):
            self.assertTrue(isinstance(f, Feature))
            self.assertTrue(isinstance(f.geometry, MultiLineString))
            count += 1
        self.assertEqual(count, 1)

    def test_get_multipolygon_features(self):
        result = GeoJSONResult(self.featurecollection)
        count = 0
        for f in result.features("MultiPolygon"):
            self.assertTrue(isinstance(f, Feature))
            self.assertTrue(isinstance(f.geometry, MultiPolygon))
            count += 1
        self.assertEqual(count, 1)

    def test_features_argument_error(self):
        result = GeoJSONResult(self.featurecollection)
        with self.assertRaises(TypeError):
            [a for a in result.features({"style": "stout"})]

    def test_get_by_attributes(self):
        result = GeoJSONResult(self.featurecollection)
        count = 0
        for f in result.features(properties={"style": "stout"}):
            count += 1
        self.assertEqual(count, 2)
        for f in result.features(properties={"style": "kolsch"}):
            self.assertTrue(isinstance(f.geometry, MultiPoint))

if __name__ == "__main__":
    unittest.main()
