# -*- coding: utf-8 -*-
"""linear_policy_classifier.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xToz2E4saEEE9slP3gkSJz5gDl8kGaHz
"""

label = [[1, 'First Party Collection/Use'], 
              [2, 'Third Party Sharing/Collection'], 
              [3, 'User Choice/Control'], 
              [4, 'User Access, Edit and Deletion'], 
              [5, 'Data Retention'],
              [6, 'Data Security'],
              [7, 'Policy Change'], 
              [8, 'Do Not Track'],
              [9, 'International and Specific Audiences'],
              [10, 'Introductory/Generic'],
              [11, 'Privacy contact information'],
              [12, 'Privacy contact information']]

import os
import json
import csv
import pandas as pd
import nltk
from nltk.corpus import stopwords 
from nltk.stem.wordnet import WordNetLemmatizer
import string
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
import numpy as np
from sklearn.metrics import classification_report
from flask import Flask, request, render_template
import nltk
nltk.download('stopwords')


def readPolicyFile(fileLocation):
    policySegments = []
    for filename in os.listdir(fileLocation):
        absFilename = "{}/{}".format(fileLocation,filename)
        with open(absFilename) as csv_file:
            #print absFilename
            categoryId = 0
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if row[5] == "First Party Collection/Use":
                    categoryId = 1
                elif row[5] == "Third Party Sharing/Collection":
                    categoryId = 2
                elif row[5] == "User Choice/Control":
                    categoryId = 3
                elif row[5] == "User Access, Edit and Deletion":
                    categoryId = 4
                elif row[5] == "Data Retention":
                    categoryId = 5
                elif row[5] == "Data Security":
                    categoryId = 6
                elif row[5] == "Policy Change":
                    categoryId = 7
                elif row[5] == "Do Not Track":
                    categoryId = 8 
                elif row[5] == "International and Specific Audiences":
                    categoryId = 9
                elif row[5] == "Introductory/Generic":
                    categoryId = 10
                elif row[5] == "Privacy contact information":
                    categoryId = 11
                elif row[5] == "Practice not covered":
                    categoryId = 12
                else:
                    continue
                    
                policySegment = ''
                jsonData=json.loads(row[6])
                for (k, v) in jsonData.items():
                    for (k, v) in v.items():
                        if k == 'selectedText':
                            policySegment = ''.join(v)
                
                policySegments.append([policySegment, categoryId, row[5]])
            #print policySegments
            #print policySegments
    df = pd.DataFrame(policySegments, columns = ['text', 'label', 'label_name'])
    return df

def cleanDocs(dataFrame):
    cleanNull = dataFrame[df.text != 'null'].reset_index(drop=True)
    stop = set(stopwords.words('english'))
    exclude = set(string.punctuation) 
    lemma = WordNetLemmatizer()
    clean_docs = []
    bigram_docs = []
    for index, entry in enumerate(cleanNull['text']):
        stop_free = " ".join([i for i in entry.lower().split() if i not in stop])
        punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
        digit_free = [word for word in punc_free.split() if not word.isdigit() and len(word) > 2]
        normalized = " ".join(lemma.lemmatize(word) for word in digit_free)
        nouns = [word[0] for word in nltk.pos_tag(normalized.split()) if word[1] == 'NN' or word[1] == 'VB']
        cleanNull.loc[index,'text_final'] = str(nouns)

	#bigram_transformer = phrases.Phrases(clean_docs)
	
	#for doc in bigram_transformer[clean_docs]:
	#		bigram_docs.append(doc)
    cleanEmpty = cleanNull[cleanNull.text_final != '[]']
    return cleanEmpty

def loadTestDataset(fileName):
    df = pd.read_csv(fileName)
    return df

def buildModel(Corpus):
    Train_data, Test_data, Train_label, Test_label = train_test_split(Corpus['text_final'],Corpus['label'],test_size=0.3)
    #Encoder = preprocessing.LabelEncoder()
    #Train_label = Encoder.fit_transform(Train_label)
    #Test_label = Encoder.fit_transform(Test_label)
    Tfidf_vect = TfidfVectorizer(max_features=5000)
    Tfidf_vect.fit(Corpus['text_final'])
    Train_data_Tfidf = Tfidf_vect.transform(Train_data)
    Test_data_Tfidf = Tfidf_vect.transform(Test_data)
    
