__version__ = "0.4.1"

from .types import (Point, LineString, Polygon,
                    MultiPoint, MultiLineString, MultiPolygon,
                    GeometryCollection, Feature, FeatureCollection,
                    merge, burst)

from .geojson import (Serializer, Deserializer,
                      DEFAULTCRS,
                      fromfile, fromstring, tostring, loads, dumps,
                      result_fromstring, result_fromfile)

from . import antimeridian
from . import orientation
