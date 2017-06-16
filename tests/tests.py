import unittest
import os
import json

import sys
if sys.version_info.major >= 3:
    from io import StringIO
else:
    from StringIO import StringIO

import picogeojson
from picogeojson import Serializer, Deserializer, merge, burst, DEFAULTCRS
import picogeojson.bbox as bbox
from picogeojson.geojson import fixed_precision
from picogeojson.result import GeoJSONResult

from result_tests import ResultTests

TESTDATA = "tests/"

class DeserializerTests(unittest.TestCase):

    def setUp(self):
        self.deserializer = Deserializer()
        return

    def test_shorthand(self):
        res = picogeojson.fromfile(os.path.join(TESTDATA, 'point.json'))
        self.assertEqual(res.coordinates, [100.0, 0.0])
        return

    def test_shorthand_result(self):
        res = picogeojson.result_fromfile(os.path.join(TESTDATA, 'point.json'))
        self.assertEqual(type(res), GeoJSONResult)
        for pt in res.points:
            self.assertEqual(pt.coordinates, [100.0, 0.0])
        return

    def test_shorthand_string(self):
        with open(os.path.join(TESTDATA, 'point.json'), 'r') as f:
            string = f.read()
        res = picogeojson.fromstring(string)
        self.assertEqual(res.coordinates, [100.0, 0.0])
        return

    def test_shorthand_string_compat(self):
        with open(os.path.join(TESTDATA, 'point.json'), 'r') as f:
            string = f.read()
        res = picogeojson.loads(string)
        self.assertEqual(res.coordinates, [100.0, 0.0])
        return

    def test_shorthand_string_result(self):
        with open(os.path.join(TESTDATA, 'point.json'), 'r') as f:
            string = f.read()
        res = picogeojson.result_fromstring(string)
        self.assertEqual(type(res), GeoJSONResult)
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
             [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2]]]])
        return

    def test_geometrycollection_read(self):
        res = self.deserializer.fromfile(os.path.join(TESTDATA, 'geometrycollection.json'))
        self.assertEqual(len(res.geometries), 2)
        self.assertTrue(isinstance(res.geometries[0], picogeojson.Point))
        self.assertTrue(isinstance(res.geometries[1], picogeojson.LineString))
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
        self.assertTrue(isinstance(fc.features[0].geometry, picogeojson.Point))
        self.assertEqual(fc.features[0].geometry.coordinates, [102.0, 0.5])
        self.assertEqual(fc.features[0].properties, {"prop0": "value0"})

        self.assertTrue(isinstance(fc.features[1].geometry, picogeojson.LineString))
        self.assertEqual(fc.features[1].geometry.coordinates,
                        [[102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]])
        self.assertEqual(fc.features[1].properties,
                        {"prop0": "value0", "prop1": 0.0})

        self.assertTrue(isinstance(fc.features[2].geometry, picogeojson.Polygon))
        self.assertEqual(fc.features[2].geometry.coordinates,
                        [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0],
                          [100.0, 1.0], [100.0, 0.0]]])
        self.assertEqual(fc.features[2].properties,
                        {"prop0": "value0", "prop1": {"this": "that"}})
        return

