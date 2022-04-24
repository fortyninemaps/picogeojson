__version__ = "0.8.0"

from .types import (Point, LineString, Polygon,
                    MultiPoint, MultiLineString, MultiPolygon,
                    GeometryCollection, Feature, FeatureCollection)

from .map import Map

from .deserializer import Deserializer, fromfile, fromstring, fromdict

from .serializer import Serializer, tofile, tostring, todict

from .crs import DEFAULTCRS

from . import antimeridian
from . import orientation

from . import transformations

