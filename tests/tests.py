import json
import os
import sys
import unittest

if sys.version_info.major >= 3:
    from io import StringIO
else:
    from StringIO import StringIO

try:
    import pathlib
except ImportError:
    pass

import picogeojson as pico
from picogeojson import Serializer, Deserializer, merge, burst, DEFAULTCRS
import picogeojson.bbox as bbox
from picogeojson.geojson import fixed_precision
from picogeojson.result import Result

from type_tests import ClosedRingTests, InvalidCoordTests, FuncTests
from result_tests import ResultTests

TESTDATA = "tests/"

class DeserializerTests(unittest.TestCase):

    def setUp(self):
        self.deserializer = Deserializer()
        return

    def test_shorthand(self):
        res = pico.fromfile(os.path.join(TESTDATA, 'point.json'))
        self.assertEqual(res.coordinates, [100.0, 0.0])
        return

    def test_fromdict(self):
        d = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]]
                },
                "properties": {
                    "cover": "water",
                    "color": "blue"
                }
        }
        geom = pico.fromdict(d)
        self.assertEqual(d["geometry"]["coordinates"], geom.geometry.coordinates)
        self.assertEqual(d["properties"], geom.properties)
        return

    def test_shorthand_result(self):
        res = pico.result_fromfile(os.path.join(TESTDATA, 'point.json'))
        self.assertEqual(type(res), Result)
        for pt in res.points:
            self.assertEqual(pt.coordinates, [100.0, 0.0])
        return

    def test_shorthand_string(self):
        with open(os.path.join(TESTDATA, 'point.json'), 'r') as f:
            string = f.read()
        res = pico.fromstring(string)
        self.assertEqual(res.coordinates, [100.0, 0.0])
        return

    def test_shorthand_string_compat(self):
        with open(os.path.join(TESTDATA, 'point.json'), 'r') as f:
            string = f.read()
        res = pico.loads(string)
        self.assertEqual(res.coordinates, [100.0, 0.0])
        return

    def test_shorthand_string_result(self):
        with open(os.path.join(TESTDATA, 'point.json'), 'r') as f:
            string = f.read()
        res = pico.result_fromstring(string)
        self.assertEqual(type(res), Result)
        for pt in res.points:
            self.assertEqual(pt.coordinates, [100.0, 0.0])
        return

    def test_point_read(self):
        res = self.deserializer.fromfile(os.path.join(TESTDATA, 'point.json'))
        self.assertEqual(res.coordinates, [100.0, 0.0])

        # check __call__ version
        res = self.deserializer(os.path.join(TESTDATA, 'point.json'))
        self.assertEqual(res.coordinates, [100.0, 0.0])
        return

    def test_point_read_fileobject(self):
        with open(os.path.join(TESTDATA, 'point.json'), 'r') as f:
            res = self.deserializer.fromfile(f)
        self.assertEqual(res.coordinates, [100.0, 0.0])

        # check __call__ version
        with open(os.path.join(TESTDATA, 'point.json'), 'r') as f:
            res = self.deserializer(f)
        self.assertEqual(res.coordinates, [100.0, 0.0])
        return

    def test_linestring_read(self):
        res = self.deserializer.fromfile(os.path.join(TESTDATA, 'linestring.json'))
        self.assertEqual(res.coordinates, [[100.0, 0.0], [101.0, 1.0]])
        return

    def test_polygon_read(self):
        res = self.deserializer.fromfile(os.path.join(TESTDATA, 'polygon.json'))
        self.assertEqual(res.coordinates,
            [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]])
        return

    @unittest.skipIf(sys.version_info < (3, 4), "pathlib support missing")
    def test_polygon_read_pathlib(self):
        res = self.deserializer.fromfile(pathlib.Path(TESTDATA) / 'polygon.json')
        self.assertEqual(res.coordinates,
            [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]])
        return

    def test_multipoint_read(self):
        res = self.deserializer.fromfile(os.path.join(TESTDATA, 'multipoint.json'))
        self.assertEqual(res.coordinates, [[100.0, 0.0], [101.0, 1.0]])
        return

    def test_multilinestring_read(self):
        res = self.deserializer.fromfile(os.path.join(TESTDATA, 'multilinestring.json'))
        self.assertEqual(res.coordinates, [[[100.0, 0.0], [101.0, 1.0]],
                                           [[102.0, 2.0], [103.0, 3.0]]])
        return

    def test_multipolygon_read(self):
        res = self.deserializer.fromfile(os.path.join(TESTDATA, 'multipolygon.json'))
        self.assertEqual(res.coordinates,
            [[[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]],
             [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]],
              [[100.2, 0.2], [100.2, 0.8], [100.8, 0.8], [100.8, 0.2], [100.2, 0.2]]]])
        return

    def test_geometrycollection_read(self):
        res = self.deserializer.fromfile(os.path.join(TESTDATA, 'geometrycollection.json'))
        self.assertEqual(len(res.geometries), 2)
        self.assertTrue(isinstance(res.geometries[0], pico.Point))
        self.assertTrue(isinstance(res.geometries[1], pico.LineString))
        return

    def test_feature_read(self):
        fc = self.deserializer.fromfile(os.path.join(TESTDATA, 'feature.json'))
        self.assertEqual(fc.id, 0)
        self.assertEqual(fc.geometry.coordinates,
            [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]])
        self.assertEqual(type(fc.geometry).__name__, "Polygon")
        self.assertEqual(fc.properties["name"], "Strathcona")

    def test_featurecollection_read(self):
        fc = self.deserializer.fromfile(os.path.join(TESTDATA, 'featurecollection.json'))
        self.assertTrue(isinstance(fc.features[0].geometry, pico.Point))
        self.assertEqual(fc.features[0].geometry.coordinates, [102.0, 0.5])
        self.assertEqual(fc.features[0].properties, {"prop0": "value0"})

        self.assertTrue(isinstance(fc.features[1].geometry, pico.LineString))
        self.assertEqual(fc.features[1].geometry.coordinates,
                        [[102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]])
        self.assertEqual(fc.features[1].properties,
                        {"prop0": "value0", "prop1": 0.0})

        self.assertTrue(isinstance(fc.features[2].geometry, pico.Polygon))
        self.assertEqual(fc.features[2].geometry.coordinates,
                        [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0],
                          [100.0, 1.0], [100.0, 0.0]]])
        self.assertEqual(fc.features[2].properties,
                        {"prop0": "value0", "prop1": {"this": "that"}})
        return

