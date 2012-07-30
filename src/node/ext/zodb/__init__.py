from plumber import plumber
from persistent import Persistent
from node.behaviors import (
    Adopt,
    Order,
    AsAttrAccess,
    DefaultInit,
    Nodify,
    NodeChildValidate,
)
from node.ext.zodb.interfaces import IZODBNode
from node.ext.zodb.behaviors import (
    ZODBBehavior,
    PodictStorage,
    OOBTodictStorage,
    ZODBAttributes,
)
from node.ext.zodb.utils import (
    Podict,
    OOBTodict,
    volatile_property,
)


ZODB_ATTRIBUTE_PARTS = (
    NodeChildValidate, Adopt, DefaultInit, Nodify
)
ZODB_NODE_PARTS = (
    NodeChildValidate, Adopt, Order, AsAttrAccess,
    DefaultInit, Nodify, ZODBAttributes
)


class ZODBNodeAttributes(Persistent):
    __metaclass__ = plumber
    __plumbing__ = ZODB_ATTRIBUTE_PARTS + (PodictStorage,)
    allow_non_node_childs = True


class ZODBNode(Persistent):
    __metaclass__ = plumber
    __plumbing__ = ZODB_NODE_PARTS + (PodictStorage,)
    attributes_factory = ZODBNodeAttributes


class OOBTNodeAttributes(Persistent):
    __metaclass__ = plumber
    __plumbing__ = ZODB_ATTRIBUTE_PARTS + (OOBTodictStorage,)
    allow_non_node_childs = True


class OOBTNode(Persistent):
    __metaclass__ = plumber
    __plumbing__ = ZODB_NODE_PARTS + (OOBTodictStorage,)
    attributes_factory = OOBTNodeAttributes