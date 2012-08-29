``node.ext.zodb`` is a persistent `node <http://pypi,python.org/pypi/node>`_ 
implemenatation for the `ZODB <http://www.zodb.org>`_. 

With node a unified robust tree structure can be build and with this package 
this structures can be persistet easily.

It provides two implementation types:

- ``node.ext.zodb.ZODBNode`` based on ``persistent.dict.PersistentDict``,
- ``node.ext.zodb.OOBTNode`` based on ``BTrees.OOBTree.OOBTree``.

Usage
=====

First a open DB connection is needed. This may be a naked ZODB install or 
in an context of `Pyramid <http://docs.pylonsproject.org/en/latest/docs/pyramid.html>`_
or `Zope2 <http://zope2.zope.org/>`_/ `Plone <http://plone.org>`_ or where ever 
it makes sense for you.

Once the DB ``root`` object or any other contained persistent object is available 
adding nodes is as simple as so::

    >>> from node.ext.zodb import ZODBNode
    >>> root['person'] = ZODBNode()
    >>> root['person'].attrs['name'] = "Willi"
    >>> root['person']['home'] = ZODBNode()
    >>> root['person']['home'].attrs['address'] = "Innsbruck, Austria"
    >>> root['person']['work'] = ZODBNode()
    >>> root['person']['work'].attrs['address'] = "Hall in Tirol, Austria"

Once the transaction is committed al changes are persistent.

For more information on ``node`` and its usage please refer to the 
`node documentation <http://pypi.python.org/pypi/node>`_.

Source Code
===========

The sources are in a GIT DVCS with its main branches at
`github <http://github.com/bluedynamics/node.ext.zodb>`_.

We'd be happy to see many forks and pull-requests to make it even better.

Contributors
============

- Robert Niederreiter <rnix@squarewave.at>

- Jens Klein <jk@kleinundparter.at>



