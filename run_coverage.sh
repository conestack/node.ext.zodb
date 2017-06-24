#!/bin/sh
./$1/bin/coverage run -m node.ext.zodb.tests
./$1/bin/coverage report
./$1/bin/coverage html
