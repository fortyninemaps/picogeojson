__version__ = "0.3.1"

from .types import (Point, LineString, Polygon,
                    MultiPoint, MultiLineString, MultiPolygon,
                    GeometryCollection, Feature, FeatureCollection,
                    merge)

from .geojson import (Serializer, Deserializer,
                      DEFAULTCRS,
                      fromfile, fromstring, tostring, loads, dumps)

from . import antimeridian
from . import orientation
