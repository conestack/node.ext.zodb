from node.behaviors import MappingAdopt
from node.behaviors import AsAttrAccess
from node.behaviors import DefaultInit
from node.behaviors import MappingConstraints
from node.behaviors import MappingNode
from node.behaviors import Order
from node.ext.zodb.behaviors import OOBTodictStorage
from node.ext.zodb.behaviors import PodictStorage
from node.ext.zodb.behaviors import ZODBAttributes
from node.ext.zodb.behaviors import ZODBBehavior  # noqa
from node.ext.zodb.interfaces import IZODBNode  # noqa
from node.ext.zodb.utils import OOBTodict  # noqa
from node.ext.zodb.utils import Podict  # noqa
from node.ext.zodb.utils import volatile_property  # noqa
from persistent import Persistent
from plumber import plumbing


@plumbing(
    MappingConstraints,
    MappingAdopt,
    DefaultInit,
    MappingNode,
    PodictStorage)
class ZODBNodeAttributes(Persistent):
    child_constraints = None


@plumbing(
    MappingConstraints,
    MappingAdopt,
    Order,
    AsAttrAccess,
    DefaultInit,
    MappingNode,
    ZODBAttributes,
    PodictStorage)
class ZODBNode(Persistent):
    attributes_factory = ZODBNodeAttributes


@plumbing(
    MappingConstraints,
    MappingAdopt,
    DefaultInit,
    MappingNode,
    OOBTodictStorage)
class OOBTNodeAttributes(Persistent):
    child_constraints = None


@plumbing(
    MappingConstraints,
    MappingAdopt,
    Order,
    AsAttrAccess,
    DefaultInit,
    MappingNode,
    ZODBAttributes,
    OOBTodictStorage)
class OOBTNode(Persistent):
    attributes_factory = OOBTNodeAttributes
