#!/bin/bash

if [ -x "$(which python)" ]; then
    rm -r py2_zodb3

    virtualenv --clear --no-site-packages -p python py2_zodb3

    ./py2_zodb3/bin/pip install coverage
    ./py2_zodb3/bin/pip install zope.interface
    ./py2_zodb3/bin/pip install zope.lifecycleevent
    ./py2_zodb3/bin/pip install zope.component
    ./py2_zodb3/bin/pip install zope.deprecation
    ./py2_zodb3/bin/pip install ZODB3==3.10.7
    ./py2_zodb3/bin/pip install https://github.com/bluedynamics/odict/archive/master.zip
    ./py2_zodb3/bin/pip install https://github.com/bluedynamics/plumber/archive/master.zip
    ./py2_zodb3/bin/pip install https://github.com/bluedynamics/node/archive/master.zip
    ./py2_zodb3/bin/pip install -e .

    rm -r py2_zodb5

    virtualenv --clear --no-site-packages -p python py2_zodb5

    ./py2_zodb5/bin/pip install coverage
    ./py2_zodb5/bin/pip install zope.interface
    ./py2_zodb5/bin/pip install zope.lifecycleevent
    ./py2_zodb5/bin/pip install zope.component
    ./py2_zodb5/bin/pip install zope.deprecation
    ./py2_zodb5/bin/pip install ZODB3==3.11.0
    ./py2_zodb5/bin/pip install https://github.com/bluedynamics/odict/archive/master.zip
    ./py2_zodb5/bin/pip install https://github.com/bluedynamics/plumber/archive/master.zip
    ./py2_zodb5/bin/pip install https://github.com/bluedynamics/node/archive/master.zip
    ./py2_zodb5/bin/pip install -e .
fi
if [ -x "$(which python3)" ]; then
    rm -r py3_zodb5

    virtualenv --clear --no-site-packages -p python3 py3_zodb5

    ./py3_zodb5/bin/pip install coverage
    ./py3_zodb5/bin/pip install zope.interface
    ./py3_zodb5/bin/pip install zope.lifecycleevent
    ./py3_zodb5/bin/pip install zope.component
    ./py3_zodb5/bin/pip install zope.deprecation
    ./py2_zodb5/bin/pip install ZODB3==3.11.0
    ./py3_zodb5/bin/pip install https://github.com/bluedynamics/odict/archive/master.zip
    ./py3_zodb5/bin/pip install https://github.com/bluedynamics/plumber/archive/master.zip
    ./py3_zodb5/bin/pip install https://github.com/bluedynamics/node/archive/master.zip
    ./py3_zodb5/bin/pip install -e .
fi
