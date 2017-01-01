""" Unit tests for vector functions """

import unittest
import os
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import json

import picogeojson as pgj
from picogeojson import Serializer, Deserializer, DEFAULTCRS

TESTDATA = "tests/"

class DeserializerTests(unittest.TestCase):

    def test_point_read(self):
        with open(os.path.join(TESTDATA, 'point.json')) as f:
            reader = Deserializer(f)
        res = reader.parse()
        self.assertEqual(res.coordinates, [100.0, 0.0])
        return

    def test_linestring_read(self):
        with open(os.path.join(TESTDATA, 'linestring.json')) as f:
            reader = Deserializer(f)
        res = reader.parse()
        self.assertEqual(res.coordinates, [[100.0, 0.0], [101.0, 1.0]])
        return

    def test_polygon_read(self):
        with open(os.path.join(TESTDATA, 'polygon.json')) as f:
            reader = Deserializer(f)
        res = reader.parse()
        self.assertEqual(res.coordinates,
            [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]])
        return

    def test_multipoint_read(self):
        with open(os.path.join(TESTDATA, 'multipoint.json')) as f:
            reader = Deserializer(f)
        res = reader.parse()
        self.assertEqual(res.coordinates, [[100.0, 0.0], [101.0, 1.0]])
        return

    def test_multilinestring_read(self):
        with open(os.path.join(TESTDATA, 'multilinestring.json')) as f:
            reader = Deserializer(f)
        res = reader.parse()
        self.assertEqual(res.coordinates, [[[100.0, 0.0], [101.0, 1.0]],
                                              [[102.0, 2.0], [103.0, 3.0]]])
        return

    def test_multipolygon_read(self):
        with open(os.path.join(TESTDATA, 'multipolygon.json')) as f:
            reader = Deserializer(f)
        res = reader.parse()
        self.assertEqual(res.coordinates,
            [[[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]],
             [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]],
             [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2]]]])
        return

    def test_geometrycollection_read(self):
        with open(os.path.join(TESTDATA, 'geometrycollection.json')) as f:
            reader = Deserializer(f)
        res = reader.parse()
        self.assertEqual(len(res.geometries), 2)
        self.assertTrue(isinstance(res.geometries[0], pgj.Point))
        self.assertTrue(isinstance(res.geometries[1], pgj.LineString))
        return

    def test_featurecollection_read(self):
        path = os.path.join(TESTDATA, "featurecollection.json")
        with open(path) as f:
            reader = Deserializer(f)
        fc = reader.parse()
        self.assertTrue(isinstance(fc.features[0].geometry, pgj.Point))
        self.assertEqual(fc.features[0].geometry.coordinates, [102.0, 0.5])
        self.assertEqual(fc.features[0].properties["scalar"], {"prop0": "value0"})

        self.assertTrue(isinstance(fc.features[1].geometry, pgj.LineString))
        self.assertEqual(fc.features[1].geometry.coordinates,
                        [[102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]])
        self.assertEqual(fc.features[1].properties["scalar"],
                        {"prop0": "value0", "prop1": 0.0})

        self.assertTrue(isinstance(fc.features[2].geometry, pgj.Polygon))
        self.assertEqual(fc.features[2].geometry.coordinates,
                        [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0],
                          [100.0, 1.0], [100.0, 0.0]]])
        self.assertEqual(fc.features[2].properties["scalar"],
                        {"prop0": "value0", "prop1": {"this": "that"}})
        return

