
History
=======

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
