#!/bin/bash
. PACKAGE
echo "Creating Plasmoid package: $NAME-$VERSION.plasmoid"
zip -r ../$NAME-$VERSION.plasmoid . -x@zip_excluded.lst
