node.ext.zodb
=============

Setup environment:

.. code-block:: pycon

    >>> import os
    >>> import tempfile
    >>> tempdir = tempfile.mkdtemp()
    >>> import ZODB
    >>> from ZODB.FileStorage import FileStorage
    >>> from ZODB.DB import DB
    >>> storage = FileStorage(os.path.join(tempdir, 'Data.fs'))
    >>> db = DB(storage)
    >>> connection = db.open()
    >>> root = connection.root()


OOBTree
=======

Test OOBTree persistence:

.. code-block:: pycon

    >>> from BTrees.OOBTree import OOBTree
    >>> bt = OOBTree()
    >>> root['btree'] = bt
    >>> bt['key'] = [1, OOBTree(), 3]
    >>> bt['key']
    [1, <BTrees.OOBTree.OOBTree object at ...>, 3]

Commit and reopen database:

.. code-block:: pycon

    >>> import transaction
    >>> transaction.commit()
    >>> connection.close()
    >>> db.close()
    >>> storage = FileStorage(os.path.join(tempdir, 'Data.fs'))
    >>> db = DB(storage)
    >>> connection = db.open()
    >>> root = connection.root()

Check whether we get back object as it was stored:

.. code-block:: pycon

    >>> bt = root['btree']
    >>> bt['key']
    [1, <BTrees.OOBTree.OOBTree object at ...>, 3]

Delete OOBTree:

.. code-block:: pycon

    >>> del root['btree']
    >>> transaction.commit()


OOBTodict
=========

Test OOBTodict:

.. code-block:: pycon

    >>> from node.ext.zodb import OOBTodict
    >>> od = root['oobtodict'] = OOBTodict()
    >>> od
    OOBTodict()

Class bases:

.. code-block:: pycon

    >>> od.__class__.__bases__
    (<class 'odict.pyodict._odict'>, <type 'BTrees.OOBTree.OOBTree'>)

Add some children:

.. code-block:: pycon

    >>> od['foo'] = OOBTodict()
    >>> od['bar'] = OOBTodict()
    >>> od['baz'] = OOBTodict()
    >>> od
    OOBTodict([('foo', OOBTodict()), ('bar', OOBTodict()), ('baz', OOBTodict())])

Internal data representation:

.. code-block:: pycon

    >>> od._dict_impl()
    <type 'BTrees.OOBTree.OOBTree'>

    >>> data = list(od._dict_impl().items(od))
    >>> data = sorted(data, key=lambda x: x[0])
    >>> data
    [('____lh', 'foo'), 
    ('____lt', 'baz'), 
    ('bar', ['foo', OOBTodict(), 'baz']), 
    ('baz', ['bar', OOBTodict(), nil]), 
    ('foo', [nil, OOBTodict(), 'bar'])]

    >>> od.lt
    'baz'

    >>> od.lh
    'foo'

    >>> od._dict_impl().__getitem__(od, 'foo')
    [nil, OOBTodict(), 'bar']

    >>> od._dict_impl().__getitem__(od, 'bar')
    ['foo', OOBTodict(), 'baz']

    >>> od._dict_impl().__getitem__(od, 'baz')
    ['bar', OOBTodict(), nil]

Check keys:

.. code-block:: pycon

    >>> od.keys()
    ['foo', 'bar', 'baz']

Check iterkeys:

.. code-block:: pycon

    >>> list(od.iterkeys())
    ['foo', 'bar', 'baz']

Check values:

.. code-block:: pycon

    >>> od.values()
    [OOBTodict(), OOBTodict(), OOBTodict()]

Check itervalues:

.. code-block:: pycon

    >>> list(od.itervalues())
    [OOBTodict(), OOBTodict(), OOBTodict()]

Check items:

.. code-block:: pycon

    >>> od.items()
    [('foo', OOBTodict()), ('bar', OOBTodict()), ('baz', OOBTodict())]

Check iteritems:

