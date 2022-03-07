from node.behaviors import MappingStorage
from node.ext.zodb.interfaces import IZODBNode
from node.ext.zodb.utils import OOBTodict
from node.ext.zodb.utils import Podict
from node.interfaces import IAttributes
from node.interfaces import INode
from node.interfaces import IOrdered
from node.utils import AttributeAccess
from node.utils import instance_property
from plumber import Behavior
from plumber import default
from plumber import finalize
from plumber import override
from plumber import plumb
from zope.interface import implementer
import copy


@implementer(IZODBNode)
class ZODBBehavior(Behavior):
    """This behavior requires plumbed class to inherit from ``Persistent``.
    """

    @override
    @property
    def __parent__(self):
        return self._v_parent

    @default
    def __call__(self):
        """Supposed to be plumbed if something should happen in a particular
        subclass on ``__call__``. Persisting is left to the ZODB transaction
        mechanism.
        """
        pass

    @finalize
    def copy(self):
        return copy.deepcopy(self)

    @plumb
    def __setattr__(_next, self, name, value):
        # adding a setter property for __parent__ not works, _p_changed gets
        # set anyway as soon as settings the attribute. replace name instead to
        # _v_parent
        if name == '__parent__':
            name = '_v_parent'
        _next(self, name, value)

    @plumb
    def __setitem__(_next, self, key, value):
        _next(self, key, value)
        self.storage._p_changed = 1

    @plumb
    def __getitem__(_next, self, key):
        v = _next(self, key)
        if INode.providedBy(v):
            v._v_parent = self
        return v


@implementer(IOrdered)
class PodictStorage(ZODBBehavior, MappingStorage):

    @plumb
    def __init__(next_, self, *a, **kw):
        next_(self, *a, **kw)
        storage = self.storage
        storage.lh
        storage.lt

    @default
    @instance_property
    def storage(self):
        return Podict()


@implementer(IOrdered)
class OOBTodictStorage(ZODBBehavior, MappingStorage):

    @plumb
    def __init__(next_, self, *a, **kw):
        next_(self, *a, **kw)
        storage = self.storage
        storage.lh
        storage.lt

    @default
    @instance_property
    def storage(self):
        return OOBTodict()


@implementer(IAttributes)
class ZODBAttributes(Behavior):
    attribute_access_for_attrs = default(False)
    attributes_factory = default(None)

    @plumb
    def __init__(next_, self, *a, **kw):
        next_(self, *a, **kw)
        self.attrs

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
