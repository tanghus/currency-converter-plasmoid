#! /usr/bin/env bash
# simplified version of a script by Petri Damstén.

. ../PACKAGE

if [ "x$1" != "x" ]; then
    if [ ! -d "locale/$1" ]; then
        mkdir -p "locale/$1/LC_MESSAGES"
    fi
fi

# Create template file
echo "Extracting messages"
echo "Creating $NAME.pot file..."
xgettext --from-code=UTF-8 --package-version="$VERSION" --no-wrap --copyright-holder="$AUTHOR" \
  --default-domain="$NAME" --package-name="$NAME" --msgid-bugs-address="$EMAIL" \
  -ki18n -ki18np:1,2 -ki18nc:1c,2 -ki18ncp:1c,2,3 -o ./$NAME.pot code/*.py

# Fixing header (there must be a better way to do this)
echo "Fixing header information..."
sed -e 's/charset=CHARSET/charset=UTF-8/g' -i "$NAME.pot"

echo "Merging translations"
for d in locale/*; do
    if [ -d "$d" ]; then
        if [ -f "$d/LC_MESSAGES/$NAME.po" ]; then
            echo "Merging $NAME.pot -> $d/LC_MESSAGES/$NAME.po ..."
            msgmerge -U "$d/LC_MESSAGES/$NAME.po" "$NAME.pot"
        else
            echo "Copying $NAME.pot -> $d/LC_MESSAGES/$NAME.po ..."
            cp "$NAME.pot" "$d/LC_MESSAGES/$NAME.po"
        fi
    fi
done

for d in locale/*; do
    echo "Making $d/LC_MESSAGES/$NAME.mo ..."
    msgfmt "$d/LC_MESSAGES/$NAME.po" -o "$d/LC_MESSAGES/$NAME.mo"
done

#rm -f $NAME.pot

echo "Done!"