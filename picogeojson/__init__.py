__version__ = "0.4.0"

from .types import (Point, LineString, Polygon,
                    MultiPoint, MultiLineString, MultiPolygon,
                    GeometryCollection, Feature, FeatureCollection,
                    merge, burst)

from .geojson import (Serializer, Deserializer,
                      DEFAULTCRS,
                      fromfile, fromstring, tostring, loads, dumps)

from . import antimeridian
from . import orientation
