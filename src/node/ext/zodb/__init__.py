from plumber import (
    plumber,
    Part,
    default,
    extend,
)
from zope.interface import implements
from odict.pyodict import _odict
from persistent.dict import PersistentDict
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

#class Podict__(OOBtree):
#    """"""
    # XXX: implement missing dict behavior and use as dict impl instead of
    #      persistentdict


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
    
    @extend
    def keys(self):
        """XXX: bug with nodify
        """
        return self.storage.keys()
    
    @extend
    def values(self):
        """XXX: bug with nodify
        """
        return self.storage.values()


class ZODBNode(Podict):
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