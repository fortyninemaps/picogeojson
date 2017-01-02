__version__ = "0.2.0"

from .types import (Point, LineString, Polygon,
                    MultiPoint, MultiLineString, MultiPolygon,
                    GeometryCollection, Feature, FeatureCollection)

from .geojson import Serializer, Deserializer, DEFAULTCRS
from . import antimeridian
from . import orientation
