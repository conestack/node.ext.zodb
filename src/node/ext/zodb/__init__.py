from node.behaviors import Adopt
from node.behaviors import AsAttrAccess
from node.behaviors import DefaultInit
from node.behaviors import NodeChildValidate
from node.behaviors import Nodify
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
    NodeChildValidate,
    Adopt,
    DefaultInit,
    Nodify,
    PodictStorage)
class ZODBNodeAttributes(Persistent):
    allow_non_node_children = True


@plumbing(
    NodeChildValidate,
    Adopt,
    Order,
    AsAttrAccess,
    DefaultInit,
    Nodify,
    ZODBAttributes,
    PodictStorage)
class ZODBNode(Persistent):
    attributes_factory = ZODBNodeAttributes


@plumbing(
    NodeChildValidate,
    Adopt,
    DefaultInit,
    Nodify,
    OOBTodictStorage)
class OOBTNodeAttributes(Persistent):
    allow_non_node_children = True


@plumbing(
    NodeChildValidate,
    Adopt,
    Order,
    AsAttrAccess,
    DefaultInit,
    Nodify,
    ZODBAttributes,
    OOBTodictStorage)
class OOBTNode(Persistent):
    attributes_factory = OOBTNodeAttributes
