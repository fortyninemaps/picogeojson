__version__ = "0.7.0.dev1"

from .types import (Point, LineString, Polygon,
                    MultiPoint, MultiLineString, MultiPolygon,
                    GeometryCollection, Feature, FeatureCollection,
                    merge, burst)

from .geojson import (Serializer, Deserializer,
                      DEFAULTCRS,
                      fromfile, fromstring, fromdict, tofile, tostring, todict,
                      load, dump, loads, dumps,
                      result_fromstring, result_fromfile)

from . import antimeridian
from . import orientation