class SerializerTests(unittest.TestCase):

    def setUp(self):
        self.serializer = Serializer(write_crs=True)
        return

    def test_shorthand(self):
        pt = pico.Point((44.0, 17.0), DEFAULTCRS)
        d = json.loads(pico.tostring(pt))
        self.assertEqual(tuple(pt.coordinates), tuple(d["coordinates"]))
        self.assertTrue("crs" not in d)

        d = json.loads(pico.tostring(pt, write_crs=True))
        self.assertEqual(pt.crs, d["crs"])

    def test_shorthand_file(self):
        pt = pico.Point((44.0, 17.0), DEFAULTCRS)
        f = StringIO()
        pico.tofile(pt, f)
        f.seek(0)
        pt2 = pico.fromfile(f)
        f.close()
        self.assertEqual(tuple(pt.coordinates), tuple(pt2.coordinates))
        self.assertEqual(pt.crs, pt2.crs)

    def test_shorthand_compat(self):
        pt = pico.Point((44.0, 17.0), DEFAULTCRS)
        d = json.loads(pico.dumps(pt))
        self.assertEqual(tuple(pt.coordinates), tuple(d["coordinates"]))

    def test_todict(self):
        geom = pico.Feature(pico.Polygon([[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]]),
                            {"cover": "water", "color": "blue"})

        d = pico.todict(geom)
        self.assertEqual(d["geometry"]["coordinates"], geom.geometry.coordinates)
        self.assertEqual(d["properties"], geom.properties)
        return

    def test_serialize_point(self):
        pt = pico.Point((44.0, 17.0), DEFAULTCRS)
        s = self.serializer(pt)
        d = json.loads(s)
        self.assertEqual(tuple(pt.coordinates), tuple(d["coordinates"]))
        return

    def test_serialize_linestring(self):
        linestring = pico.LineString([[44.0, 17.0], [43.0, 17.5], [-2.1, 4.0]],
                                     DEFAULTCRS)
        s = self.serializer(linestring)
        d = json.loads(s)
        self.assertEqual(list(linestring.coordinates), list(d["coordinates"]))
        return

    def test_serialize_polygon(self):
        polygon = pico.Polygon([[[44.0, 17.0], [43.0, 17.5], [-2.1, 4.0], [44.0, 17.0]],
                                [[1.0, 1.0], [0.8, -0.7], [0.5, -0.5], [1.0, 1.0]]],
                               DEFAULTCRS)
        s = self.serializer(polygon)
        d = json.loads(s)

        self.assertEqual(list(polygon.coordinates), list(d["coordinates"]))
        return

    def test_serialize_polygon_antimeridian(self):
        polygon = pico.Polygon([[(172, -20), (-179, -20), (-177, -25),
                                 (172, -25), (172, -20)]])
        s = self.serializer(polygon)
        d = json.loads(s)
        self.assertEqual(d["type"], "MultiPolygon")
        return

    def test_serialize_multipoint(self):
        multipoint = pico.MultiPoint([[44.0, 17.0], [43.0, 17.5], [-2.1, 4.0]],
                                     DEFAULTCRS)
        s = self.serializer(multipoint)
        d = json.loads(s)
        self.assertEqual(list(multipoint.coordinates), list(d["coordinates"]))
        return

    def test_serialize_multilinestring(self):
        multilinestring = pico.MultiLineString(
                            [[[44.0, 17.0], [43.0, 17.5], [-2.1, 4.0]],
                             [[49.0, -3.0], [48.0, -2.5], [2.9, -16.0]]],
                            DEFAULTCRS)
        s = self.serializer(multilinestring)
        d = json.loads(s)
        self.assertEqual(list(multilinestring.coordinates), list(d["coordinates"]))
        return

    def test_serialize_multipolygon(self):
        multipolygon = pico.MultiPolygon(
                            [[[[44.0, 17.0], [43.0, 17.5], [-2.1, 4.0], [44.0, 17.0]],
                              [[1.0, 1.0], [0.8, -0.7], [0.5, -0.5], [1.0, 1.0]]],
                             [[[49.0, -3.0], [48.0, -2.5], [2.9, -16.0], [49.0, -3.0]]]],
                            DEFAULTCRS)
        s = self.serializer(multipolygon)
        d = json.loads(s)
        self.assertEqual(list(multipolygon.coordinates), list(d["coordinates"]))
        return

    def test_serialize_geometrycollection(self):
        collection = pico.GeometryCollection(
                            [pico.Point((3, 4), None),
                             pico.Point((5, 6), None),
                             pico.LineString([(1, 2), (3, 4), (3, 2)], None)],
                            DEFAULTCRS)
        s = self.serializer(collection)
        d = json.loads(s)
        self.assertEqual(len(d.get("geometries", [])), 3)
        self.assertEqual(d.get("crs", ""), DEFAULTCRS)
        return

    def test_serialize_geometrycollection_empty(self):
        collection = pico.GeometryCollection([], DEFAULTCRS)
        s = self.serializer(collection)
        d = json.loads(s)
        self.assertEqual(len(d.get("geometries", [0])), 0)
        self.assertEqual(d.get("crs", ""), DEFAULTCRS)
        return

    def test_top_bbox_only_geometry_collection(self):
        collection = pico.GeometryCollection(
                            [pico.Point((3, 4), None),
                             pico.Polygon([[(5, 6), (7, 8), (9, 10), (5, 6)]], None),
                             pico.LineString([(1, 2), (3, 4), (3, 2)], None)],
                            DEFAULTCRS)
        s = self.serializer(collection)
        d = json.loads(s)
        self.assertFalse(d["geometries"][1].get("bbox", False))
        self.assertFalse(d["geometries"][2].get("bbox", False))
        self.assertTrue(d.get("bbox", False) is not False)

    def test_top_bbox_only_feature_collection(self):
        collection = pico.FeatureCollection(
                [pico.Feature(pico.Point((7,3), None), {"type": "city"}, None, None),
                 pico.Feature(pico.LineString([(1,2), (1,3), (2, 2)], None),
                             {"type": "river"}, None, None),
                 pico.Feature(pico.Polygon([[(1,2), (1,3), (2, 2), (1, 2)]], None),
                             {"type": "boundary"}, None, None)],
                DEFAULTCRS)
        s = self.serializer(collection)
        d = json.loads(s)
        self.assertFalse(d["features"][1]["geometry"].get("bbox", False))
        self.assertFalse(d["features"][2]["geometry"].get("bbox", False))
        self.assertTrue(d.get("bbox", False) is not False)

    def test_serialize_feature(self):
        feature = pico.Feature(pico.Point((1,2), None), {"type": "city"}, 1, DEFAULTCRS)
        s = self.serializer(feature)
        d = json.loads(s)
        self.assertEqual(d.get("geometry", {}).get("type", ""), "Point")
        self.assertEqual(d.get("id", 0), 1)
        self.assertEqual(d.get("properties", {}).get("type", ""), "city")
        return

    def test_serialize_featurecollection(self):
        collection = pico.FeatureCollection(
                [pico.Feature(pico.Point((7,3), None), {"type": "city"}, None, None),
                 pico.Feature(pico.LineString([(1,2), (1,3), (2, 2)], None),
                             {"type": "river"}, None, None),
                 pico.Feature(pico.Polygon([[(1,2), (1,3), (2, 2), (2, 1), (1,2)]], None),
                             {"type": "boundary"}, None, None)],
                DEFAULTCRS)
        s = self.serializer(collection)
        d = json.loads(s)
        self.assertEqual(len(d.get("features", [])), 3)
        self.assertEqual(d.get("crs", ""), DEFAULTCRS)
        return

    def test_serialize_featurecollection_empty(self):
        collection = pico.FeatureCollection([], DEFAULTCRS)
        s = self.serializer(collection)
        d = json.loads(s)
        self.assertEqual(len(d.get("features", [0])), 0)
        self.assertEqual(d.get("crs", ""), DEFAULTCRS)
        return

    def test_dedup_crs_geometrycollection(self):
        crs = {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}
        collection = pico.GeometryCollection(
                [pico.Point((1, 2), crs=crs)],
                crs=crs)
        s = self.serializer(collection)
        self.assertEqual(s.count('"crs"'), 1)

    def test_dedup_crs_feature(self):
        crs = {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}
        feature = pico.Feature(pico.Point((1, 2), crs=crs),
                                      {"type": "tree"}, id=1, crs=crs)
        s = self.serializer(feature)
        self.assertEqual(s.count('"crs"'), 1)

    def test_dedup_crs_feature_collection(self):
        crs = {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}
        coll = pico.FeatureCollection(
                    [pico.Feature(pico.Point((1, 2), crs=crs),
                                         {"type": "tree"}, id=1, crs=crs),
                     pico.Feature(pico.LineString([(1, 2), (2, 3)], crs=crs),
                                         {"type": "fence"}, id=2, crs=crs),
                     pico.Feature(pico.Point((5, 4), crs=crs),
                                         {"type": "pothole"}, id=3, crs=crs)],
                    crs=crs)
        s = self.serializer(coll)
        self.assertEqual(s.count('"crs"'), 1)

    def test_serialize_precision_point(self):
        pt = pico.Point((44.1234567, 17.0987654))
        ser = Serializer(precision=3)
        s = ser(pt)
        d = json.loads(s)
        self.assertEqual((44.123, 17.099), tuple(d["coordinates"]))
        return