.. code-block:: pycon

    >>> list(od.iteritems())
    [('foo', OOBTodict()), ('bar', OOBTodict()), ('baz', OOBTodict())]

Check __iter__:

.. code-block:: pycon

    >>> [key for key in od]
    ['foo', 'bar', 'baz']

Check __getitem__:

.. code-block:: pycon

    >>> od['foo']
    OOBTodict()

Check __delitem__:

.. code-block:: pycon

    >>> del od['baz']
    >>> od
    OOBTodict([('foo', OOBTodict()), ('bar', OOBTodict())])

    >>> 'foo' in od
    True

    >>> 'baz' in od
    False

Check __len__:

.. code-block:: pycon

    >>> len(od)
    2

Check get:

.. code-block:: pycon

    >>> od.get('foo')
    OOBTodict()

    >>> od.get('baz')

Check copy:

.. code-block:: pycon

    >>> od2 = od.copy()
    >>> od2
    OOBTodict([('foo', OOBTodict()), ('bar', OOBTodict())])

Copied object not original one:

.. code-block:: pycon

    >>> od is od2
    False

    >>> od2.keys()
    ['foo', 'bar']

Check sort:

.. code-block:: pycon

    >>> od2.sort(key=lambda x: x[0])
    >>> od2
    OOBTodict([('bar', OOBTodict()), ('foo', OOBTodict())])

    >>> od2.keys()
    ['bar', 'foo']

Check update:

.. code-block:: pycon

    >>> od2.update([('bam', OOBTodict())])
    >>> od2.keys()
    ['bar', 'foo', 'bam']

Check popitem:

.. code-block:: pycon

    >>> od2.popitem()
    ('bam', OOBTodict())

    >>> od2.keys()
    ['bar', 'foo']

Reopen database connection and check structure:

.. code-block:: pycon

    >>> transaction.commit()
    >>> connection.close()
    >>> db.close()
    >>> storage = FileStorage(os.path.join(tempdir, 'Data.fs'))
    >>> db = DB(storage)
    >>> connection = db.open()
    >>> root = connection.root()
    >>> root.keys()
    ['oobtodict']

    >>> od = root['oobtodict']
    >>> data = list(od._dict_impl().items(od))
    >>> data = sorted(data, key=lambda x: x[0])
    >>> data
    [('____lh', 'foo'), 
    ('____lt', 'bar'), 
    ('bar', ['foo', OOBTodict(), nil]), 
    ('foo', [nil, OOBTodict(), 'bar'])]

    >>> od.lt
    'bar'

    >>> od.lh
    'foo'

    >>> od._dict_impl().__getitem__(od, 'foo')
    [nil, OOBTodict(), 'bar']

    >>> od._dict_impl().__getitem__(od, 'bar')
    ['foo', OOBTodict(), nil]

Add attributes and reopen database connection and check structure:

.. code-block:: pycon

    >>> od['baz'] = OOBTodict()
    >>> od['bam'] = OOBTodict()

    >>> transaction.commit()
    >>> connection.close()
    >>> db.close()
    >>> storage = FileStorage(os.path.join(tempdir, 'Data.fs'))
    >>> db = DB(storage)
    >>> connection = db.open()
    >>> root = connection.root()
    >>> od = root['oobtodict']
    >>> data = list(od._dict_impl().items(od))
    >>> data = sorted(data, key=lambda x: x[0])
    >>> data
    [('____lh', 'foo'), ('____lt', 'bam'), 
    ('bam', ['baz', OOBTodict(), nil]), 
    ('bar', ['foo', OOBTodict(), 'baz']), 
    ('baz', ['bar', OOBTodict(), 'bam']), 
    ('foo', [nil, OOBTodict(), 'bar'])]

    >>> od.keys()
    ['foo', 'bar', 'baz', 'bam']

Add and delete attributes and reopen database connection and check structure:

.. code-block:: pycon

    >>> del od['bar']
    >>> od['cow'] = OOBTodict()
    >>> od['chick'] = OOBTodict()

    >>> transaction.commit()
    >>> connection.close()
    >>> db.close()
    >>> storage = FileStorage(os.path.join(tempdir, 'Data.fs'))
    >>> db = DB(storage)
    >>> connection = db.open()
    >>> root = connection.root()
    >>> od = root['oobtodict']
    >>> data = list(od._dict_impl().items(od))
    >>> data = sorted(data, key=lambda x: x[0])

    >>> od.keys()
    ['foo', 'baz', 'bam', 'cow', 'chick']

    >>> data
    [('____lh', 'foo'), 
    ('____lt', 'chick'), 
    ('bam', ['baz', OOBTodict(), 'cow']), 
    ('baz', ['foo', OOBTodict(), 'bam']), 
    ('chick', ['cow', OOBTodict(), nil]), 
    ('cow', ['bam', OOBTodict(), 'chick']), 
    ('foo', [nil, OOBTodict(), 'baz'])]

Delete from database:

.. code-block:: pycon

    >>> del root['oobtodict']


ZODBNode
========

Based on PersistentDict as storage:

.. code-block:: pycon

    >>> from node.ext.zodb import IZODBNode
    >>> from node.ext.zodb import ZODBNode
    >>> zodbnode = ZODBNode('zodbnode')
    >>> zodbnode
    <ZODBNode object 'zodbnode' at ...>

Interface check:

.. code-block:: pycon

    >>> IZODBNode.providedBy(zodbnode)
    True

Storage check:

.. code-block:: pycon

    >>> zodbnode.storage
    Podict()

    >>> zodbnode._storage
    Podict()

Structure check:

.. code-block:: pycon

    >>> root[zodbnode.__name__] = zodbnode
    >>> zodbnode['child'] = ZODBNode('child')
    >>> root
    {'zodbnode': <ZODBNode object 'zodbnode' at ...>}

    >>> zodbnode.keys()
    ['child']

    >>> zodbnode.values()
    [<ZODBNode object 'child' at ...>]

    >>> zodbnode['child']
    <ZODBNode object 'child' at ...>

    >>> zodbnode.printtree()
    <class 'node.ext.zodb.ZODBNode'>: zodbnode
      <class 'node.ext.zodb.ZODBNode'>: child

    >>> root.keys()
    ['zodbnode']

Reopen database connection and check again:

.. code-block:: pycon

    >>> transaction.commit()
    >>> connection.close()
    >>> db.close()
    >>> storage = FileStorage(os.path.join(tempdir, 'Data.fs'))
    >>> db = DB(storage)
    >>> connection = db.open()
    >>> root = connection.root()
    >>> root.keys()
    ['zodbnode']

    >>> root['zodbnode'].printtree()
    <class 'node.ext.zodb.ZODBNode'>: zodbnode
      <class 'node.ext.zodb.ZODBNode'>: child

Delete child node:

.. code-block:: pycon

    >>> del root['zodbnode']['child']

    >>> root['zodbnode'].printtree()
    <class 'node.ext.zodb.ZODBNode'>: zodbnode

Check node attributes:

.. code-block:: pycon

    >>> root['zodbnode'].attrs
    <ZODBNodeAttributes object '_attrs' at ...>

    >>> root['zodbnode'].attrs['foo'] = 1
    >>> root['zodbnode'].attrs['bar'] = ZODBNode()
    >>> root['zodbnode'].attrs.values()
    [1, <ZODBNode object 'bar' at ...>]

    >>> transaction.commit()

Fill root with some ZODBNodes and check memory usage:

.. code-block:: pycon

    >>> old_size = storage.getSize()

    >>> root['largezodb'] = ZODBNode('largezodb')
    >>> for i in range(1000):
    ...     root['largezodb'][str(i)] = ZODBNode()

    >>> len(root['largezodb'])
    1000

    >>> transaction.commit()

    >>> new_size = storage.getSize()