class SerializerTests(unittest.TestCase):

    def setUp(self):
        self.serializer = Serializer()
        return

    def test_shorthand(self):
        pt = picogeojson.Point((44.0, 17.0), DEFAULTCRS)
        d = json.loads(picogeojson.tostring(pt))
        self.assertEqual(tuple(pt.coordinates), tuple(d["coordinates"]))
        self.assertEqual(pt.crs, d["crs"])

    def test_shorthand_file(self):
        pt = picogeojson.Point((44.0, 17.0), DEFAULTCRS)
        f = StringIO()
        picogeojson.tofile(pt, f)
        f.seek(0)
        pt2 = picogeojson.fromfile(f)
        f.close()
        self.assertEqual(tuple(pt.coordinates), tuple(pt2.coordinates))
        self.assertEqual(pt.crs, pt2.crs)

    def test_shorthand_compat(self):
        pt = picogeojson.Point((44.0, 17.0), DEFAULTCRS)
        d = json.loads(picogeojson.dumps(pt))
        self.assertEqual(tuple(pt.coordinates), tuple(d["coordinates"]))

    def test_serialize_point(self):
        pt = picogeojson.Point((44.0, 17.0), DEFAULTCRS)
        s = self.serializer(pt)
        d = json.loads(s)
        self.assertEqual(tuple(pt.coordinates), tuple(d["coordinates"]))
        return

    def test_serialize_linestring(self):
        linestring = picogeojson.LineString([[44.0, 17.0], [43.0, 17.5], [-2.1, 4.0]],
                                        DEFAULTCRS)
        s = self.serializer(linestring)
        d = json.loads(s)
        self.assertEqual(list(linestring.coordinates), list(d["coordinates"]))
        return

    def test_serialize_polygon_open(self):
        serializer = Serializer()
        with self.assertRaises(ValueError):
            polygon = picogeojson.Polygon([[(0, 0), (0, 1), (1, 1), (1, 0)]])
            s = serializer(polygon)
        return

    def test_serialize_polygon_reverse(self):
        # serializer may be used to enforce the RFC7946 requirement for CCW
        # external rings
        #
        # this test creates a backwards Polygon, and checks that the serializer
        # roverses it when told to do so, but not otherwise
        serializer = Serializer(enforce_poly_winding=True)
        polygon = picogeojson.Polygon([[(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]])
        s = serializer(polygon)
        d_ccw = json.loads(s)

        serializer = Serializer(enforce_poly_winding=False)
        polygon = picogeojson.Polygon([[(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]])
        s = serializer(polygon)
        d_cw = json.loads(s)

        self.assertEqual(d_ccw["coordinates"][0], d_cw["coordinates"][0][::-1])
        return

    def test_serialize_polygon(self):
        polygon = picogeojson.Polygon([[[44.0, 17.0], [43.0, 17.5], [-2.1, 4.0], [44.0, 17.0]],
                                       [[1.0, 1.0], [0.8, -0.7], [0.5, -0.5], [1.0, 1.0]]],
                                      DEFAULTCRS)
        s = self.serializer(polygon)
        d = json.loads(s)

        self.assertEqual(list(polygon.coordinates), list(d["coordinates"]))
        return

    def test_serialize_polygon_antimeridian(self):
        polygon = picogeojson.Polygon([[(172, -20), (-179, -20), (-177, -25),
                                (172, -25), (172, -20)]])
        s = self.serializer(polygon)
        d = json.loads(s)
        self.assertEqual(d["type"], "MultiPolygon")
        return

    def test_serialize_multipoint(self):
        multipoint = picogeojson.MultiPoint([[44.0, 17.0], [43.0, 17.5], [-2.1, 4.0]],
                                        DEFAULTCRS)
        s = self.serializer(multipoint)
        d = json.loads(s)
        self.assertEqual(list(multipoint.coordinates), list(d["coordinates"]))
        return

    def test_serialize_multilinestring(self):
        multilinestring = picogeojson.MultiLineString(
                            [[[44.0, 17.0], [43.0, 17.5], [-2.1, 4.0]],
                             [[49.0, -3.0], [48.0, -2.5], [2.9, -16.0]]],
                            DEFAULTCRS)
        s = self.serializer(multilinestring)
        d = json.loads(s)
        self.assertEqual(list(multilinestring.coordinates), list(d["coordinates"]))
        return

    def test_serialize_multipolygon(self):
        multipolygon = picogeojson.MultiPolygon(
                            [[[[44.0, 17.0], [43.0, 17.5], [-2.1, 4.0], [44.0, 17.0]],
                              [[1.0, 1.0], [0.8, -0.7], [0.5, -0.5], [1.0, 1.0]]],
                             [[[49.0, -3.0], [48.0, -2.5], [2.9, -16.0], [49.0, -3.0]]]],
                            DEFAULTCRS)
        s = self.serializer(multipolygon)
        d = json.loads(s)
        self.assertEqual(list(multipolygon.coordinates), list(d["coordinates"]))
        return

    def test_serialize_multipolygon_reverse(self):
        multipolygon = picogeojson.MultiPolygon(
                            [[[[0.0, 0.0], [2.0, 0.0], [1, 2.0], [0.0, 0.0]]],
                             [[[0.0, 0.0], [-2.0, 0.0], [-1.0, 2.0], [0.0, 0.0]]]],
                            DEFAULTCRS)

        serializer = Serializer(enforce_poly_winding=True)
        s = serializer(multipolygon)
        d_ccw = json.loads(s)

        serializer = Serializer(enforce_poly_winding=False)
        s = serializer(multipolygon)
        d_cw = json.loads(s)

        self.assertEqual(d_cw["coordinates"][1][0], d_ccw["coordinates"][1][0][::-1])
        return

    def test_serialize_geometrycollection(self):
        collection = picogeojson.GeometryCollection(
                            [picogeojson.Point((3, 4), None),
                             picogeojson.Point((5, 6), None),
                             picogeojson.LineString([(1, 2), (3, 4), (3, 2)], None)],
                            DEFAULTCRS)
        s = self.serializer(collection)
        d = json.loads(s)
        self.assertEqual(len(d.get("geometries", [])), 3)
        self.assertEqual(d.get("crs", ""), DEFAULTCRS)
        return

    def test_top_bbox_only_geometry_collection(self):
        collection = picogeojson.GeometryCollection(
                            [picogeojson.Point((3, 4), None),
                             picogeojson.Polygon([[(5, 6), (7, 8), (9, 10), (5, 6)]], None),
                             picogeojson.LineString([(1, 2), (3, 4), (3, 2)], None)],
                            DEFAULTCRS)
        s = self.serializer(collection)
        d = json.loads(s)
        self.assertFalse(d["geometries"][1].get("bbox", False))
        self.assertFalse(d["geometries"][2].get("bbox", False))
        self.assertTrue(d.get("bbox", False) is not False)

    def test_top_bbox_only_feature_collection(self):
        collection = picogeojson.FeatureCollection(
                [picogeojson.Feature(picogeojson.Point((7,3), None), {"type": "city"}, None, None),
                 picogeojson.Feature(picogeojson.LineString([(1,2), (1,3), (2, 2)], None),
                             {"type": "river"}, None, None),
                 picogeojson.Feature(picogeojson.Polygon([[(1,2), (1,3), (2, 2), (1, 2)]], None),
                             {"type": "boundary"}, None, None)],
                DEFAULTCRS)
        s = self.serializer(collection)
        d = json.loads(s)
        self.assertFalse(d["features"][1]["geometry"].get("bbox", False))
        self.assertFalse(d["features"][2]["geometry"].get("bbox", False))
        self.assertTrue(d.get("bbox", False) is not False)

    def test_serialize_feature(self):
        feature = picogeojson.Feature(picogeojson.Point((1,2), None), {"type": "city"}, 1, DEFAULTCRS)
        s = self.serializer(feature)
        d = json.loads(s)
        self.assertEqual(d.get("geometry", {}).get("type", ""), "Point")
        self.assertEqual(d.get("id", 0), 1)
        self.assertEqual(d.get("properties", {}).get("type", ""), "city")
        return

    def test_serialize_featurecollection(self):
        collection = picogeojson.FeatureCollection(
                [picogeojson.Feature(picogeojson.Point((7,3), None), {"type": "city"}, None, None),
                 picogeojson.Feature(picogeojson.LineString([(1,2), (1,3), (2, 2)], None),
                             {"type": "river"}, None, None),
                 picogeojson.Feature(picogeojson.Polygon([[(1,2), (1,3), (2, 2), (2, 1), (1,2)]], None),
                             {"type": "boundary"}, None, None)],
                DEFAULTCRS)
        s = self.serializer(collection)
        d = json.loads(s)
        self.assertEqual(len(d.get("features", [])), 3)
        self.assertEqual(d.get("crs", ""), DEFAULTCRS)
        return

    def test_dedup_crs_geometrycollection(self):
        crs = {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}
        collection = picogeojson.GeometryCollection(
                [picogeojson.Point((1, 2), crs=crs)],
                crs=crs)
        s = self.serializer(collection)
        self.assertEqual(s.count('"crs"'), 1)

    def test_dedup_crs_feature(self):
        crs = {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}
        feature = picogeojson.Feature(picogeojson.Point((1, 2), crs=crs),
                                      {"type": "tree"}, id=1, crs=crs)
        s = self.serializer(feature)
        self.assertEqual(s.count('"crs"'), 1)

    def test_dedup_crs_feature_collection(self):
        crs = {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}
        coll = picogeojson.FeatureCollection(
                    [picogeojson.Feature(picogeojson.Point((1, 2), crs=crs),
                                         {"type": "tree"}, id=1, crs=crs),
                     picogeojson.Feature(picogeojson.LineString([(1, 2), (2, 3)], crs=crs),
                                         {"type": "fence"}, id=2, crs=crs),
                     picogeojson.Feature(picogeojson.Point((5, 4), crs=crs),
                                         {"type": "pothole"}, id=3, crs=crs)],
                    crs=crs)
        s = self.serializer(coll)
        self.assertEqual(s.count('"crs"'), 1)


class AntimerdianTests(unittest.TestCase):

    def test_contains(self):
        self.assertFalse(picogeojson.antimeridian.contains(
            [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)],
            [(2, 0), (2, 1), (3, 1), (3, 0), (2, 0)]))

        self.assertTrue(picogeojson.antimeridian.contains(
            [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)],
            [(1, 1), (1, 3), (3, 3), (3, 1), (1, 1)]))
        return

    def test_linestring_split(self):
        res = picogeojson.antimeridian.antimeridian_cut(
                picogeojson.LineString([(172, 34), (178, 36), (-179, 37), (-177, 39)])
                )
        self.assertTrue(isinstance(res, picogeojson.MultiLineString))
        self.assertEqual(len(res.coordinates), 2)
        self.assertEqual(res.coordinates[0][-1], (180, 36.33333333))
        self.assertEqual(res.coordinates[1][0], (-179.99999999, 36.33333333))

    def test_polygon_split(self):
        res = picogeojson.antimeridian.antimeridian_cut(
                picogeojson.Polygon([[(172, -20), (-179, -20), (-177, -25), (172, -25), (172, -20)]])
                )
        self.assertTrue(isinstance(res, picogeojson.MultiPolygon))
        self.assertEqual(len(res.coordinates), 2)

    def test_polygon_split_holes(self):
        res = picogeojson.antimeridian.antimeridian_cut(
                picogeojson.Polygon([[(172, -20), (-179, -20), (-177, -25), (172, -25), (172, -20)],
                             [(174, -22), (-179, -22), (-179, -23), (174, -22)]])
                )
        self.assertTrue(isinstance(res, picogeojson.MultiPolygon))
        self.assertEqual(len(res.coordinates), 2)
        self.assertEqual(len(res.coordinates[0]), 2)
        self.assertEqual(len(res.coordinates[1]), 2)

    def test_multilinestring_split(self):
        res = picogeojson.antimeridian.antimeridian_cut(
                picogeojson.MultiLineString(
                            [[(172, 34), (178, 36), (-179, 37), (-177, 39)],
                             [(172, -34), (178, -36), (-179, -37), (-177, -39)]])
                )
        self.assertEqual(len(res.coordinates), 4)

    def test_featurecollection_split(self):
        res = picogeojson.antimeridian.antimeridian_cut(
                picogeojson.FeatureCollection([
                    picogeojson.Feature(
                        picogeojson.LineString([(172, 34), (178, 36), (-179, 37), (-177, 39)]),
                        {"desc": "a linestring spanning the dateline"}),
                    picogeojson.Feature(
                        picogeojson.Point((1,2)),
                        {"desc": "a single point"}),
                    picogeojson.Feature(
                        picogeojson.GeometryCollection([
                            picogeojson.Polygon([[(178, 3), (-178, 5), (-178, 7), (178, 5)]]),
                            picogeojson.LineString([(172, -34), (178, -36), (-179, -37), (-177, -39)])]),
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
        self.assertTrue(picogeojson.orientation.is_counterclockwise(
            [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]))

        self.assertFalse(picogeojson.orientation.is_counterclockwise(
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

    def test_point_bbox_2(self):
        p = picogeojson.Point((2, 3))
        bbx = bbox.geom_bbox(p)
        self.assertEqual(bbx, [2, 3, 2, 3])

    def test_point_bbox_3(self):
        p = picogeojson.Point((2, 3, 1))
        bbx = bbox.geom_bbox(p)
        self.assertEqual(bbx, [2, 3, 1, 2, 3, 1])

    def test_geometrycollection_bbox_2(self):
        collection = picogeojson.GeometryCollection(
                            [picogeojson.Point((3, 4), None),
                             picogeojson.Point((5, 6), None),
                             picogeojson.LineString([(1, 2), (3, 4), (3, 2)], None)],
                            DEFAULTCRS)
        bbx = bbox.geom_bbox(collection)
        self.assertEqual(bbx, [1, 2, 5, 6])

    def test_geometrycollection_bbox_3(self):
        collection = picogeojson.GeometryCollection(
                            [picogeojson.Point((3, 4, 1), None),
                             picogeojson.Point((5, 6, 2), None),
                             picogeojson.LineString([(1, 2, 2), (3, 4, 5), (3, 2, 3)], None)],
                            DEFAULTCRS)
        bbx = bbox.geom_bbox(collection)
        self.assertEqual(bbx, [1, 2, 1, 5, 6, 5])

    def test_feature_bbox_2(self):
        feature = picogeojson.Feature(
                    picogeojson.LineString([(1,2), (1,3), (2, 2)], None),
                    {"type": "river"}, None, None)
        bbx = bbox.feature_bbox(feature)
        self.assertEqual(bbx, [1, 2, 2, 3])

    def test_feature_bbox_3(self):
        feature = picogeojson.Feature(
                    picogeojson.LineString([(1, 2, 1), (1, 3, 0.5), (2, 2, 0)], None),
                    {"type": "river"}, None, None)
        bbx = bbox.feature_bbox(feature)
        self.assertEqual(bbx, [1, 2, 0, 2, 3, 1])

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

    def test_merge_points(self):
        pts = [picogeojson.Point((1, 2)),
               picogeojson.Point((3, 4)),
               picogeojson.Point((5, 6)),
               picogeojson.Point((7, 8))]
        merged = merge(pts)
        self.assertEqual(type(merged).__name__, "MultiPoint")
        self.assertEqual(len(merged.coordinates), 4)

    def test_merge_linestrings(self):
        lns = [picogeojson.LineString([(1, 2), (2, 2), (1, 1), (-1, 2)]),
               picogeojson.LineString([(3, 4), (3, 4), (3, 2), (-3, 4)]),
               picogeojson.LineString([(5, 6), (4, 6), (5, 3), (-5, 6)]),
               picogeojson.LineString([(7, 8), (5, 8), (7, 4), (-7, 8)])]
        merged = merge(lns)
        self.assertEqual(type(merged).__name__, "MultiLineString")
        self.assertEqual(len(merged.coordinates), 4)

    def test_merge_polygons(self):
        plg = [picogeojson.Polygon([[(1, 2), (2, 2), (1, 1), (-1, 2)]]),
               picogeojson.Polygon([[(3, 4), (3, 4), (3, 2), (-3, 4)]]),
               picogeojson.Polygon([[(5, 6), (4, 6), (5, 3), (-5, 6)]]),
               picogeojson.Polygon([[(7, 8), (5, 8), (7, 4), (-7, 8)]])]
        merged = merge(plg)
        self.assertEqual(type(merged).__name__, "MultiPolygon")
        self.assertEqual(len(merged.coordinates), 4)

    def test_merge_geometrycollections(self):
        gcs = [picogeojson.GeometryCollection([
                    picogeojson.Point((1, 2)),
                    picogeojson.LineString([(2, 2), (1, 1), (-1, 2)])]),
               picogeojson.GeometryCollection([
                    picogeojson.MultiPoint([(7, 8), (5, 8), (7, 4), (-7, 8)]),
                    picogeojson.Point((9, 8))])
               ]
        merged = merge(gcs)
        self.assertEqual(type(merged).__name__, "GeometryCollection")
        self.assertEqual(len(merged.geometries), 2)

    def test_merge_geometries(self):
        gms = [picogeojson.LineString([(1, 2), (2, 2), (1, 1), (-1, 2)]),
               picogeojson.Point((3, 4)),
               picogeojson.Polygon([[(5, 6), (4, 6), (2, 5), (5, 5)]])]
        merged = merge(gms)
        self.assertEqual(type(merged).__name__, "GeometryCollection")
        self.assertEqual(len(merged.geometries), 3)

    def test_merge_features(self):
        gms = [picogeojson.Feature(
                    picogeojson.LineString([(1, 2), (2, 2), (1, 1), (-1, 2)]),
                    {"desc": "single linestring"}
                    ),
               picogeojson.Feature(picogeojson.Point((3, 4)),
                   {"desc": "single point"}),
               picogeojson.Feature(picogeojson.GeometryCollection(
                   [picogeojson.LineString([(1, 2), (2, 3), (1, 4)]),
                    picogeojson.Point((-2, -3))]),
                   {"desc": "collection of geometries"}),
               picogeojson.Feature(picogeojson.Polygon([[(5, 6), (4, 6), (2, 5), (5, 5)]]),
                   {"desc": "single polygon"})]
        merged = merge(gms)
        self.assertEqual(type(merged).__name__, "FeatureCollection")
        self.assertEqual(len(merged.features), 4)

    def test_merge_features_featurecollections(self):
        gms = [picogeojson.Feature(
                    picogeojson.LineString([(1, 2), (2, 2), (1, 1), (-1, 2)]),
                    {"desc": "single linestring"}
                    ),
               picogeojson.FeatureCollection(
                   [picogeojson.Feature(picogeojson.Point((3, 4)),
                       {"desc": "single point"}),
                    picogeojson.Feature(picogeojson.GeometryCollection(
                       [picogeojson.LineString([(1, 2), (2, 3), (1, 4)]),
                        picogeojson.Point((-2, -3))]),
                       {"desc": "collection of geometries"})]
                    ),
               picogeojson.Feature(picogeojson.Polygon([[(5, 6), (4, 6), (2, 5), (5, 5)]]),
                   {"desc": "single polygon"})]
        merged = merge(gms)
        self.assertEqual(type(merged).__name__, "FeatureCollection")
        self.assertEqual(len(merged.features), 4)

    def test_merge_featurecollections(self):
        fcs = [picogeojson.FeatureCollection([
                   picogeojson.Feature(
                        picogeojson.LineString([(1, 2), (2, 2), (1, 1), (-1, 2)]),
                        {"desc": "single linestring"}),
                   picogeojson.Feature(
                        picogeojson.LineString([(0, 2), (1, -1), (1, 0), (-1, 3)]),
                        {"desc": "another linestring"})]),
               picogeojson.FeatureCollection(
                   [picogeojson.Feature(picogeojson.Point((3, 4)),
                       {"desc": "single point"}),
                    picogeojson.Feature(picogeojson.GeometryCollection(
                       [picogeojson.LineString([(1, 2), (2, 3), (1, 4)]),
                        picogeojson.Point((-2, -3))]),
                       {"desc": "collection of geometries"})])]
        merged = merge(fcs)
        self.assertEqual(type(merged).__name__, "FeatureCollection")
        self.assertEqual(len(merged.features), 4)

    def test_burst_multipoint(self):
        result = burst(picogeojson.MultiPoint([(1, 2), (3, 4), (5, 6)]))
        self.assertEqual(len(result), 3)
        self.assertEqual(type(result[0]).__name__, "Point")
        self.assertEqual(type(result[1]).__name__, "Point")
        self.assertEqual(type(result[2]).__name__, "Point")

    def test_burst_point(self):
        result = burst(picogeojson.Point((1, 2)))
        self.assertEqual(len(result), 1)
        self.assertEqual(type(result[0]).__name__, "Point")

    def test_burst_geometrycollection(self):
        result = burst(picogeojson.GeometryCollection([
            picogeojson.Point(1, 2),
            picogeojson.LineString([(3, 4), (5, 6), (7, 6)]),
            picogeojson.Polygon([[(1, 1), (2, 2), (2, 3), (1, 2)]]),
            picogeojson.MultiLineString([[(0, 0), (0, 1), (1, 1)],
                                         [(0, 0), (1, 0), (1, 1)]])
            ], crs=DEFAULTCRS))
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0].crs, DEFAULTCRS)

    def test_burst_multipolygon(self):
        result = burst(picogeojson.MultiPolygon([
                                    [[(1, 2), (2, 3), (1, 3)]],
                                    [[(1, 2), (-2, -3), (-1, -3)]]],
                                    crs=DEFAULTCRS))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].crs, DEFAULTCRS)

    def test_burst_feature_collection(self):
        result = burst(picogeojson.FeatureCollection([
            picogeojson.Feature(picogeojson.Point((1, 2)),
                                properties={"desc": "a point"}),
            picogeojson.Feature(picogeojson.MultiPolygon([
                                    [[(1, 2), (2, 3), (1, 3)]],
                                    [[(1, 2), (-2, -3), (-1, -3)]]]),
                                properties={"desc": "some triangles"})
            ], crs=DEFAULTCRS))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].crs, DEFAULTCRS)

if __name__ == "__main__":
    unittest.main()
