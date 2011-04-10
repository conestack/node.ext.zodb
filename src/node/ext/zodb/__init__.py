from plumber import (
    plumber,
    Part,
    default,
    extend,
)
from zope.interface import implements
from odict.pyodict import _odict
from persistent import Persistent
from persistent.dict import PersistentDict
from BTrees.OOBTree import OOBTree
from node.interfaces import IStorage
from node.parts import (
    Adopt,
    Nodespaces,
    Attributes,
    Order,
    AsAttrAccess,
    DefaultInit,
    Nodify,
    NodeChildValidate,
)

#class Podict(_odict, OOBTree):
#    
#    def _dict_impl(self):
#        return OOBTree


class Podict(_odict, PersistentDict):
    
    def _dict_impl(self):
        return PersistentDict


class PodictStorage(Part):
    implements(IStorage)
    
    @default
    @property
    def storage(self):
        if not hasattr(self, '_storage_data'):
            self._storage_data = Podict()
        return self._storage_data
    
    @extend
    def __getitem__(self, key):
        return self.storage[key]
    
    @extend
    def __delitem__(self, key):
        del self.storage[key]
    
    @extend
    def __setitem__(self, key, val):
        self.storage[key] = val
    
    @extend
    def __iter__(self):
        return self.storage.__iter__()


class ZODBNode(Persistent):
    __metaclass__ = plumber
    __plumbing__ = (
        NodeChildValidate,
        Nodespaces,
        Adopt,
        Attributes,
        Order,
        AsAttrAccess,
        DefaultInit,
        Nodify,
        PodictStorage,
    )
    
    def _get_parent(self):
        return self._v_parent
    
    def _set_parent(self, val):
        self._v_parent = val
    
    __parent__ = property(_get_parent, _set_parent)
    
    def __getitem__(self, key):
        val = self.storage[key]
        val.__parent__ = self
        return val