class AntimerdianTests(unittest.TestCase):

    def test_contains(self):
        self.assertFalse(pico.antimeridian.contains(
            [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)],
            [(2, 0), (2, 1), (3, 1), (3, 0), (2, 0)]))

        self.assertTrue(pico.antimeridian.contains(
            [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)],
            [(1, 1), (1, 3), (3, 3), (3, 1), (1, 1)]))
        return

    def test_linestring_split(self):
        res = pico.antimeridian.antimeridian_cut(
                pico.LineString([(172, 34), (178, 36), (-179, 37), (-177, 39)])
                )
        self.assertTrue(isinstance(res, pico.MultiLineString))
        self.assertEqual(len(res.coordinates), 2)
        self.assertEqual(res.coordinates[0][-1], (180, 36.33333333))
        self.assertEqual(res.coordinates[1][0], (-179.99999999, 36.33333333))

    def test_polygon_split(self):
        res = pico.antimeridian.antimeridian_cut(
                pico.Polygon([[(172, -20), (-179, -20), (-177, -25), (172, -25), (172, -20)]])
                )
        self.assertTrue(isinstance(res, pico.MultiPolygon))
        self.assertEqual(len(res.coordinates), 2)

    def test_polygon_split_holes(self):
        res = pico.antimeridian.antimeridian_cut(
                pico.Polygon([[(172, -20), (-179, -20), (-177, -25), (172, -25), (172, -20)],
                              [(174, -22), (-179, -22), (-179, -23), (174, -22)]])
                )
        self.assertTrue(isinstance(res, pico.MultiPolygon))
        self.assertEqual(len(res.coordinates), 2)
        self.assertEqual(len(res.coordinates[0]), 2)
        self.assertEqual(len(res.coordinates[1]), 2)

    def test_multilinestring_split(self):
        res = pico.antimeridian.antimeridian_cut(
                pico.MultiLineString(
                            [[(172, 34), (178, 36), (-179, 37), (-177, 39)],
                             [(172, -34), (178, -36), (-179, -37), (-177, -39)]])
                )
        self.assertEqual(len(res.coordinates), 4)

    def test_featurecollection_split(self):
        res = pico.antimeridian.antimeridian_cut(
                pico.FeatureCollection([
                    pico.Feature(
                        pico.LineString([(172, 34), (178, 36), (-179, 37), (-177, 39)]),
                        {"desc": "a linestring spanning the dateline"}),
                    pico.Feature(
                        pico.Point((1,2)),
                        {"desc": "a single point"}),
                    pico.Feature(
                        pico.GeometryCollection([
                            pico.Polygon([[(178, 3), (-178, 5), (-178, 7), (178, 5), (178, 3)]]),
                            pico.LineString([(172, -34), (178, -36), (-179, -37), (-177, -39)])]),
                        {"desc": "a geometry collection containing a polygon and a linestring"})
                    ]))
        self.assertEqual(type(res).__name__, "FeatureCollection")
        self.assertEqual(len(res.features), 3)
        self.assertEqual(type(res.features[0].geometry).__name__,
                         "MultiLineString")
        self.assertEqual(type(res.features[2].geometry).__name__,
                         "GeometryCollection")
        self.assertEqual(type(res.features[2].geometry.geometries[0]).__name__,
                         "MultiPolygon")

