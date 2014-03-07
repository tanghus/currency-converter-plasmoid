#!/bin/sh
ui_files=`ls *.ui`
echo $ui_files

# for ui in $ui_files;
#   do
#     echo $ui
#     pykdeuic4 currency_converter_config.ui > ../code/currency_converter_config_ui.py
#   done


for ui in $ui_files;
  do
    pykdeuic4 $ui >  ../code/`echo $ui|cut -d. -f1`_ui.py
  done
