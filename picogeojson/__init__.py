__version__ = "0.1.1"

from .types import (Point, LineString, Polygon,
                    MultiPoint, MultiLineString, MultiPolygon,
                    GeometryCollection, Feature, FeatureCollection)

from .geojson import Serializer, Deserializer, DEFAULTCRS
from . import antimeridian
from . import orientation