class OrientationTests(unittest.TestCase):

    def test_isccw(self):
        self.assertTrue(pico.orientation.is_counterclockwise(
            [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]))

        self.assertFalse(pico.orientation.is_counterclockwise(
            [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]))

class BboxTests(unittest.TestCase):

    def test_coordinate_bbox_2d(self):
        cs = [[i, j] for i in range(0, 30, 3) for j in range(10, -10, -2)]
        bbx = bbox.coordstring_bbox(cs)
        self.assertEqual(bbx, [0, -8, 27, 10])

    def test_coordinate_bbox_3d(self):
        cs = [[i, j, k] for i in range(0, 30, 3)
                        for j in range(10, -10, -2)
                        for k in range(1, 5)]
        bbx = bbox.coordstring_bbox(cs)
        self.assertEqual(bbx, [0, -8, 1, 27, 10, 4])

    def test_coordinate_bbox_empty(self):
        cs = []
        bbx = bbox.coordstring_bbox(cs)
        self.assertTrue(bbx is None)

    def test_point_bbox_2(self):
        p = pico.Point((2, 3))
        bbx = bbox.geom_bbox(p)
        self.assertEqual(bbx, [2, 3, 2, 3])

    def test_point_bbox_3(self):
        p = pico.Point((2, 3, 1))
        bbx = bbox.geom_bbox(p)
        self.assertEqual(bbx, [2, 3, 1, 2, 3, 1])

    def test_geometrycollection_bbox_2(self):
        collection = pico.GeometryCollection(
                            [pico.Point((3, 4), None),
                             pico.Point((5, 6), None),
                             pico.LineString([(1, 2), (3, 4), (3, 2)], None)],
                            DEFAULTCRS)
        bbx = bbox.geom_bbox(collection)
        self.assertEqual(bbx, [1, 2, 5, 6])

    def test_geometrycollection_bbox_some_empty(self):
        collection = pico.GeometryCollection(
                            [pico.Point((3, 4), None),
                             pico.Point((5, 6), None),
                             pico.GeometryCollection([], None)],
                            DEFAULTCRS)
        bbx = bbox.geom_bbox(collection)
        self.assertEqual(bbx, [3, 4, 5, 6])

    def test_geometrycollection_bbox_3(self):
        collection = pico.GeometryCollection(
                            [pico.Point((3, 4, 1), None),
                             pico.Point((5, 6, 2), None),
                             pico.LineString([(1, 2, 2), (3, 4, 5), (3, 2, 3)], None)],
                            DEFAULTCRS)
        bbx = bbox.geom_bbox(collection)
        self.assertEqual(bbx, [1, 2, 1, 5, 6, 5])

    def test_feature_bbox_2(self):
        feature = pico.Feature(
                    pico.LineString([(1,2), (1,3), (2, 2)], None),
                    {"type": "river"}, None, None)
        bbx = bbox.feature_bbox(feature)
        self.assertEqual(bbx, [1, 2, 2, 3])

    def test_feature_bbox_3(self):
        feature = pico.Feature(
                    pico.LineString([(1, 2, 1), (1, 3, 0.5), (2, 2, 0)], None),
                    {"type": "river"}, None, None)
        bbx = bbox.feature_bbox(feature)
        self.assertEqual(bbx, [1, 2, 0, 2, 3, 1])

    def test_feature_collection_bbox_empty(self):
        collection = pico.FeatureCollection([], None)
        self.assertTrue(bbox.feature_collection_bbox(collection) is None)

    def test_feature_collection_bbox(self):
        feature1 = pico.Feature(pico.LineString([(1,2), (1,3), (2, 2)], None),
                                {"type": "river"}, None, None)

        feature2 = pico.Feature(pico.Point((0,2), None),
                                {"type": "spring"}, None, None)
        collection = pico.FeatureCollection([feature1, feature2], None)
        bbx = bbox.feature_collection_bbox(collection)
        self.assertEqual(bbx, [0, 2, 2, 3])

