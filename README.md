# ReplaceTopicTerms

Create a ReplaceTopicTerms object with argument of a gavagai export excel report\n
translator=ReplaceTopicTerms(gavagai_excel_filename:String)\n
Add more mappings by providing extra excel reports\n
translator.load_mapping_gavagai(filename)\n
Translate one sentence:\n
translator.replace_one_review(sentence:String)\n
Translate a Gavagai explorer input csv file:\n
translator.update_gavagai_input_file(filename:String)\n
