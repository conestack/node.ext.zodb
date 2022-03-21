#!/bin/bash

function run_coverage {
    local target=$1

    if [ -e "$target" ]; then
        ./$target/bin/coverage run \
            --source=src/node/ext/zodb \
            -m node.ext.zodb.tests
        ./$target/bin/coverage report
    else
        echo "Target $target not found."
    fi
}

run_coverage py2
run_coverage py3
