from BTrees.OOBTree import OOBTree
from ZODB.DB import DB
from ZODB.FileStorage import FileStorage
from node.ext.zodb import OOBTodict
from node.tests import NodeTestCase
from odict.pyodict import _nil
from odict.pyodict import _odict
import ZODB
import os
import shutil
import tempfile
import transaction
import unittest


class TestNodeExtZODB(NodeTestCase):

    def setUp(self):
        super(TestNodeExtZODB, self).setUp()
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        super(TestNodeExtZODB, self).tearDown()
        shutil.rmtree(self.tempdir)

    def open(self):
        storage = FileStorage(os.path.join(self.tempdir, 'Data.fs'))
        self.db = DB(storage)
        self.connection = self.db.open()
        return self.connection.root()

    def close(self):
        transaction.commit()
        self.connection.close()
        self.db.close()

    def test_OOBTree_usage(self):
        # Test OOBTree persistence
        root = self.open()
        bt = OOBTree()
        root['btree'] = bt
        cld_bt = OOBTree()
        bt['key'] = [1, cld_bt, 3]
        self.check_output("""\
        [1, <BTrees.OOBTree.OOBTree object at ...>, 3]
        """, str(bt['key']))
        # Commit and reopen database
        self.close()
        root = self.open()
        # Check whether we get back object as it was stored
        self.check_output("""\
        [1, <BTrees.OOBTree.OOBTree object at ...>, 3]
        """, str(root['btree']['key']))
        # Delete OOBTree
        del root['btree']
        self.close()

    def test_OOBTodict(self):
        # Test bases
        od = OOBTodict()
        self.assertEqual(od.__class__.__bases__, (_odict, OOBTree))
        # Test dict impl
        cls = od._dict_impl()
        self.assertTrue(cls is OOBTree)
        # Test list tail and head
        od = OOBTodict()
        self.assertEqual(od.lt, _nil)
        self.assertEqual(od.lh, _nil)
        self.assertEqual(cls.__getitem__(od, '____lt'), _nil)
        self.assertEqual(cls.__getitem__(od, '____lh'), _nil)
        self.assertEqual(sorted(cls.keys(od)), ['____lh', '____lt'])
        # Add OOBTodict to root
        root = self.open()
        od = root['oobtodict'] = OOBTodict()
        # Add some children
        foo = od['foo'] = OOBTodict()
        bar = od['bar'] = OOBTodict()
        baz = od['baz'] = OOBTodict()
        self.check_output("""\
        OOBTodict([('foo', OOBTodict()),
        ('bar', OOBTodict()),
        ('baz', OOBTodict())])
        """, repr(od))
        # Internal data representation
        self.assertEqual(
            sorted(cls.keys(od)),
            ['____lh', '____lt', 'bar', 'baz', 'foo']
        )
        self.assertEqual(cls.__getitem__(od, '____lt'), 'baz')
        self.assertEqual(cls.__getitem__(od, '____lh'), 'foo')
        self.assertEqual(cls.__getitem__(od, 'foo'), [_nil, foo, 'bar'])
        self.assertEqual(cls.__getitem__(od, 'bar'), ['foo', bar, 'baz'])
        self.assertEqual(cls.__getitem__(od, 'baz'), ['bar', baz, _nil])
        # List tail and list head
        self.assertEqual(od.lt, 'baz')
        self.assertEqual(od.lh, 'foo')
        # Check keys
        self.assertEqual(od.keys(), ['foo', 'bar', 'baz'])
        # Check iterkeys
        self.assertEqual(list(od.iterkeys()), ['foo', 'bar', 'baz'])
        # Check values
        self.assertEqual(od.values(), [foo, bar, baz])
        # Check itervalues
        self.assertEqual(list(od.itervalues()), [foo, bar, baz])
        # Check items
        self.assertEqual(
            od.items(),
            [('foo', foo), ('bar', bar), ('baz', baz)]
        )
        # Check iteritems
        self.assertEqual(
            list(od.iteritems()),
            [('foo', foo), ('bar', bar), ('baz', baz)]
        )
        # Check __iter__
        self.assertEqual(list(od.__iter__()), ['foo', 'bar', 'baz'])
        # Check __getitem__
        self.assertEqual(od['foo'], foo)
        # Check __delitem__
        del od['baz']
        self.assertTrue('foo' in od)
        self.assertTrue('bar' in od)
        self.assertFalse('baz' in od)
        # Check __len__
        self.assertEqual(len(od), 2)
        # Check get
        self.assertEqual(od.get('foo'), foo)
        self.assertEqual(od.get('baz'), None)
        # Check copy
        od2 = od.copy()
        self.check_output("""\
        OOBTodict([('foo', OOBTodict()), ('bar', OOBTodict())])
        """, repr(od2))
        # Copied object not original one
        self.assertFalse(od is od2)
        self.assertEqual(od2.keys(), ['foo', 'bar'])
        # Check sort
        od2.sort(key=lambda x: x[0])
        self.check_output("""\
        OOBTodict([('bar', OOBTodict()), ('foo', OOBTodict())])
        """, repr(od2))
        self.assertEqual(od2.keys(), ['bar', 'foo'])
        # Check update
        bam = OOBTodict()
        od2.update([('bam', bam)])
        self.assertEqual(od2.keys(), ['bar', 'foo', 'bam'])
        # Check popitem
        self.assertEqual(od2.popitem(), ('bam', bam))
        self.assertEqual(od2.keys(), ['bar', 'foo'])
        # Reopen database connection and check structure
        self.close()
        root = self.open()
        self.assertEqual(root.keys(), ['oobtodict'])
        od = root['oobtodict']
        self.assertEqual(
            sorted(cls.keys(od)),
            ['____lh', '____lt', 'bar', 'foo']
        )
        self.assertEqual(cls.__getitem__(od, '____lh'), 'foo')
        self.assertEqual(cls.__getitem__(od, '____lt'), 'bar')
        self.assertEqual(cls.__getitem__(od, 'foo'), [_nil, od['foo'], 'bar'])
        self.assertEqual(cls.__getitem__(od, 'bar'), ['foo', od['bar'], _nil])
        self.assertEqual(od.lt, 'bar')
        self.assertEqual(od.lh, 'foo')
        # Add attributes and reopen database connection and check structure
        od['baz'] = OOBTodict()
        od['bam'] = OOBTodict()
        self.close()
        root = self.open()
        od = root['oobtodict']
        self.assertEqual(
            sorted(cls.keys(od)),
            ['____lh', '____lt', 'bam', 'bar', 'baz', 'foo']
        )
        self.assertEqual(cls.__getitem__(od, '____lh'), 'foo')
        self.assertEqual(cls.__getitem__(od, '____lt'), 'bam')
        self.assertEqual(cls.__getitem__(od, 'bam'), ['baz', od['bam'], _nil])
        self.assertEqual(cls.__getitem__(od, 'bar'), ['foo', od['bar'], 'baz'])
        self.assertEqual(cls.__getitem__(od, 'baz'), ['bar', od['baz'], 'bam'])
        self.assertEqual(cls.__getitem__(od, 'foo'), [_nil, od['foo'], 'bar'])
        self.assertEqual(od.keys(), ['foo', 'bar', 'baz', 'bam'])
        self.assertEqual(od.lt, 'bam')
        self.assertEqual(od.lh, 'foo')
        # Add and delete attributes and reopen database connection and check
        # structure
        del od['bar']
        od['cow'] = OOBTodict()
        od['chick'] = OOBTodict()
        self.close()
        root = self.open()
        od = root['oobtodict']
        self.assertEqual(od.keys(), ['foo', 'baz', 'bam', 'cow', 'chick'])
        self.assertEqual(
            sorted(cls.keys(od)),
            ['____lh', '____lt', 'bam', 'baz', 'chick', 'cow', 'foo']
        )
        self.assertEqual(cls.__getitem__(od, '____lh'), 'foo')
        self.assertEqual(cls.__getitem__(od, '____lt'), 'chick')
        self.assertEqual(cls.__getitem__(od, 'bam'), ['baz', od['bam'], 'cow'])
        self.assertEqual(cls.__getitem__(od, 'baz'), ['foo', od['baz'], 'bam'])
        self.assertEqual(cls.__getitem__(od, 'chick'), ['cow', od['chick'], _nil])
        self.assertEqual(cls.__getitem__(od, 'cow'), ['bam', od['cow'], 'chick'])
        self.assertEqual(cls.__getitem__(od, 'foo'), [_nil, od['foo'], 'baz'])
        self.assertEqual(od.lh, 'foo')
        self.assertEqual(od.lt, 'chick')
        # Delete from database
        del root['oobtodict']
        self.close()

