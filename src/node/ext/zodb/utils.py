from BTrees.OOBTree import OOBTree
from odict.pyodict import _nil
from odict.pyodict import _odict
from persistent.dict import PersistentDict


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


def volatile_property(func):
    """Like ``node.utils.instance_property``, but sets instance attribute
    with '_v_' prefix.
    """
    def wrapper(self):
        attribute_name = '_v_{}'.format(func.__name__)
        # do not use hasattr/getattr to avoid problems when overwriting
        # __getattr__ on a class which also uses volatile_property
        try:
            return object.__getattribute__(self, attribute_name)
        except AttributeError:
            setattr(self, attribute_name, func(self))
            return object.__getattribute__(self, attribute_name)
    wrapper.__doc__ = func.__doc__
    return property(wrapper)


##############################################################################
# maintenance utilities
##############################################################################

class ConsistencyError(Exception):
    """Base exception for odict data structure inconsistencies.
    """


class ListHeadInconsistency(ConsistencyError):
    """Thrown if list head references non existing dict entry.
    """

    def __init__(self, error, orgin_keys):
        self.missing = str(error)
        self.orgin_keys = orgin_keys
        message = (
            u'List head contains a reference to a non existing dict '
            u'entry: {} not in {}'
        )
        message = message.format(str(error), str(orgin_keys))
        super(ListHeadInconsistency, self).__init__(message)


class ListTailInconsistency(ConsistencyError):
    """Thrown if list tail references non existing dict entry.
    """

    def __init__(self, error, orgin_keys):
        self.missing = str(error)
        self.orgin_keys = orgin_keys
        message = (
            u'List tail contains a reference to a non existing dict '
            u'entry: {} not in {}'
        )
        message = message.format(str(error), str(orgin_keys))
        super(ListTailInconsistency, self).__init__(message)


class ListReferenceInconsistency(ConsistencyError):
    """Thrown if double linked list pointer references non existing dict entry.
    """

    def __init__(self, error, orgin_keys):
        self.missing = str(error)
        self.orgin_keys = orgin_keys
        message = (
            u'Double linked list contains a reference to a non '
            u'existing dict entry: {} not in {}'
        )
        message = message.format(str(error), str(orgin_keys))
        super(ListReferenceInconsistency, self).__init__(message)


class UnexpextedEndOfList(ConsistencyError):
    """Thrown if unexpected ``_nil`` pointer found in double linked list.
    """

    def __init__(self, od_keys, orgin_keys):
        self.od_keys = od_keys
        self.orgin_keys = orgin_keys
        message = (
            u'Unexpected ``_nil`` pointer found in double linked '
            u'list. Resulting key count does not match:  {} != {}'
        )
        message = message.format(len(orgin_keys), len(od_keys))
        super(UnexpextedEndOfList, self).__init__(message)


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
        if od.lh != _nil:
            od[od.lh]
    except KeyError, e:
        raise ListHeadInconsistency(e, orgin_keys)
    try:
        if od.lt != _nil:
            od[od.lt]
    except KeyError, e:
        raise ListTailInconsistency(e, orgin_keys)
    try:
        od_keys = od.keys()
    except KeyError, e:
        raise ListReferenceInconsistency(e, orgin_keys)
    if len(orgin_keys) != len(od_keys):
        raise UnexpextedEndOfList(od_keys, orgin_keys)


def reset_odict(od, ignore_key=None):
    """Reset odict. Order will break.
    """
    dict_impl = od._dict_impl()
    keys = dict_impl.keys(od)
    if ignore_key is not None:
        keys = [_ for _ in keys if not ignore_key(_)]
    items = []
    for key in keys:
        items.append((key, dict_impl.__getitem__(od, key)))
    dict_impl.clear(od)
    od.lh = _nil
    od.lt = _nil
    for k, v in items:
        od[k] = v[1]
