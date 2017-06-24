#!/bin/sh
if [ -x "$(which python)" ]; then
    ./py2_zodb3/bin/python -m unittest node.ext.zodb.tests
    ./py2_zodb5/bin/python -m unittest node.ext.zodb.tests
fi
if [ -x "$(which python3)" ]; then
    ./py3_zodb5/bin/python -m unittest node.ext.zodb.tests
fi