"""

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
    >>> storage._dict_impl() == OOBTree
    True

    >>> sorted(storage._dict_impl().keys(storage))
    ['____lh', '____lt', 'bar', 'foo']

values ``foo`` and ``bar`` are list tail and list head values:

.. code-block:: pycon

    >>> storage._dict_impl().__getitem__(storage, '____lh')
    'foo'

    >>> storage._dict_impl().__getitem__(storage, '____lt')
    'bar'

    >>> storage._dict_impl().__getitem__(storage, 'bar')
    ['foo', <OOBTNode object 'bar' at ...>, nil]

    >>> storage._dict_impl().__getitem__(storage, 'foo')
    [nil, 2, 'bar']

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
    >>> storage._dict_impl().__getitem__(storage, '____lh')
    'foo'

    >>> storage._dict_impl().__getitem__(storage, '____lt')
    'baz'

    >>> storage._dict_impl().__getitem__(storage, 'bar')
    ['foo', <OOBTNode object 'bar' at ...>, 'baz']

    >>> storage._dict_impl().__getitem__(storage, 'baz')
    ['bar', 'some added value', nil]

    >>> storage._dict_impl().__getitem__(storage, 'foo')
    [nil, 2, 'bar']

    >>> storage.lt
    'baz'

    >>> storage.lh
    'foo'

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
"""


if __name__ == '__main__':
    unittest.main()                                          # pragma: no cover


# from interlude import interact
# from pprint import pprint
# import doctest
# import unittest
#
#
# optionflags = doctest.NORMALIZE_WHITESPACE | \
#               doctest.ELLIPSIS | \
#               doctest.REPORT_ONLY_FIRST_FAILURE
# 
# 
# TESTFILES = [
#     '__init__.rst',
# ]
#
#
# def test_suite():
#     return unittest.TestSuite([
#         doctest.DocFileSuite(
#             f,
#             optionflags=optionflags,
#             globs={'interact': interact,
#                    'pprint': pprint},
#         ) for f in TESTFILES
#     ])
#
#
# if __name__ == '__main__':
#     unittest.main(defaultTest='test_suite')                 #pragma NO COVERAGE
