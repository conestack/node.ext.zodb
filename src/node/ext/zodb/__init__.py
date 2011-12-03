from plumber import plumber
from persistent import Persistent
from node.parts import (
    Adopt,
    Order,
    AsAttrAccess,
    DefaultInit,
    Nodify,
    NodeChildValidate,
)
from node.ext.zodb.interfaces import IZODBNode
from node.ext.zodb.parts import (
    ZODBPart,
    PodictStorage,
    OOBTodictStorage,
    ZODBAttributes,
)
from node.ext.zodb.utils import (
    Podict,
    OOBTodict,
    volatile_property,
)


attribute_parts = (
    NodeChildValidate, Adopt, DefaultInit, Nodify
)
node_parts = (
    NodeChildValidate, Adopt, Order, AsAttrAccess,
    DefaultInit, Nodify, ZODBAttributes
)


class ZODBNodeAttributes(Persistent):
    __metaclass__ = plumber
    __plumbing__ = attribute_parts + (PodictStorage,)
    allow_non_node_childs = True


class ZODBNode(Persistent):
    __metaclass__ = plumber
    __plumbing__ = node_parts + (PodictStorage,)
    attributes_factory = ZODBNodeAttributes


class OOBTNodeAttributes(Persistent):
    __metaclass__ = plumber
    __plumbing__ = attribute_parts + (OOBTodictStorage,)
    allow_non_node_childs = True


class OOBTNode(Persistent):
    __metaclass__ = plumber
    __plumbing__ = node_parts + (OOBTodictStorage,)
    attributes_factory = OOBTNodeAttributes