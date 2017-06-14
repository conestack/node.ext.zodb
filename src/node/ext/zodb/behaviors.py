from node.behaviors import Storage
from node.ext.zodb.interfaces import IZODBNode
from node.ext.zodb.utils import OOBTodict
from node.ext.zodb.utils import Podict
from node.interfaces import IAttributes
from node.interfaces import INode
from node.interfaces import IOrdered
from node.utils import AttributeAccess
from node.utils import instance_property
from persistent import Persistent
from plumber import Behavior
from plumber import default
from plumber import finalize
from plumber import override
from plumber import plumb
from zope.interface import implementer
import copy


@implementer(IZODBNode)
class ZODBBehavior(Behavior):
    """This part requires plumbed class to inherit from Persistent.
    """

    @override
    @property
    def __parent__(self):
        """Always expect _v_parent to be set, see __setattr__ and
        __getitem__.
        """
        return self._v_parent

    @override
    def __getitem__(self, key):
        v = self.storage[key]
        if INode.providedBy(v):
            v._v_parent = self
        return v

    @override
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
class PodictStorage(ZODBBehavior, Storage):

    @default
    @instance_property
    def storage(self):
        return Podict()


@implementer(IOrdered)
class OOBTodictStorage(ZODBBehavior, Storage):

    @default
    @instance_property
    def storage(self):
        return OOBTodict()


@implementer(IAttributes)
class ZODBAttributes(Behavior):
    attribute_access_for_attrs = default(False)
    attributes_factory = default(None)

    @finalize
    @property
    def attrs(self):
        try:
            attrs = self._attrs
        except AttributeError:
            self._attrs = attrs = self.attributes_factory(
                name='_attrs',
                parent=self
            )
        if self.attribute_access_for_attrs:
            return AttributeAccess(attrs)
        return attrs
