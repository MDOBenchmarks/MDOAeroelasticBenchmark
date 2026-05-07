#! /bin/bash
figureDir=$(pwd)
for d in */; do
    cd $d
    for file in Plot*.py; do
        echo "Running $file"
        python -OO $file
    done
    cd $figureDir
done