ZODB 3 and ZODB 5 return different sizes so check whether lower or equal higher
value:

.. code-block:: pycon

    >>> (new_size - old_size) / 1000 <= 145
    True


OOBTNode
========

Based on OOBTree as storage:

.. code-block:: pycon

    >>> from node.ext.zodb import OOBTNode
    >>> oobtnode = OOBTNode('oobtnode')
    >>> oobtnode
    <OOBTNode object 'oobtnode' at ...>

Interface check:

.. code-block:: pycon

    >>> IZODBNode.providedBy(oobtnode)
    True

Storage check:

.. code-block:: pycon

    >>> oobtnode.storage
    OOBTodict()

    >>> oobtnode._storage
    OOBTodict()

Structure check:

.. code-block:: pycon

    >>> root[oobtnode.__name__] = oobtnode
    >>> oobtnode['child'] = OOBTNode('child')
    >>> sorted(root.keys())
    ['largezodb', 'oobtnode', 'zodbnode']

    >>> oobtnode.keys()
    ['child']

    >>> oobtnode.values()
    [<OOBTNode object 'child' at ...>]

    >>> oobtnode['child']
    <OOBTNode object 'child' at ...>

    >>> oobtnode.printtree()
    <class 'node.ext.zodb.OOBTNode'>: oobtnode
      <class 'node.ext.zodb.OOBTNode'>: child

    >>> oobtnode.storage
    OOBTodict([('child', <OOBTNode object 'child' at ...>)])

Reopen database connection and check again:

.. code-block:: pycon

    >>> transaction.commit()
    >>> connection.close()
    >>> db.close()
    >>> storage = FileStorage(os.path.join(tempdir, 'Data.fs'))
    >>> db = DB(storage)
    >>> connection = db.open()
    >>> root = connection.root()
    >>> sorted(root.keys())
    ['largezodb', 'oobtnode', 'zodbnode']

    >>> oobtnode = root['oobtnode']
    >>> oobtnode.keys()
    ['child']

    >>> oobtnode.printtree()
    <class 'node.ext.zodb.OOBTNode'>: oobtnode
      <class 'node.ext.zodb.OOBTNode'>: child

    >>> oobtnode['child'].__parent__
    <OOBTNode object 'oobtnode' at ...>

Delete child node:

.. code-block:: pycon

    >>> del oobtnode['child']
    >>> transaction.commit()

    >>> oobtnode.printtree()
    <class 'node.ext.zodb.OOBTNode'>: oobtnode

Check node attributes:

.. code-block:: pycon

    >>> oobtnode.attrs
    <OOBTNodeAttributes object '_attrs' at ...>

    >>> oobtnode.attrs['foo'] = 1
    >>> oobtnode.attrs['bar'] = OOBTNode()
    >>> oobtnode.attrs.values()
    [1, <OOBTNode object 'bar' at ...>]

Check attribute access for node attributes:

.. code-block:: pycon

    >>> oobtnode.attribute_access_for_attrs = True
    >>> oobtnode.attrs.foo
    1

Check whether flag has been persisted:

.. code-block:: pycon

    >>> transaction.commit()
    >>> connection.close()
    >>> db.close()
    >>> storage = FileStorage(os.path.join(tempdir, 'Data.fs'))
    >>> db = DB(storage)
    >>> connection = db.open()
    >>> root = connection.root()

    >>> oobtnode = root['oobtnode']
    >>> oobtnode.attrs.foo
    1

    >>> oobtnode.attrs.bar
    <OOBTNode object 'bar' at ...>

    >>> oobtnode.attrs.foo = 2
    >>> oobtnode.attrs.foo
    2

    >>> oobtnode.attribute_access_for_attrs = False

Check attrs storage:

