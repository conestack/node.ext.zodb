Changes
=======

1.6 (2022-12-05)
----------------

- Pass ``name`` and ``parent`` as keyword arguments all over the place.
  Preparation for use of ``NodeInit`` behavior instead of ``DefaultInit``.
  [rnix]


1.5 (2022-03-21)
----------------

- Replace deprecated use of ``Storage`` by ``MappingStorage``.
  [rnix]

- Replace deprecated use of ``Nodify`` by ``MappingNode``.
  [rnix]

- Replace deprecated use of ``Adopt`` by ``MappingAdopt``.
  [rnix]

- Replace deprecated use of ``NodeChildValidate`` by ``MappingConstraints``.
  [rnix]

- Replace deprecated use of ``allow_non_node_childs`` by ``child_constraints``.
  [rnix]


1.4 (2021-10-21)
----------------

- Implement ``_list_factory`` on ``Podict`` and ``OOBTodict`` and use
  ``PersistentList`` for internal double linked list triples to allow
  transaction property detect changes.
  [rnix, jensens]

- Drop ZODB3.
  [rnix]


1.3 (2020-07-09)
----------------

- Access ``attrs`` when initializing nodes with ``ZODBAttributes`` behavior
  applied to avoid lazy creation. Needed to prevent ``_p_changed`` being set on
  first access.
  [rnix, 2020-06-23]

- Access ``storage`` when initializing nodes with ``PodictStorage`` or
  ``OOBTodictStorage`` behaviors applied to avoid lazy creation. Needed
  to prevent ``_p_changed`` being set on first access.
  [rnix, 2020-06-23]

- Use ``plumb`` instead of overriding ``__setattr__`` to change ``__parent__``
  name to ``_v_parent`` on ``ZODBBehavior``.
  [rnix, 2020-06-23]

- Use ``plumb`` instead of overriding ``__getitem__`` to set parent on
  ``ZODBBehavior``.
  [rnix, 2020-02-28]


1.2 (2017-07-18)
----------------

- Add python 3 support.
  [rnix, 2017-06-24]

- Add ``keys`` to ``OOBTodict`` and accept any number of ``*args`` and ``**kw``
  to match expected contract by ``OOBTree`` and Fix tests with ZODB 5.
  [rnix, 2017-06-22]

- Add ``__nonzero__`` and ``__bool__`` to ``OOBTodict`` in order to make it
  work properly with ZODB 5.
  [rnix, 2017-06-22]

- Use ``@property`` and ``@property.setter`` for ``OOBTodict.lh`` and
  ``OOBTodict.lt``.
  [rnix, 2017-06-22]


1.1.1
-----

- Change ``ZODB`` install requirement to ``ZODB3``. Latter one is a meta
  package as of version 3.11.0 and installs ``ZODB``
  [rnix, 2017-06-19]


1.1
---

- Remove superfluous ``__repr__`` function from ``OOBTodict``. ``odict``
  package properly outputs class name as of version 1.6.2.
  [rnix, 2017-06-14]

- Fix ``volatile_property`` to work on classes overwriting ``__getattr__``.
  [rnix, 2017-06-14]

- Use ``plumbing`` decorator instead of ``__metaclass__`` and ``__plumbing__``
  class attributes.
  [rnix, 2017-06-14]


1.0.1
-----

- Add maintenance utilities.
  [rnix, 2014-05-13]

- Cleanup tests.
  [rnix, 2014-05-13]


1.0
---

- initial
  [rnix]