class FixedPrecisionTests(unittest.TestCase):

    def test_scalar(self):
        self.assertEqual(fixed_precision(3.141592654, 3), 3.142)

    def test_list(self):
        self.assertEqual(fixed_precision([1.234567, 2.345678, 3.456789], 3),
                                         [1.235, 2.346, 3.457])

    def test_nested_list(self):
        self.assertEqual(fixed_precision([[1.234567, 2.345678], 3.456789], 3),
                                         [[1.235, 2.346], 3.457])


class MergeBurstTests(unittest.TestCase):

    def test_merge_empty(self):
        with self.assertRaises(ValueError):
            merge([])

    def test_merge_one(self):
        pt = pico.Point((1, 2))
        merged = merge([pt])
        self.assertEqual(pt, merged)

    def test_merge_points(self):
        pts = [pico.Point((1, 2)),
               pico.Point((3, 4)),
               pico.Point((5, 6)),
               pico.Point((7, 8))]
        merged = merge(pts)
        self.assertEqual(type(merged).__name__, "MultiPoint")
        self.assertEqual(len(merged.coordinates), 4)

    def test_merge_linestrings(self):
        lns = [pico.LineString([(1, 2), (2, 2), (1, 1), (-1, 2)]),
               pico.LineString([(3, 4), (3, 4), (3, 2), (-3, 4)]),
               pico.LineString([(5, 6), (4, 6), (5, 3), (-5, 6)]),
               pico.LineString([(7, 8), (5, 8), (7, 4), (-7, 8)])]
        merged = merge(lns)
        self.assertEqual(type(merged).__name__, "MultiLineString")
        self.assertEqual(len(merged.coordinates), 4)

    def test_merge_polygons(self):
        plg = [pico.Polygon([[(1, 2), (2, 2), (1, 1), (-1, 2), (1, 2)]]),
               pico.Polygon([[(3, 4), (3, 4), (3, 2), (-3, 4), (3, 4)]]),
               pico.Polygon([[(5, 6), (4, 6), (5, 3), (-5, 6), (5, 6)]]),
               pico.Polygon([[(7, 8), (5, 8), (7, 4), (-7, 8), (7, 8)]])]
        merged = merge(plg)
        self.assertEqual(type(merged).__name__, "MultiPolygon")
        self.assertEqual(len(merged.coordinates), 4)

    def test_merge_geometrycollections(self):
        gcs = [pico.GeometryCollection([
                    pico.Point((1, 2)),
                    pico.LineString([(2, 2), (1, 1), (-1, 2)])]),
               pico.GeometryCollection([
                    pico.MultiPoint([(7, 8), (5, 8), (7, 4), (-7, 8)]),
                    pico.Point((9, 8))])
               ]
        merged = merge(gcs)
        self.assertEqual(type(merged).__name__, "GeometryCollection")
        self.assertEqual(len(merged.geometries), 2)

    def test_merge_geometries(self):
        gms = [pico.LineString([(1, 2), (2, 2), (1, 1), (-1, 2)]),
               pico.Point((3, 4)),
               pico.Polygon([[(5, 6), (4, 6), (2, 5), (5, 5), (5, 6)]])]
        merged = merge(gms)
        self.assertEqual(type(merged).__name__, "GeometryCollection")
        self.assertEqual(len(merged.geometries), 3)

    def test_merge_features(self):
        gms = [pico.Feature(
                    pico.LineString([(1, 2), (2, 2), (1, 1), (-1, 2)]),
                    {"desc": "single linestring"}
                    ),
               pico.Feature(pico.Point((3, 4)),
                   {"desc": "single point"}),
               pico.Feature(pico.GeometryCollection(
                   [pico.LineString([(1, 2), (2, 3), (1, 4)]),
                    pico.Point((-2, -3))]),
                   {"desc": "collection of geometries"}),
               pico.Feature(pico.Polygon([[(5, 6), (4, 6), (2, 5), (5, 5), (5, 6)]]),
                   {"desc": "single polygon"})]
        merged = merge(gms)
        self.assertEqual(type(merged).__name__, "FeatureCollection")
        self.assertEqual(len(merged.features), 4)

    def test_merge_features_featurecollections(self):
        gms = [pico.Feature(pico.LineString([(1, 2), (2, 2), (1, 1), (-1, 2)]),
                            {"desc": "single linestring"}),
               pico.FeatureCollection(
                   [pico.Feature(pico.Point((3, 4)),
                       {"desc": "single point"}),
                    pico.Feature(pico.GeometryCollection(
                       [pico.LineString([(1, 2), (2, 3), (1, 4)]),
                        pico.Point((-2, -3))]),
                       {"desc": "collection of geometries"})]
               ),
               pico.Feature(pico.Polygon([[(5, 6), (4, 6), (2, 5), (5, 5), (5, 6)]]),
                            {"desc": "single polygon"})]
        merged = merge(gms)
        self.assertEqual(type(merged).__name__, "FeatureCollection")
        self.assertEqual(len(merged.features), 4)

    def test_merge_featurecollections(self):
        fcs = [pico.FeatureCollection([
                   pico.Feature(
                        pico.LineString([(1, 2), (2, 2), (1, 1), (-1, 2)]),
                        {"desc": "single linestring"}),
                   pico.Feature(
                        pico.LineString([(0, 2), (1, -1), (1, 0), (-1, 3)]),
                        {"desc": "another linestring"})]),
               pico.FeatureCollection(
                   [pico.Feature(pico.Point((3, 4)),
                       {"desc": "single point"}),
                    pico.Feature(pico.GeometryCollection(
                       [pico.LineString([(1, 2), (2, 3), (1, 4)]),
                        pico.Point((-2, -3))]),
                       {"desc": "collection of geometries"})])]
        merged = merge(fcs)
        self.assertEqual(type(merged).__name__, "FeatureCollection")
        self.assertEqual(len(merged.features), 4)

    def test_burst_multipoint(self):
        result = list(burst(pico.MultiPoint([(1, 2), (3, 4), (5, 6)])))
        self.assertEqual(len(result), 3)
        self.assertEqual(type(result[0]).__name__, "Point")
        self.assertEqual(type(result[1]).__name__, "Point")
        self.assertEqual(type(result[2]).__name__, "Point")

    def test_burst_point(self):
        result = list(burst(pico.Point((1, 2))))
        self.assertEqual(len(result), 1)
        self.assertEqual(type(result[0]).__name__, "Point")

    def test_burst_geometrycollection(self):
        result = list(burst(pico.GeometryCollection([
            pico.Point((1, 2)),
            pico.LineString([(3, 4), (5, 6), (7, 6)]),
            pico.Polygon([[(1, 1), (2, 2), (2, 3), (1, 2), (1, 1)]]),
            pico.MultiLineString([[(0, 0), (0, 1), (1, 1)],
                                  [(0, 0), (1, 0), (1, 1)]])
            ], crs=DEFAULTCRS)))
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0].crs, DEFAULTCRS)

    def test_burst_multipolygon(self):
        result = list(burst(pico.MultiPolygon([
                                    [[(1, 2), (2, 3), (1, 3), (1, 2)]],
                                    [[(1, 2), (-2, -3), (-1, -3), (1, 2)]]],
                                    crs=DEFAULTCRS)))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].crs, DEFAULTCRS)

    def test_burst_feature_collection(self):
        result = list(burst(pico.FeatureCollection([
            pico.Feature(pico.Point((1, 2)),
                                properties={"desc": "a point"}),
            pico.Feature(pico.MultiPolygon([
                                    [[(1, 2), (2, 3), (1, 3), (1, 2)]],
                                    [[(1, 2), (-2, -3), (-1, -3), (1, 2)]]]),
                                properties={"desc": "some triangles"})
            ], crs=DEFAULTCRS)))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].crs, DEFAULTCRS)

if __name__ == "__main__":
    unittest.main()