.. code-block:: pycon

    >>> oobtnode.attrs.storage
    OOBTodict([('foo', 2), ('bar', <OOBTNode object 'bar' at ...>)])

    >>> oobtnode.attrs._storage
    OOBTodict([('foo', 2), ('bar', <OOBTNode object 'bar' at ...>)])

    >>> oobtnode.attrs.storage is oobtnode.attrs._storage
    True

    >>> transaction.commit()
    >>> connection.close()
    >>> db.close()
    >>> storage = FileStorage(os.path.join(tempdir, 'Data.fs'))
    >>> db = DB(storage)
    >>> connection = db.open()
    >>> root = connection.root()
    >>> oobtnode = root['oobtnode']
    >>> oobtnode.attribute_access_for_attrs = False
    >>> oobtnode.attrs.storage
    OOBTodict([('foo', 2), ('bar', <OOBTNode object 'bar' at ...>)])

Check internal datastructure of attrs:

.. code-block:: pycon

    >>> storage = oobtnode.attrs.storage
    >>> storage._dict_impl()
    <type 'BTrees.OOBTree.OOBTree'>

    >>> keys = [_ for _ in storage._dict_impl().keys(storage)]
    >>> sorted(keys)
    ['____lh', '____lt', 'bar', 'foo']

values ``foo`` and ``bar`` are list tail and list head values:

.. code-block:: pycon

    >>> values = [_ for _ in storage._dict_impl().values(storage)]
    >>> sorted(values)
    [[nil, 2, 'bar'], 
    ['foo', <OOBTNode object 'bar' at ...>, nil], 
    'bar', 
    'foo']

    >>> storage.lt
    'bar'

    >>> storage.lh
    'foo'

Add attribute, reopen database connection and check again:

.. code-block:: pycon

    >>> oobtnode.attrs['baz'] = 'some added value'

    >>> transaction.commit()
    >>> connection.close()
    >>> db.close()
    >>> storage = FileStorage(os.path.join(tempdir, 'Data.fs'))
    >>> db = DB(storage)
    >>> connection = db.open()
    >>> root = connection.root()
    >>> oobtnode = root['oobtnode']

    >>> storage = oobtnode.attrs.storage
    >>> values = [_ for _ in storage._dict_impl().values(storage)]
    >>> sorted(values)
    [[nil, 2, 'bar'], 
    ['bar', 'some added value', nil], 
    ['foo', <OOBTNode object 'bar' at ...>, 'baz'], 
    'baz', 
    'foo']

Test copy and detach:

.. code-block:: pycon

    >>> oobtnode['c1'] = OOBTNode()
    >>> oobtnode['c2'] = OOBTNode()
    >>> oobtnode['c3'] = OOBTNode()
    >>> oobtnode.printtree()
    <class 'node.ext.zodb.OOBTNode'>: oobtnode
      <class 'node.ext.zodb.OOBTNode'>: c1
      <class 'node.ext.zodb.OOBTNode'>: c2
      <class 'node.ext.zodb.OOBTNode'>: c3

Detach c1:

.. code-block:: pycon

    >>> c1 = oobtnode.detach('c1')
    >>> c1
    <OOBTNode object 'c1' at ...>

    >>> oobtnode.printtree()
    <class 'node.ext.zodb.OOBTNode'>: oobtnode
      <class 'node.ext.zodb.OOBTNode'>: c2
      <class 'node.ext.zodb.OOBTNode'>: c3

Add c1 as child to c2:

.. code-block:: pycon

    >>> oobtnode['c2'][c1.name] = c1
    >>> oobtnode.printtree()
    <class 'node.ext.zodb.OOBTNode'>: oobtnode
      <class 'node.ext.zodb.OOBTNode'>: c2
        <class 'node.ext.zodb.OOBTNode'>: c1
      <class 'node.ext.zodb.OOBTNode'>: c3

Reopen database connection and check again:

.. code-block:: pycon

    >>> transaction.commit()
    >>> connection.close()
    >>> db.close()
    >>> storage = FileStorage(os.path.join(tempdir, 'Data.fs'))
    >>> db = DB(storage)
    >>> connection = db.open()
    >>> root = connection.root()
    >>> oobtnode = root['oobtnode']
    >>> oobtnode.printtree()
    <class 'node.ext.zodb.OOBTNode'>: oobtnode
      <class 'node.ext.zodb.OOBTNode'>: c2
        <class 'node.ext.zodb.OOBTNode'>: c1
      <class 'node.ext.zodb.OOBTNode'>: c3

Copy c1:

.. code-block:: pycon

    >>> c1_copy = oobtnode['c2']['c1'].copy()
    >>> c1_copy is oobtnode['c2']['c1']
    False

    >>> oobtnode['c1'] = c1_copy
    >>> oobtnode.printtree()
    <class 'node.ext.zodb.OOBTNode'>: oobtnode
      <class 'node.ext.zodb.OOBTNode'>: c2
        <class 'node.ext.zodb.OOBTNode'>: c1
      <class 'node.ext.zodb.OOBTNode'>: c3
      <class 'node.ext.zodb.OOBTNode'>: c1

    >>> oobtnode['c4'] = oobtnode['c2'].copy()
    >>> oobtnode.printtree()
    <class 'node.ext.zodb.OOBTNode'>: oobtnode
      <class 'node.ext.zodb.OOBTNode'>: c2
        <class 'node.ext.zodb.OOBTNode'>: c1
      <class 'node.ext.zodb.OOBTNode'>: c3
      <class 'node.ext.zodb.OOBTNode'>: c1
      <class 'node.ext.zodb.OOBTNode'>: c4
        <class 'node.ext.zodb.OOBTNode'>: c1

    >>> oobtnode['c2']['c1'] is oobtnode['c4']['c1']
    False

    >>> oobtnode['c2']['c1'].attrs is oobtnode['c4']['c1'].attrs
    False

    >>> transaction.commit()

Swap nodes:

.. code-block:: pycon

    >>> oobtnode.swap(oobtnode['c1'], oobtnode['c3'])
    >>> oobtnode.swap(oobtnode['c1'], oobtnode['c2'])
    >>> oobtnode.printtree()
    <class 'node.ext.zodb.OOBTNode'>: oobtnode
      <class 'node.ext.zodb.OOBTNode'>: c1
      <class 'node.ext.zodb.OOBTNode'>: c2
        <class 'node.ext.zodb.OOBTNode'>: c1
      <class 'node.ext.zodb.OOBTNode'>: c3
      <class 'node.ext.zodb.OOBTNode'>: c4
        <class 'node.ext.zodb.OOBTNode'>: c1

Calling nodes does nothing, persisting is left to transaction mechanism:

.. code-block:: pycon

    >>> oobtnode()

Fill root with some OOBTNodes and check memory usage:

.. code-block:: pycon

    >>> old_size = storage.getSize()

    >>> root['large'] = OOBTNode()
    >>> for i in range(1000):
    ...     root['large'][str(i)] = OOBTNode()

    >>> len(root['large'])
    1000

    >>> transaction.commit()

    >>> new_size = storage.getSize()

ZODB 3 and ZODB 5 return different sizes so check whether lower or equal higher
value:

.. code-block:: pycon

    >>> (new_size - old_size) / 1000 <= 139
    True


Utils
=====

Test ``volatile_property``:

.. code-block:: pycon

    >>> from node.ext.zodb import volatile_property
    >>> class PropTest(object):
    ...     @volatile_property
    ...     def foo(self):
    ...         return 'foo'

    >>> inst = PropTest()
    >>> 'foo' in dir(inst)
    True

    >>> '_v_foo' in dir(inst)
    False

    >>> inst.foo
    'foo'

    >>> '_v_foo' in dir(inst)
    True

    >>> inst._v_foo
    'foo'

    >>> inst._v_foo is inst.foo
    True

Check odict consistency:

