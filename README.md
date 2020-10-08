# ReplaceTopicTerms

This project provides tool for word replacement for a Gavagai import csv file
using a map table generated with a Gavagai Explorer output filename

##How to use
e.g. `python3 ReplaceTopicTerms.py -m gavagai_export_file.xlsx -f file_tobe_updated.csv -c Review -l english`

##Arguments
### -f --filename
filepath of the csv file to be updated
### -m --mappingfile
filepath to the gavagai export xlsx file that is used for generating
the mapping table
### -l --language
Language of the stop words
### -o -outdir
Directory path for the result file/plots to be stored
### -c --column
Target Column to be analyzed(Default:Review)