from BTrees.OOBTree import OOBTree
from ZODB.DB import DB
from ZODB.FileStorage import FileStorage
from node.ext.zodb import IZODBNode
from node.ext.zodb import OOBTNode
from node.ext.zodb import OOBTNodeAttributes
from node.ext.zodb import OOBTodict
from node.ext.zodb import Podict
from node.ext.zodb import ZODBNode
from node.ext.zodb import ZODBNodeAttributes
from node.ext.zodb import volatile_property
from node.ext.zodb.utils import ListHeadInconsistency
from node.ext.zodb.utils import ListReferenceInconsistency
from node.ext.zodb.utils import ListTailInconsistency
from node.ext.zodb.utils import UnexpextedEndOfList
from node.ext.zodb.utils import check_odict_consistency
from node.ext.zodb.utils import reset_odict
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
        self.storage = FileStorage(os.path.join(self.tempdir, 'Data.fs'))
        self.db = DB(self.storage)
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
        self.assertEqual(list(root.keys()), ['oobtodict'])
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
        self.assertEqual(
            cls.__getitem__(od, 'chick'),
            ['cow', od['chick'], _nil]
        )
        self.assertEqual(
            cls.__getitem__(od, 'cow'),
            ['bam', od['cow'], 'chick']
        )
        self.assertEqual(cls.__getitem__(od, 'foo'), [_nil, od['foo'], 'baz'])
        self.assertEqual(od.lh, 'foo')
        self.assertEqual(od.lt, 'chick')
        # Delete from database
        del root['oobtodict']
        self.close()

    def test_ZODBNode(self):
        # Based on PersistentDict as storage
        zodbnode = ZODBNode('zodbnode')
        # Interface check
        self.assertTrue(IZODBNode.providedBy(zodbnode))
        # Storage check
        self.assertTrue(isinstance(zodbnode.storage, Podict))
        self.assertTrue(isinstance(zodbnode._storage, Podict))
        # Structure check
        root = self.open()
        root[zodbnode.__name__] = zodbnode
        zodbnode['child'] = ZODBNode('child')
        self.check_output("""\
        {'zodbnode': <ZODBNode object 'zodbnode' at ...>}
        """, repr(root))
        self.assertEqual(zodbnode.keys(), ['child'])
        self.assertEqual(zodbnode.values(), [zodbnode['child']])
        self.assertEqual(zodbnode.treerepr(), (
            '<class \'node.ext.zodb.ZODBNode\'>: zodbnode\n'
            '  <class \'node.ext.zodb.ZODBNode\'>: child\n'
        ))
        self.assertEqual(list(root.keys()), ['zodbnode'])
        # Reopen database connection and check again
        self.close()
        root = self.open()
        self.assertEqual(list(root.keys()), ['zodbnode'])
        zodbnode = root['zodbnode']
        self.assertEqual(zodbnode.treerepr(), (
            '<class \'node.ext.zodb.ZODBNode\'>: zodbnode\n'
            '  <class \'node.ext.zodb.ZODBNode\'>: child\n'
        ))
        # Delete child node
        del zodbnode['child']
        self.assertEqual(zodbnode.treerepr(), (
            '<class \'node.ext.zodb.ZODBNode\'>: zodbnode\n'
        ))
        # Check node attributes
        self.assertTrue(isinstance(zodbnode.attrs, ZODBNodeAttributes))
        self.assertEqual(zodbnode.attrs.name, '_attrs')
        zodbnode.attrs['foo'] = 1
        bar = zodbnode.attrs['bar'] = ZODBNode()
        self.assertEqual(zodbnode.attrs.values(), [1, bar])
        # Fill root with some ZODBNodes and check memory usage
        transaction.commit()
        old_size = self.storage.getSize()
        root['largezodb'] = ZODBNode('largezodb')
        for i in range(1000):
            root['largezodb'][str(i)] = ZODBNode()
        self.assertEqual(len(root['largezodb']), 1000)
        transaction.commit()
        new_size = self.storage.getSize()
        # ZODB 3 and ZODB 5 return different sizes so check whether lower or
        # equal higher value
        self.assertTrue((new_size - old_size) / 1000 <= 160)
        self.close()

    def test_OOBTNode(self):
        # Based on OOBTree as storage
        oobtnode = OOBTNode('oobtnode')
        # Interface check
        self.assertTrue(IZODBNode.providedBy(oobtnode))
        # Storage check
        self.assertTrue(isinstance(oobtnode.storage, OOBTodict))
        self.assertTrue(isinstance(oobtnode._storage, OOBTodict))
        # Structure check
        root = self.open()
        root[oobtnode.__name__] = oobtnode
        oobtnode['child'] = OOBTNode('child')
        self.assertEqual(sorted(root.keys()), ['oobtnode'])
        self.assertEqual(oobtnode.keys(), ['child'])
        self.assertEqual(oobtnode.values(), [oobtnode['child']])
        self.assertEqual(oobtnode.treerepr(), (
            '<class \'node.ext.zodb.OOBTNode\'>: oobtnode\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: child\n'
        ))
        self.check_output("""\
        OOBTodict([('child', <OOBTNode object 'child' at ...>)])
        """, repr(oobtnode.storage))
        # Reopen database connection and check again
        self.close()
        root = self.open()
        self.assertEqual(sorted(root.keys()), ['oobtnode'])
        oobtnode = root['oobtnode']
        self.assertEqual(oobtnode.keys(), ['child'])
        self.assertEqual(oobtnode.treerepr(), (
            '<class \'node.ext.zodb.OOBTNode\'>: oobtnode\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: child\n'
        ))
        self.assertTrue(oobtnode['child'].__parent__ is oobtnode)
        # Delete child node
        del oobtnode['child']
        transaction.commit()
        self.assertEqual(oobtnode.treerepr(), (
            '<class \'node.ext.zodb.OOBTNode\'>: oobtnode\n'
        ))
        # Check node attributes
        self.assertTrue(isinstance(oobtnode.attrs, OOBTNodeAttributes))
        self.assertEqual(oobtnode.attrs.name, '_attrs')
        oobtnode.attrs['foo'] = 1
        bar = oobtnode.attrs['bar'] = OOBTNode()
        self.assertEqual(oobtnode.attrs.values(), [1, bar])
        # Check attribute access for node attributes
        oobtnode.attribute_access_for_attrs = True
        self.assertEqual(oobtnode.attrs.foo, 1)
        # Check whether flag has been persisted
        self.close()
        root = self.open()
        oobtnode = root['oobtnode']
        self.assertEqual(oobtnode.attrs.foo, 1)
        self.assertEqual(oobtnode.attrs.bar, oobtnode.attrs['bar'])
        oobtnode.attrs.foo = 2
        self.assertEqual(oobtnode.attrs.foo, 2)
        oobtnode.attribute_access_for_attrs = False
        # Check attrs storage
        self.check_output("""\
        OOBTodict([('foo', 2), ('bar', <OOBTNode object 'bar' at ...>)])
        """, repr(oobtnode.attrs.storage))
        self.check_output("""\
        OOBTodict([('foo', 2), ('bar', <OOBTNode object 'bar' at ...>)])
        """, repr(oobtnode.attrs._storage))
        self.assertTrue(oobtnode.attrs.storage is oobtnode.attrs._storage)
        self.close()
        root = self.open()
        oobtnode = root['oobtnode']
        oobtnode.attribute_access_for_attrs = False
        self.check_output("""\
        OOBTodict([('foo', 2), ('bar', <OOBTNode object 'bar' at ...>)])
        """, repr(oobtnode.attrs.storage))
        # Check internal datastructure of attrs
        storage = oobtnode.attrs.storage
        cls = storage._dict_impl()
        self.assertTrue(cls is OOBTree)
        self.assertEqual(
            sorted(cls.keys(storage)),
            ['____lh', '____lt', 'bar', 'foo']
        )
        # values ``foo`` and ``bar`` are list tail and list head values
        self.assertEqual(cls.__getitem__(storage, '____lh'), 'foo')
        self.assertEqual(cls.__getitem__(storage, '____lt'), 'bar')
        attrs = oobtnode.attrs
        self.assertEqual(
            cls.__getitem__(storage, 'bar'),
            ['foo', attrs['bar'], _nil]
        )
        self.assertEqual(
            cls.__getitem__(storage, 'foo'),
            [_nil, 2, 'bar']
        )
        self.assertEqual(storage.lt, 'bar')
        self.assertEqual(storage.lh, 'foo')
        # Add attribute, reopen database connection and check again
        oobtnode.attrs['baz'] = 'some added value'
        self.close()
        root = self.open()
        oobtnode = root['oobtnode']
        storage = oobtnode.attrs.storage
        cls = storage._dict_impl()
        self.assertEqual(cls.__getitem__(storage, '____lh'), 'foo')
        self.assertEqual(cls.__getitem__(storage, '____lt'), 'baz')
        attrs = oobtnode.attrs
        self.assertEqual(
            cls.__getitem__(storage, 'bar'),
            ['foo', attrs['bar'], 'baz']
        )
        self.assertEqual(
            cls.__getitem__(storage, 'baz'),
            ['bar', 'some added value', _nil]
        )
        self.assertEqual(
            cls.__getitem__(storage, 'foo'),
            [_nil, 2, 'bar']
        )
        self.assertEqual(storage.lt, 'baz')
        self.assertEqual(storage.lh, 'foo')
        # Test copy and detach
        oobtnode['c1'] = OOBTNode()
        oobtnode['c2'] = OOBTNode()
        oobtnode['c3'] = OOBTNode()
        self.assertEqual(oobtnode.treerepr(), (
            '<class \'node.ext.zodb.OOBTNode\'>: oobtnode\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c1\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c2\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c3\n'
        ))
        # Detach c1
        c1 = oobtnode.detach('c1')
        self.assertTrue(isinstance(c1, OOBTNode))
        self.assertEqual(c1.name, 'c1')
        self.assertEqual(oobtnode.treerepr(), (
            '<class \'node.ext.zodb.OOBTNode\'>: oobtnode\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c2\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c3\n'
        ))
        # Add c1 as child to c2
        oobtnode['c2'][c1.name] = c1
        self.assertEqual(oobtnode.treerepr(), (
            '<class \'node.ext.zodb.OOBTNode\'>: oobtnode\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c2\n'
            '    <class \'node.ext.zodb.OOBTNode\'>: c1\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c3\n'
        ))
        # Reopen database connection and check again
        self.close()
        root = self.open()
        oobtnode = root['oobtnode']
        self.assertEqual(oobtnode.treerepr(), (
            '<class \'node.ext.zodb.OOBTNode\'>: oobtnode\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c2\n'
            '    <class \'node.ext.zodb.OOBTNode\'>: c1\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c3\n'
        ))
        # Copy c1
        c1_copy = oobtnode['c2']['c1'].copy()
        self.assertFalse(c1_copy is oobtnode['c2']['c1'])
        oobtnode['c1'] = c1_copy
        self.assertEqual(oobtnode.treerepr(), (
            '<class \'node.ext.zodb.OOBTNode\'>: oobtnode\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c2\n'
            '    <class \'node.ext.zodb.OOBTNode\'>: c1\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c3\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c1\n'
        ))
        oobtnode['c4'] = oobtnode['c2'].copy()
        self.assertEqual(oobtnode.treerepr(), (
            '<class \'node.ext.zodb.OOBTNode\'>: oobtnode\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c2\n'
            '    <class \'node.ext.zodb.OOBTNode\'>: c1\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c3\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c1\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c4\n'
            '    <class \'node.ext.zodb.OOBTNode\'>: c1\n'
        ))
        self.assertFalse(oobtnode['c2']['c1'] is oobtnode['c4']['c1'])
        self.assertFalse(
            oobtnode['c2']['c1'].attrs is oobtnode['c4']['c1'].attrs
        )
        transaction.commit()
        # Swap nodes
        oobtnode.swap(oobtnode['c1'], oobtnode['c3'])
        oobtnode.swap(oobtnode['c1'], oobtnode['c2'])
        self.assertEqual(oobtnode.treerepr(), (
            '<class \'node.ext.zodb.OOBTNode\'>: oobtnode\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c1\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c2\n'
            '    <class \'node.ext.zodb.OOBTNode\'>: c1\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c3\n'
            '  <class \'node.ext.zodb.OOBTNode\'>: c4\n'
            '    <class \'node.ext.zodb.OOBTNode\'>: c1\n'
        ))
        # Calling nodes does nothing, persisting is left to transaction
        # mechanism
        oobtnode()
        # Fill root with some OOBTNodes and check memory usage
        old_size = self.storage.getSize()
        root['large'] = OOBTNode()
        for i in range(1000):
            root['large'][str(i)] = OOBTNode()
        self.assertEqual(len(root['large']), 1000)
        transaction.commit()
        new_size = self.storage.getSize()
        # ZODB 3 and ZODB 5 return different sizes so check whether lower or
        # equal higher value
        self.assertTrue((new_size - old_size) / 1000 <= 160)
        self.close()

    def test_utils(self):
        # Test ``volatile_property``
        class PropTest(object):
            @volatile_property
            def foo(self):
                return 'foo'
        inst = PropTest()
        self.assertTrue('foo' in dir(inst))
        self.assertFalse('_v_foo' in dir(inst))
        self.assertEqual(inst.foo, 'foo')
        self.assertTrue('_v_foo' in dir(inst))
        self.assertEqual(inst._v_foo, 'foo')
        self.assertTrue(inst._v_foo is inst.foo)
        # Check odict consistency
        od = OOBTodict()
        od['foo'] = 'foo'
        od['bar'] = 'bar'
        od['baz'] = 'baz'
        # Ignore key callback for OOBTree odicts needs to ignore keys starting
        # with four underscores since these entries define the object
        # attributes

        def ignore_key(key):
            return key.startswith('____')

        check_odict_consistency(od, ignore_key=ignore_key)
        # Check if ``_nil`` marker set irregulary
        dict_impl = od._dict_impl()
        dict_impl.__setitem__(od, 'bam', ['foo', 'bam', _nil])
        self.assertEqual(od.keys(), ['foo', 'bar', 'baz'])
        self.assertEqual(
            sorted(dict_impl.keys(od)),
            ['____lh', '____lt', 'bam', 'bar', 'baz', 'foo']
        )
        err = self.expect_error(
            UnexpextedEndOfList,
            check_odict_consistency,
            od,
            ignore_key=ignore_key
        )
        expected = (
            'Unexpected ``_nil`` pointer found in double linked '
            'list. Resulting key count does not match:  4 != 3'
        )
        self.assertEqual(str(err), expected)
        # Manually sanitize odict
        dict_impl.__delitem__(od, 'bam')
        check_odict_consistency(od, ignore_key=ignore_key)
        # Check whether double linked list contains inexistent key
        dict_impl.__setitem__(od, 'foo', [_nil, 'foo', 'inexistent'])
        err = self.expect_error(
            ListReferenceInconsistency,
            check_odict_consistency,
            od,
            ignore_key=ignore_key
        )
        expected = (
            'Double linked list contains a reference to a non existing dict '
            'entry: \'inexistent\' not in [\'bar\', \'baz\', \'foo\']'
        )
        self.assertEqual(str(err), expected)
        # Manually sanitize odict
        dict_impl.__setitem__(od, 'foo', [_nil, 'foo', 'bar'])
        check_odict_consistency(od, ignore_key=ignore_key)
        # Check broken list head
        od.lh = 'inexistent'
        err = self.expect_error(
            ListHeadInconsistency,
            check_odict_consistency,
            od,
            ignore_key=ignore_key
        )
        expected = (
            'List head contains a reference to a non existing dict entry: '
            '\'inexistent\' not in [\'bar\', \'baz\', \'foo\']'
        )
        self.assertEqual(str(err), expected)
        # Manually sanitize odict
        od.lh = 'foo'
        check_odict_consistency(od, ignore_key=ignore_key)
        # Check broken list tail
        od.lt = 'inexistent'
        err = self.expect_error(
            ListTailInconsistency,
            check_odict_consistency,
            od,
            ignore_key=ignore_key
        )
        expected = (
            'List tail contains a reference to a non existing dict entry: '
            '\'inexistent\' not in [\'bar\', \'baz\', \'foo\']'
        )
        self.assertEqual(str(err), expected)
        # Manually sanitize odict
        od.lt = 'baz'
        check_odict_consistency(od, ignore_key=ignore_key)
        # Reset odict
        od.lh = 'inexistent'
        od.lt = 'baz'
        dict_impl.__setitem__(od, 'foo', ['123', 'foo', 'bar'])
        dict_impl.__setitem__(od, '123', [_nil, 'foo', _nil])
        reset_odict(od, ignore_key=ignore_key)
        self.assertEqual(od.lh, '123')
        self.assertEqual(od.lt, 'foo')
        self.check_output("""\
        OOBTodict([('123', 'foo'),
        ('bar', 'bar'),
        ('baz', 'baz'),
        ('foo', 'foo')])
        """, repr(od))
        check_odict_consistency(od, ignore_key=ignore_key)


if __name__ == '__main__':
    unittest.main()                                          # pragma: no cover