.. code-block:: pycon

    >>> from odict.pyodict import _nil
    >>> from node.ext.zodb.utils import check_odict_consistency

    >>> od = OOBTodict()
    >>> od['foo'] = 'foo'
    >>> od['bar'] = 'bar'
    >>> od['baz'] = 'baz'

Ignore key callback for OOBTree odicts needs to ignore keys starting with
four underscores since these entries define the object attributes:

.. code-block:: pycon

    >>> ignore_key = lambda x: x.startswith('____')
    >>> check_odict_consistency(od, ignore_key=ignore_key)

Check if ``_nil`` marker set irregulary:

.. code-block:: pycon

    >>> dict_impl = od._dict_impl()
    >>> dict_impl.__setitem__(od, 'bam', ['foo', 'bam', _nil])
    >>> od.keys()
    ['foo', 'bar', 'baz']

    >>> sorted([_ for _ in dict_impl.keys(od)])
    ['____lh', '____lt', 'bam', 'bar', 'baz', 'foo']

    >>> check_odict_consistency(od, ignore_key=ignore_key)
    Traceback (most recent call last):
      ...
    UnexpextedEndOfList: Unexpected ``_nil`` pointer found in double linked 
    list. Resulting key count does not match:  4 != 3

Manually sanitize odict:

.. code-block:: pycon

    >>> dict_impl.__delitem__(od, 'bam')
    >>> check_odict_consistency(od, ignore_key=ignore_key)

Check whether double linked list contains inexistent key:

.. code-block:: pycon

    >>> dict_impl.__setitem__(od, 'foo', [_nil, 'foo', 'inexistent'])
    >>> check_odict_consistency(od, ignore_key=ignore_key)
    Traceback (most recent call last):
      ...
    ListReferenceInconsistency: Double linked list contains a reference 
    to a non existing dict entry: 'inexistent' not in ['bar', 'baz', 'foo']

Manually sanitize odict:

.. code-block:: pycon

    >>> dict_impl.__setitem__(od, 'foo', [_nil, 'foo', 'bar'])
    >>> check_odict_consistency(od, ignore_key=ignore_key)

Check broken list head:

.. code-block:: pycon

    >>> od.lh = 'inexistent'
    >>> check_odict_consistency(od, ignore_key=ignore_key)
    Traceback (most recent call last):
      ...
    ListHeadInconsistency: List head contains a reference to a non existing 
    dict entry: 'inexistent' not in ['bar', 'baz', 'foo']

Manually sanitize odict:

.. code-block:: pycon

    >>> od.lh = 'foo'
    >>> check_odict_consistency(od, ignore_key=ignore_key)

Check broken list tail:

.. code-block:: pycon

    >>> od.lt = 'inexistent'
    >>> check_odict_consistency(od, ignore_key=ignore_key)
    Traceback (most recent call last):
      ...
    ListTailInconsistency: List tail contains a reference to a non existing 
    dict entry: 'inexistent' not in ['bar', 'baz', 'foo']

Manually sanitize odict:

.. code-block:: pycon

    >>> od.lt = 'baz'
    >>> check_odict_consistency(od, ignore_key=ignore_key)

Reset odict:

.. code-block:: pycon

    >>> od.lh = 'inexistent'
    >>> od.lt = 'baz'
    >>> dict_impl.__setitem__(od, 'foo', ['123', 'foo', 'bar'])
    >>> dict_impl.__setitem__(od, '123', [_nil, 'foo', _nil])

    >>> from node.ext.zodb.utils import reset_odict
    >>> reset_odict(od, ignore_key=ignore_key)

    >>> od.lh
    '123'

    >>> od.lt
    'foo'

    >>> od
    OOBTodict([('123', 'foo'), ('bar', 'bar'), ('baz', 'baz'), ('foo', 'foo')])

    >>> check_odict_consistency(od, ignore_key=ignore_key)

Cleanup test environment:

.. code-block:: pycon

    >>> connection.close()
    >>> db.close()
    >>> import shutil
    >>> shutil.rmtree(tempdir)
