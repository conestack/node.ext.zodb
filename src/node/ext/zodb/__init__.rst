Setup environment::

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

Test OOBTree persistence::

    >>> from BTrees.OOBTree import OOBTree
    >>> bt = OOBTree()
    >>> root['btree'] = bt
    >>> bt['key'] = [1, OOBTree(), 3]
    >>> bt['key']
    [1, <BTrees.OOBTree.OOBTree object at ...>, 3]
    
    >>> import transaction
    >>> transaction.commit()
    >>> connection.close()
    >>> db.close()
    >>> storage = FileStorage(os.path.join(tempdir, 'Data.fs'))
    >>> db = DB(storage)
    >>> connection = db.open()
    >>> root = connection.root()
    >>> bt = root['btree']
    >>> bt['key']
    [1, <BTrees.OOBTree.OOBTree object at ...>, 3]
    
    >>> del root['btree']
    >>> transaction.commit()

Test OOBTodict::

    >>> from node.ext.zodb import OOBTodict
    >>> od = OOBTodict()
    >>> od
    OOBTodict()
    
    >>> od.__class__.__bases__
    (<class 'odict.pyodict._odict'>, <type 'BTrees.OOBTree.OOBTree'>)
    
    >>> od['foo'] = OOBTodict()
    >>> od['bar'] = OOBTodict()
    >>> od['baz'] = OOBTodict()
    >>> od
    OOBTodict([('foo', OOBTodict()), ('bar', OOBTodict()), ('baz', OOBTodict())])
    
    >>> od._dict_impl().__getitem__(od, 'foo')
    [nil, OOBTodict(), 'bar']
    
    >>> od.lt
    'baz'
    
    >>> od.lh
    'foo'
    
    >>> od.keys()
    ['foo', 'bar', 'baz']
    
    >>> list(od.iterkeys())
    ['foo', 'bar', 'baz']
    
    >>> od.values()
    [OOBTodict(), OOBTodict(), OOBTodict()]
    
    >>> list(od.itervalues())
    [OOBTodict(), OOBTodict(), OOBTodict()]
    
    >>> od.items()
    [('foo', OOBTodict()), ('bar', OOBTodict()), ('baz', OOBTodict())]
    
    >>> list(od.iteritems())
    [('foo', OOBTodict()), ('bar', OOBTodict()), ('baz', OOBTodict())]
    
    >>> [key for key in od]
    ['foo', 'bar', 'baz']
    
    >>> od['foo']
    OOBTodict()
    
    >>> del od['baz']
    >>> od
    OOBTodict([('foo', OOBTodict()), ('bar', OOBTodict())])
    
    >>> 'foo' in od
    True
    
    >>> 'baz' in od
    False
    
    >>> len(od)
    2
    
    >>> od.get('foo')
    OOBTodict()
    
    >>> od.get('baz')
    
    >>> od2 = od.copy()
    >>> od2
    OOBTodict([('foo', OOBTodict()), ('bar', OOBTodict())])
    
    >>> od is od2
    False
    
    >>> od2.keys()
    ['foo', 'bar']

    >>> od2.sort(reverse=True)
    >>> od2.keys()
    ['bar', 'foo']
    
    >>> od2.update([('bam', OOBTodict())])
    >>> od2.keys()
    ['bar', 'foo', 'bam']
    
    >>> od2.popitem()
    ('bam', OOBTodict())
    
    >>> od2.keys()
    ['bar', 'foo']
    
    >>> od
    OOBTodict([('foo', OOBTodict()), ('bar', OOBTodict())])
    
    >>> od._dict_impl()
    <type 'BTrees.OOBTree.OOBTree'>
    
    >>> list(od._dict_impl().items(od))
    [('____lh', 'foo'), 
    ('____lt', 'bar'), 
    ('bar', ['foo', OOBTodict(), nil]), 
    ('foo', [nil, OOBTodict(), 'bar'])]
    
    >>> od._dict_impl().__getitem__(od, 'bar')
    ['foo', OOBTodict(), nil]
    
    >>> root['oobtodict'] = od
    >>> transaction.commit()
    >>> root.keys()
    ['oobtodict']
    
    >>> od.lt
    'bar'
    
    >>> od.lh
    'foo'
    
    >>> connection.close()
    >>> db.close()
    >>> storage = FileStorage(os.path.join(tempdir, 'Data.fs'))
    >>> db = DB(storage)
    >>> connection = db.open()
    >>> root = connection.root()
    >>> root.keys()
    ['oobtodict']
    
    >>> od = root['oobtodict']
    >>> list(od._dict_impl().keys(od))
    ['____lh', '____lt', 'bar', 'foo']
    
    >>> od.lt
    'bar'
    
    >>> od.lh
    'foo'
    
    >>> od
    OOBTodict([('foo', OOBTodict()), ('bar', OOBTodict())])
    
    >>> del root['oobtodict']

