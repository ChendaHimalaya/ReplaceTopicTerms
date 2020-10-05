import xlrd
import pandas as pd
import sys
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
import numpy as np
from matplotlib import pyplot as plt


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

    vectorizer=TfidfVectorizer(analyzer='word',stop_words='english')
    countVectorizer=CountVectorizer(analyzer='word',stop_words='english')


    X=vectorizer.fit_transform(corpus)
    X2=countVectorizer.fit_transform(corpus)
    tfidf_tokens = vectorizer.get_feature_names()
    count_tokens= countVectorizer.get_feature_names()
    df_tfidfvect = pd.DataFrame(data=X.toarray(), columns=tfidf_tokens)
    df_count=pd.DataFrame(data=X2.toarray(),columns=count_tokens)
    print(vectorizer.get_feature_names())
    print(X.shape)
    print(df_tfidfvect[50:70])
    # print(countVectorizer.get_feature_names())
    # print(X2.shape)
    # print(df_count)

def compute_frequency(filename):
    df1=pd.read_csv(filename)
    corpus=df1['Review']
    countVectorizer = CountVectorizer(analyzer='word', stop_words='english')
    X2 = countVectorizer.fit_transform(corpus)
    count_tokens = countVectorizer.get_feature_names()
    df_count = pd.DataFrame(data=X2.toarray(), columns=count_tokens)
    sum_column=df_count.sum(axis=0)
    sum_column=sum_column.to_frame()
    np_sum=df_count.sum(axis=0).to_numpy()
    sum_column.columns=['count']
    sum_column=sum_column.sort_values(by=['count'])
    # with open('words_with_highest_frequency_'+filename,'a') as f:
    #     count_list=list(reversed(sum_column['count'].tolist()[-1000:]))
    #     word_list=list(reversed(sum_column.index.values[-1000:]))
    #     for i in range(len(count_list)):
    #         f.write(str(word_list[i])+":"+str(count_list[i])+'\n')
    #
    #     f.close()
    plt.figure(1)

    plt.hist(np_sum,bins=[i for i in range(25)])
    plt.title('Frequency in 1-25')
    plt.xlabel('Frequency')
    plt.ylabel('Count')
    plt.savefig(filename[0:-4]+'_frequency_1-25.png',dpi=240)
    plt.figure(2)

    plt.hist(np_sum, bins=[25+10*i for i in range(25)])
    plt.title('Frequency in 25-275')
    plt.savefig(filename[0:-4] + '_frequency_25-275.png', dpi=240)
    plt.figure(3)

    plt.hist(np_sum, bins=[275 + 100 * i for i in range(40)])
    plt.title('Frequency for 275+')
    plt.savefig(filename[0:-4] + '_frequency_275+.png', dpi=240)


    #print(sum_column.loc(sum_column[0].idmax()))

    #print(np.max(np_sum))


    #print(X)


def main():
    # translator=ReplaceTopicTerms("example_hotel.xlsx")
    # translator.update_gavagai_input_file("example_hotel.csv")
    # compute_tfidf("example_hotel.csv")
    # compute_tfidf("updated_example_hotel.csv")
    compute_frequency("example_hotel.csv")
    compute_frequency("updated_example_hotel.csv")


if __name__=='__main__':
    main()





