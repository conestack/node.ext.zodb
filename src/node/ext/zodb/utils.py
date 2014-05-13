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


##############################################################################
# maintenance utilities
##############################################################################

class ConsistencyError(Exception):
    """Exception used if odict data structure is damaged.
    """


def check_odict_consistency(od, ignore_key=None):
    """Check consistency of odict.

    If ignore_key is given, it gets called for all keys from original dict
    implementation and expect True for it if specific keys should be ignored.
    """
    dict_impl = od._dict_impl()
    orgin_keys = dict_impl.keys(od)
    if ignore_key is not None:
        orgin_keys = [_ for _ in orgin_keys if not ignore_key(_)]
    try:
        od[od.lh]
    except KeyError, e:
        message = u'List head contains a reference to a non ' +\
                  u'existing dict entry: %s not in %s'
        message = message % (str(e), str(orgin_keys))
        raise ConsistencyError(message)
    try:
        od[od.lt]
    except KeyError, e:
        message = u'List tail contains a reference to a non ' +\
                  u'existing dict entry: %s not in %s'
        message = message % (str(e), str(orgin_keys))
        raise ConsistencyError(message)
    try:
        od_keys = od.keys()
    except KeyError, e:
        message = u'Double linked list contains a reference to a non ' +\
                  u'existing dict entry: %s not in %s'
        message = message % (str(e), str(orgin_keys))
        raise ConsistencyError(message)
    if len(orgin_keys) != len(od_keys):
        message = u'Given odict based implementation double linked list ' +\
                  u'structure broken. Key count does not match: %s != %s'
        message = message % (len(orgin_keys), len(od_keys))
        raise ConsistencyError(message)