#     print(Tfidf_vect.vocabulary_)
    
    # fit the training dataset on the NB classifier
#     Naive = MultinomialNB()
#     Naive.fit(Train_data_Tfidf,Train_label)
#     # predict the labels on validation dataset
#     predictions_NB = Naive.predict(Test_data_Tfidf)
#     # Use accuracy_score function to get the accuracy
#     print(classification_report(Test_label, predictions_NB))
#     print("Naive Bayes Accuracy Score -> ",accuracy_score(predictions_NB, Test_label)*100)
    
    # Classifier - Algorithm - SVM
    # fit the training dataset on the classifier
    SVM = SVC(C=1.0, kernel='linear', degree=3, gamma='auto')
    SVM.fit(Train_data_Tfidf,Train_label)
    # predict the labels on validation dataset
    predictions_SVM = SVM.predict(Test_data_Tfidf)
    #print Test_data_Tfidf
    #print predictions_SVM
    # Use accuracy_score function to get the accuracy
    print(classification_report(Test_label, predictions_SVM))
    print("SVM Accuracy Score -> ",accuracy_score(predictions_SVM, Test_label)*100)
    
    
    return SVM

def predictLable(model, corpus):
    print (corpus)
    Tfidf_vect = TfidfVectorizer(max_features=5000)
    Tfidf_vect.fit(corpus['text_final'])
    webPolicy_TFidf = Tfidf_vect.transform(corpus['text_final'])
    webPolicyPredition = model.predict(webPolicy_TFidf)
    
    return webPolicyPredition

def mergeData(corpus, predictedResult):
    labels = [[1, 'First Party Collection/Use'], 
              [2, 'Third Party Sharing/Collection'], 
              [3, 'User Choice/Control'], 
              [4, 'User Access, Edit and Deletion'], 
              [5, 'Data Retention'],
              [6, 'Data Security'],
              [7, 'Policy Change'], 
              [8, 'Do Not Track'],
              [9, 'International and Specific Audiences'],
              [10, 'Introductory/Generic'],
              [11, 'Privacy contact information'],
              [12, 'Privacy contact information']]
    
    dfLabel = pd.DataFrame(labels, columns=['label', 'discription'])
    dfPredictedResult = pd.DataFrame(predictedResult)
    dfContact = pd.concat([corpus, dfPredictedResult], axis=1)
    dfContact.columns = ['topic_number', 'corpus', 'label'] 
    return pd.merge(dfContact, dfLabel, on='label')

nltk.download('averaged_perceptron_tagger')

np.random.seed(500)
fileLocation = r'C:\Users\mamta\Downloads\ARCHIT_SANKALP\OPP-115_v1_0\OPP-115\annotations'

df = readPolicyFile(fileLocation)
Corpus = cleanDocs(df)
print (Corpus['label_name'].unique())
Corpus.to_csv('clean_OOP-115_policy_corpus.csv', index=False)
model = buildModel(Corpus)

# webPolicyCorpus = loadTestDataset('topic_10_only_nouns_n_verb_run_1.csv')
# gdprPolicyCorpus = loadTestDataset('topic_10_gdpr_only_nouns_n_verb_run_1.csv')

# webPolicyPrediction = predictLable(model, webPolicyCorpus)
# gdprPolicyPrediction = predictLable(model, gdprPolicyCorpus)

# mergeData(webPolicyCorpus, webPolicyPrediction)

"""
import pandas as pd
d={"text":["personal and other information that may be collected when you interact with the Barnes & Noble enterprise,"]}
corpus=pd.DataFrame(d)
corpus.to_csv("out.csv",index=False)
"""





app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    
  try:

    corpus = loadTestDataset('/content/input.csv')
    print(corpus)

    k= predictLable(model, cleanDocs(corpus))

    l= list(k)
  except:
    output = 'A'
  return render_template('index.html', prediction_text='OUTPUT =  {}'.format(output))

if __name__ == "__main__":
    app.run(debug=True)
