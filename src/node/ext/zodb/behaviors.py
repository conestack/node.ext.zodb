import copy
from plumber import (
    Part,
    default,
    extend,
    finalize,
    plumb,
)
from persistent import Persistent
from zope.interface import implementer
from node.interfaces import (
    INode,
    IAttributes,
    IOrdered,
)
from node.behaviors import Storage
from node.utils import (
    AttributeAccess,
    instance_property,
)
from node.ext.zodb.interfaces import IZODBNode
from node.ext.zodb.utils import (
    Podict,
    OOBTodict,
)


@implementer(IZODBNode)
class ZODBPart(Part):
    """This part requires plumbed class to inherit from Persistent.
    """
    
    @extend
    @property
    def __parent__(self):
        """Always expect _v_parent to be set, see __setattr__ and
        __getitem__.
        """
        return self._v_parent
    
    @extend
    def __getitem__(self, key):
        v = self.storage[key]
        if INode.providedBy(v):
            v._v_parent = self
        return v
    
    @extend
    def __setattr__(self, name, value):
        """If name is __parent__, write value to _v_parent. This avoids
        _p_changed to be set set by Persitent.__setattr__. Using a read/write
        property for __parent__ won't work.
        """
        if name == '__parent__':
            name = '_v_parent'
        Persistent.__setattr__(self, name, value)
    
    @default
    def __call__(self):
        """Meant to be plumbed if something should happen in a particular
        subclass on __call__. Persisting is left to the ZODB transaction
        mechanism.
        """
        pass
    
    @plumb
    def __setitem__(_next, self, key, value):
        _next(self, key, value)
        self.storage._p_changed = 1
    
    @finalize
    def copy(self):
        return copy.deepcopy(self)


@implementer(IOrdered)
class PodictStorage(ZODBPart, Storage):
    
    @default
    @instance_property
    def storage(self):
        return Podict()


@implementer(IOrdered)
class OOBTodictStorage(ZODBPart, Storage):
    
    @default
    @instance_property
    def storage(self):
        return OOBTodict()


@implementer(IAttributes)
class ZODBAttributes(Part):
    attribute_access_for_attrs = default(False)
    attributes_factory = default(None)

    @finalize
    @property
    def attrs(self):
        try:
            attrs = self._attrs
        except AttributeError:
            self._attrs = attrs = self.attributes_factory(name='_attrs',
                                                          parent=self)
        if self.attribute_access_for_attrs:
            return AttributeAccess(attrs)
        return attrs