import xlrd
import pandas as pd
import sys
from sklearn.feature_extraction.text import TfidfVectorizer


class ReplaceTopicTerms:
    '''Used for replacing words with their coresponding topics in a sentence/file of sentences/Gavagai input file  '''
    def __init__(self,gavagai_export_file):
        self.map_table=[{} for i in range(4)] #Mapping table for word with size 1,2,3 and >3
        self.load_mapping_gavagai(gavagai_export_file)

    def load_mapping_gavagai(self,gavagai_export_file):
        '''Create mappings using Gavagai export excel file, with default options
            Input:String| filepath to the Gavagai export file path
            Output:List of Integers |Number of words in each mapping table'''
        summary_sheet=pd.read_excel(gavagai_export_file,sheet_name="Summary")
        topics=summary_sheet['Label'].tolist()
        terms=summary_sheet['Terms'].tolist()
        for i in range(len(topics)):
            topic=topics[i]

            term=terms[i].split(", ") if type(terms[i])==type('s') else []
            for word in term:
                word_len=len(word.split(" "))
                index=word_len-1 if word_len<=3 else 3
                self.map_table[index][word]=topic



        return [len(self.map_table[i]) for i in range(4)]
    def replace_one_review(self,sentence):
        '''Replace words that matches any of the terms in the mapping table
            Input:String |A senetence that needs to be updated
            Output:String  |the sentence with all possible replacements have been done'''
        if sentence=="" or sentence==" ":
            return sentence
        for mapping_table in reversed(self.map_table):
            for key in mapping_table:
                if key in sentence.lower():
                    return self.replace_one_review(sentence.lower().split(key,1)[0])+mapping_table[key]+self.replace_one_review(sentence.lower().split(key,1)[1])
        return sentence

    def update_gavagai_input_file(self,gavagai_input_file,output_name=None):
        '''Update all the reviews/sentences in the default Gavagai explorer input csv file
            Input: String| file path to the input file
            Output:Bool |True if a new file is generated, False otherwise
            '''

        if output_name==None:
            output_name="updated_"+gavagai_input_file

        try:
            with open(gavagai_input_file,'r') as f:
                f_write = open(output_name, 'a')
                s=f.readlines()
                f_write.write(s[0])   #Skip first row
                f_write.close()
                for line in s[1:]:
                    f_write = open(output_name, 'a')
                    f_write.write(self.replace_one_review(line))
                    f_write.close()
                f.close()
                return True
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return False

def compute_tfidf(filename):
    df1=pd.read_csv(filename)
    corpus=df1['Review']

    vectorizer=TfidfVectorizer()
    X=vectorizer.fit_transform(corpus)
    print(vectorizer.get_feature_names())
    print(X.shape)
    #print(X)

def main():
    translator=ReplaceTopicTerms("empty_entry.xlsx")
    translator.update_gavagai_input_file("example_hotel.csv")
    compute_tfidf("example_hotel.csv")
    compute_tfidf("updated_example_hotel.csv")



if __name__=='__main__':
    main()





