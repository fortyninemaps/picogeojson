__version__ = "0.2.1"

from .types import (Point, LineString, Polygon,
                    MultiPoint, MultiLineString, MultiPolygon,
                    GeometryCollection, Feature, FeatureCollection)

from .geojson import (Serializer, Deserializer,
                      DEFAULTCRS,
                      fromfile, fromstring, tostring)

from . import antimeridian
from . import orientation