class SerializerTests(unittest.TestCase):

    def setUp(self):
        self.serializer = Serializer()
        return

    def test_serialize_point(self):
        pt = pgj.Point((44.0, 17.0), DEFAULTCRS)
        s = self.serializer(pt)
        d = json.loads(s)
        self.assertEqual(tuple(pt.coordinates), tuple(d["coordinates"]))
        return

    def test_serialize_linestring(self):
        linestring = pgj.LineString([[44.0, 17.0], [43.0, 17.5], [-2.1, 4.0]],
                                        DEFAULTCRS)
        s = self.serializer(linestring)
        d = json.loads(s)
        self.assertEqual(list(linestring.coordinates), list(d["coordinates"]))
        return

    def test_serialize_polygon(self):
        polygon = pgj.Polygon([[[44.0, 17.0], [43.0, 17.5], [-2.1, 4.0], [44.0, 17.0]],
                                   [[1.0, 1.0], [0.5, -0.5], [0.8, -0.7], [1.0, 1.0]]],
                                  DEFAULTCRS)
        s = self.serializer(polygon)
        d = json.loads(s)

        self.assertEqual(list(polygon.coordinates), list(d["coordinates"]))
        return

    def test_serialize_multipoint(self):
        multipoint = pgj.MultiPoint([[44.0, 17.0], [43.0, 17.5], [-2.1, 4.0]],
                                        DEFAULTCRS)
        s = self.serializer(multipoint)
        d = json.loads(s)
        self.assertEqual(list(multipoint.coordinates), list(d["coordinates"]))
        return

    def test_serialize_multilinestring(self):
        multilinestring = pgj.MultiLineString(
                            [[[44.0, 17.0], [43.0, 17.5], [-2.1, 4.0]],
                             [[49.0, -3.0], [48.0, -2.5], [2.9, -16.0]]],
                            DEFAULTCRS)
        s = self.serializer(multilinestring)
        d = json.loads(s)
        self.assertEqual(list(multilinestring.coordinates), list(d["coordinates"]))
        return

    def test_serialize_multipolygon(self):
        multipolygon = pgj.MultiPolygon(
                            [[[44.0, 17.0], [43.0, 17.5], [-2.1, 4.0]],
                              [[1.0, 1.0], [0.5, -0.5], [0.8, [-0.7]]],
                             [[[49.0, -3.0], [48.0, -2.5], [2.9, -16.0]]]],
                            DEFAULTCRS)
        s = self.serializer(multipolygon)
        d = json.loads(s)
        self.assertEqual(list(multipolygon.coordinates), list(d["coordinates"]))
        return

    def test_serialize_geometrycollection(self):
        collection = pgj.GeometryCollection([pgj.Point((3, 4), None),
                                             pgj.Point((5, 6), None),
                                             pgj.LineString([(1, 2), (3, 4), (3, 2)], None)],
                                            DEFAULTCRS)
        s = self.serializer(collection)
        d = json.loads(s)
        self.assertEqual(len(d.get("geometries", [])), 3)
        self.assertEqual(d.get("crs", ""), DEFAULTCRS)
        return

    def test_serialize_feature(self):
        feature = pgj.Feature(pgj.Point((1,2), None), {"type": "city"}, 1, DEFAULTCRS)
        s = self.serializer(feature)
        d = json.loads(s)
        self.assertEqual(d.get("geometry", {}).get("type", ""), "Point")
        self.assertEqual(d.get("id", 0), 1)
        self.assertEqual(d.get("properties", {}).get("type", ""), "city")
        return

    def test_serialize_featurecollection(self):
        collection = pgj.FeatureCollection(
                [pgj.Feature(pgj.Point((7,3), None), {"type": "city"}, None, None),
                 pgj.Feature(pgj.LineString([(1,2), (1,3), (2, 2)], None),
                             {"type": "river"}, None, None),
                 pgj.Feature(pgj.Polygon([[(1,2), (1,3), (2, 2), (2, 1)]], None),
                             {"type": "boundary"}, None, None)],
                DEFAULTCRS)
        s = self.serializer(collection)
        d = json.loads(s)
        self.assertEqual(len(d.get("features", [])), 3)
        self.assertEqual(d.get("crs", ""), DEFAULTCRS)
        return

class AntimerdianTests(unittest.TestCase):

    def test_linestring_crosses(self):
        self.assertTrue(pgj.antimeridian.crosses_antimeridian(
                            pgj.LineString([(172, 34), (178, 36), (-179, 37), (-177, 39)])
                        ))

        self.assertFalse(pgj.antimeridian.crosses_antimeridian(
                            pgj.LineString([(172, 34), (178, 36), (179, 37), (178, 39)])
                        ))

    def test_linestring_split(self):
        res = pgj.antimeridian.antimeridian_cut(
                pgj.LineString([(172, 34), (178, 36), (-179, 37), (-177, 39)])
                )
        self.assertTrue(isinstance(res, pgj.MultiLineString))
        self.assertEqual(len(res.coordinates), 2)
        self.assertEqual(res.coordinates[0][-1], (180, 36.33333333))
        self.assertEqual(res.coordinates[1][0], (-179.99999999, 36.33333333))


if __name__ == "__main__":
    unittest.main()
