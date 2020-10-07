import xlrd
import pandas as pd
import sys
import os
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
import numpy as np
from matplotlib import pyplot as plt


class ReplaceTopicTerms:
    '''Used for replacing words with their coresponding topics in a sentence/file of sentences/Gavagai input file  '''
    def __init__(self,gavagai_export_file):
        self.map_table=[{} for i in range(4)] #Mapping table for word with size 1,2,3 and >3
        self.vocabulary = []
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
                self.vocabulary.append(word)



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

    def update_gavagai_input_file(self,gavagai_input_file,target_column="Review",output_name=None,generate_report=True):
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
                if generate_report:
                    self.generate_report(gavagai_input_file,output_name,target_column)
                return True
        except:
            print("Unexpected error:", sys.exc_info())
            return False



    def reverse_mapping(self):
        '''Internal Use, create inversed mapppings'''
        reverse_map={}
        for map in self.map_table:
            for key in map:
                if map[key] in reverse_map.keys():
                    reverse_map[map[key]].append(key)
                else:
                    reverse_map[map[key]]=[key]
        return reverse_map

    def generate_report(self,original_file,updated_file,target_column):
        '''Generate report that compares the original file and the updated file, using words in the existed mapping table
            Input:Strings|
            Output:Bool|'''
        if not os.path.exists('Result'):
            os.makedirs('Result')
        filelist=[original_file,updated_file]
        self.export_frequency(filelist,target_column,outpath='Result/',legends=["Original","Updated"])

        reverse_map=self.reverse_mapping()
        tfidf_original = self.compute_tfidf(original_file, target_column)
        #tfidf_original.replace(0,np.NaN)
        tfidf_updated = self.compute_tfidf(updated_file, target_column)
        #tfidf_updated.replace(0,np.NaN)
        for key in reverse_map:
            key_array=tfidf_original[key]
            topic_value=[key_array.mean(),key_array.max(),key_array[key_array>0].min()]
            original_value=[]
            for item in reverse_map[key]:
                item_array=tfidf_updated[item]
                temp=[item_array.mean(),item_array.max(),item_array[item_array>0].min()]
                original_value.append(item+":"+str(temp))



            with open('Result/tfidf_summary_'+original_file[0:-4]+'.txt','a') as f:
                f.write("After Update:"+key+str(topic_value))
                f.write('\n')
                f.write(",".join(original_value))
                f.write('\n')
                f.close()




    def add_vacab(self,old_vocab):
        for word in self.vocabulary:
            if word in old_vocab:
                continue
            else:
                old_vocab.append(word)
        return old_vocab





    def compute_tfidf(self,filename,target_column,voc=None):
        '''Internal Use, compute tf-idf matrix
        filename:String|file path to the input file
        target_column:String|The column name of the texts that is going to be analyzed'''
        if not voc:
            voc=self.vocabulary
        df1=pd.read_csv(filename)
        corpus=df1[target_column]
        vectorizer=TfidfVectorizer(analyzer='word',stop_words='english')
        X=vectorizer.fit_transform(corpus)
        full_vocab=vectorizer.get_feature_names()
        full_vocab=self.add_vacab(full_vocab)
        vectorizer = TfidfVectorizer(analyzer='word', stop_words='english',vocabulary=full_vocab)
        X = vectorizer.fit_transform(corpus)
        tfidf_tokens=vectorizer.get_feature_names()
        print(tfidf_tokens)
        df_tfidf=pd.DataFrame(data=X.toarray(),columns=tfidf_tokens)
        print(df_tfidf)

        return df_tfidf

    def compute_frequency(self,filename,target_column):
        '''Internal Use, compute word frequency
        filename:String|file path to the input file
        target_column:String|The column name of the texts that is going to be analyzed
        returns a pandas dataframe of the count matrix'''
        df1 = pd.read_csv(filename)
        corpus = df1['Review']
        countVectorizer = CountVectorizer(analyzer='word', stop_words='english')
        X2 = countVectorizer.fit_transform(corpus)
        count_tokens = countVectorizer.get_feature_names()
        df_count = pd.DataFrame(data=X2.toarray(), columns=count_tokens)
        return df_count
    def sort_column(self,column):
        column.columns=['count']
        return column.sort_values(by="count")

    def export_frequency(self,filelist,target_column,outpath=None,bin_intervals=None,legends=None):
        '''Generate export files that compares the word frequency between the original csv file and updated one
            filelist:list(Strings)|iterable of path of filenames that needed to be ploted
            target_column:String|The column name of the texts that is going to be analyzed
            outpath:String|Export directory
            bin_interval:List of lists|List of bin intervals
            legends:List of Strings|Legends used for the plots'''
        if not outpath:
            outpath='Result/'
        #sum_columns=[]
        np_sums=[]
        for filename in filelist:
            df=self.compute_frequency(filename,target_column)
            #sum_columns.append(self.sort_column(df.sum(axis=0).to_frame()))
            np_sums.append(df.sum(axis=0).to_numpy())
            sum_column=self.sort_column(df.sum(axis=0).to_frame())
            with open(outpath+'words_with_highest_frequency_'+filename[0:-4]+".txt",'a') as f:
                count_list=list(reversed(sum_column['count'].tolist()[-1000:]))
                word_list=list(reversed(sum_column.index.values[-1000:]))
                for i in range(len(count_list)):
                    f.write(str(word_list[i])+":"+str(count_list[i])+'\n')

                f.close()
        if not bin_intervals:
            #Todo Maybe a smarter algorithm on deciding the intervals
            bin_intervals=[[i for i in range(25)],[25+i*10 for i in range(25)],[250+i*100 for i in range(25)]]
        figure_count=-1

        for bin_interval in bin_intervals:
            figure_count += 1
            for index,filename in enumerate(filelist):
                plt.figure(figure_count)
                plt.hist(np_sums[index],bins=bin_interval,alpha=0.3)
                plt.xlabel("Frequency")
                plt.ylabel('Count')
                plt.title("Frequency from {} to {}".format(np.min(bin_interval),np.max(bin_interval)))
            if legends:
                plt.legend(legends)
            else:
                plt.legend([filelist[i][0:-4] for i in range(len(filelist))])
            plt.savefig(outpath+"frequency_plot_from {} to {}.png".format(np.min(bin_interval),np.max(bin_interval)),dpi=240)

def main():
    translator=ReplaceTopicTerms("example_hotel.xlsx")
    translator.update_gavagai_input_file("example_hotel.csv")




if __name__=='__main__':
    main()