ZODBNode. Based on PersistentDict as storage::

    >>> from node.ext.zodb import IZODBNode
    >>> from node.ext.zodb import ZODBNode
    >>> zodbnode = ZODBNode('zodbnode')
    >>> zodbnode
    <ZODBNode object 'zodbnode' at ...>
    
    >>> IZODBNode.providedBy(zodbnode)
    True
    
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
    
    >>> del root['zodbnode']['child']
    
    >>> root['zodbnode'].printtree()
    <class 'node.ext.zodb.ZODBNode'>: zodbnode
    
    >>> root['zodbnode'].attrs
    <ZODBNodeAttributes object '_attrs' at ...>

    >>> root['zodbnode'].attrs['foo'] = 1
    >>> root['zodbnode'].attrs['bar'] = ZODBNode()
    >>> root['zodbnode'].attrs.values()
    [1, <ZODBNode object 'bar' at ...>]
    
    >>> transaction.commit()

Fill root with some ZODBNodes and check memory usage::

    >>> old_size = storage.getSize()
    
    >>> root['largezodb'] = ZODBNode('largezodb')
    >>> for i in range(1000):
    ...     root['largezodb'][str(i)] = ZODBNode()
    
    >>> len(root['largezodb'])
    1000
    
    >>> transaction.commit()

    >>> new_size = storage.getSize()
    >>> (new_size - old_size) / 1000
    139L

OOBTNode. Based on OOBTree as storage::

    >>> from node.ext.zodb import OOBTNode
    >>> oobtnode = OOBTNode('oobtnode')
    >>> oobtnode
    <OOBTNode object 'oobtnode' at ...>
    
    >>> IZODBNode.providedBy(oobtnode)
    True
    
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
    
    >>> del oobtnode['child']
    >>> transaction.commit()
    
    >>> oobtnode.printtree()
    <class 'node.ext.zodb.OOBTNode'>: oobtnode
    
    >>> oobtnode.attrs
    <OOBTNodeAttributes object '_attrs' at ...>

    >>> oobtnode.attrs['foo'] = 1
    >>> oobtnode.attrs['bar'] = OOBTNode()
    >>> oobtnode.attrs.values()
    [1, <OOBTNode object 'bar' at ...>]
    
    >>> oobtnode.attribute_access_for_attrs = True
    >>> oobtnode.attrs.foo
    1
    
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

Test copy and detach::

    >>> oobtnode['c1'] = OOBTNode()
    >>> oobtnode['c2'] = OOBTNode()
    >>> oobtnode['c3'] = OOBTNode()
    >>> oobtnode.printtree()
    <class 'node.ext.zodb.OOBTNode'>: oobtnode
      <class 'node.ext.zodb.OOBTNode'>: c1
      <class 'node.ext.zodb.OOBTNode'>: c2
      <class 'node.ext.zodb.OOBTNode'>: c3

Detach c1::

    >>> c1 = oobtnode.detach('c1')
    >>> c1
    <OOBTNode object 'c1' at ...>
    
    >>> oobtnode.printtree()
    <class 'node.ext.zodb.OOBTNode'>: oobtnode
      <class 'node.ext.zodb.OOBTNode'>: c2
      <class 'node.ext.zodb.OOBTNode'>: c3

Add c1 as child to c2::

    >>> oobtnode['c2'][c1.name] = c1
    >>> oobtnode.printtree()
    <class 'node.ext.zodb.OOBTNode'>: oobtnode
      <class 'node.ext.zodb.OOBTNode'>: c2
        <class 'node.ext.zodb.OOBTNode'>: c1
      <class 'node.ext.zodb.OOBTNode'>: c3

Commit and re-read::

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

Copy c1::

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

Swap nodes::

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

Calling nodes does nothing, persisting is left to transaction mechanism::

    >>> oobtnode()

Fill root with some OOBTNodes and check memory usage::

    >>> old_size = storage.getSize()
    
    >>> root['large'] = OOBTNode()
    >>> for i in range(1000):
    ...     root['large'][str(i)] = OOBTNode()
    
    >>> len(root['large'])
    1000
    
    >>> transaction.commit()

    >>> new_size = storage.getSize()
    >>> (new_size - old_size) / 1000
    136L

Test ``volatile_property``::

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

Cleanup test environment::

    >>> connection.close()
    >>> db.close()
    >>> import shutil
    >>> shutil.rmtree(tempdir)
