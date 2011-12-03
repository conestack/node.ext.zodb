from odict.pyodict import (
    _odict,
    _nil,
)
from persistent.dict import PersistentDict
from BTrees.OOBTree import OOBTree


class Podict(_odict, PersistentDict):
    
    def _dict_impl(self):
        return PersistentDict


class OOBTodict(_odict, OOBTree):
    
    def _dict_impl(self):
        return OOBTree
    
    def _get_lh(self):
        try:
            return self['____lh']
        except KeyError:
            self['____lh'] = _nil
        return self['____lh']

    def _set_lh(self, val):
        self['____lh'] = val

    lh = property(_get_lh, _set_lh)

    def _get_lt(self):
        try:
            return self['____lt']
        except KeyError:
            self['____lt'] = _nil
        return self['____lt']

    def _set_lt(self, val):
        self['____lt'] = val

    lt = property(_get_lt, _set_lt)
    
    def __getitem__(self, key):
        if key.startswith('____'):
            return self._dict_impl().__getitem__(self, key)
        return _odict.__getitem__(self, key)
    
    def __setitem__(self, key, val):
        if key.startswith('____'):
            # private attributes, no way to set persistent attributes on
            # OOBTree deriving class.
            self._dict_impl().__setitem__(self, key, val)
        else:
            _odict.__setitem__(self, key, val)
    
    def __repr__(self):
        if self:
            pairs = ("(%r, %r)" % (k, v) for k, v in self.iteritems())
            return "OOBTodict([%s])" % ", ".join(pairs)
        else:
            return "OOBTodict()"


def volatile_property(func):
    """Like ``node.utils.instance_property``, but sets instance attribute
    with '_v_' prefix.
    """
    def wrapper(self):
        attribute_name = '_v_%s' % func.__name__
        if not hasattr(self, attribute_name):
            setattr(self, attribute_name, func(self))
        return getattr(self, attribute_name)
    wrapper.__doc__ = func.__doc__
    return property(wrapper)