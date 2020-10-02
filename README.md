# ReplaceTopicTerms

Create a ReplaceTopicTerms object with argument of a gavagai export excel report
translator=ReplaceTopicTerms(gavagai_excel_filename:String)
Add more mappings by providing extra excel reports
translator.load_mapping_gavagai(filename)
Translate one sentence:
translator.replace_one_review(sentence:String)
Translate a Gavagai explorer input csv file:
translator.update_gavagai_input_file(filename:String)
