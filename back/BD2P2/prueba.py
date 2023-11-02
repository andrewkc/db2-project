import pandas as pd
import sys
import json
from operator import itemgetter
from collections import OrderedDict, defaultdict
import math
import numpy as np
import nltk
from nltk.stem.snowball import SnowballStemmer
import os
import time

stemmer = SnowballStemmer('english')
nltk.download('punkt')


def compute_term_frequency(collection):
    document_term_frequencies = {}
    total_term_frequencies = {}

    for document_id, document in enumerate(collection):
        term_frequencies = {}

        for term in document:
            if term in term_frequencies:
                term_frequencies[term] += 1

            if term in total_term_frequencies:
                total_term_frequencies[term] += 1
            else:
                total_term_frequencies[term] = 1

        document_term_frequencies[document_id] = term_frequencies

    sorted_total_term_frequencies = sorted(total_term_frequencies.items(), key=lambda item: item[1], reverse=True)

    return document_term_frequencies, sorted_total_term_frequencies

def compute_idf(term, idf_freq, term_freq, N):
    if term in idf_freq: #si ya existe para term
        idf = idf_freq[term]
    else:
        df = 0 #en cuantos docs aparece term
        for num in range(N):
            if term in term_freq[num]:
                df += 1
        if df == 0:
            idf = 0
        else:
            idf = np.log10((N / df))
        idf_freq[term] = idf
    return idf

#Para querys
def calculate_tf(query, document):
    term_frequency = document.count(query)
    return (1+math.log10(term_frequency))

def calculate_idf(query, documents):
    document_frequency = sum(1 for document in documents if query in document)
    return math.log(len(documents) / (document_frequency + 1))

def compute_tfidf(data, collection):
    tfidf = {} #para tener score tfidf
    idf_freq = {} #se va updateando cada vez que se saque idf de una palabra, para no recalcular
    index = {} #para tener
    length = {} #para tener vector normalizado de cada abstract

    term_freq, orden_keywords = compute_term_frequency(collection) # Contar la frecuencia de cada término en cada documento

    for doc_id, doc in enumerate(collection):
        nameDoc = str(data.iloc[int(doc_id),0])
        smoothed_tf = []

        for tup_term in orden_keywords:
            term = tup_term[0]
            #compute index
            if term in term_freq[doc_id]:
                tf_t_d = term_freq[doc_id][term]
                if term_freq[doc_id][term] != 0:
                    if term in index:
                        index[term].append((nameDoc, tf_t_d))
                    else:
                        index[term] = [(nameDoc, tf_t_d)]
                #Term Frequency + Smoothing
                tf = np.log10(tf_t_d +1)
                idf = compute_idf(term, idf_freq, term_freq, len(collection))
                smoothed_tf.append(round(tf * idf, 3))
            else:
                smoothed_tf.append(0)

        #compute length
        array = np.array(list(smoothed_tf))
        length[nameDoc] = np.linalg.norm(array)
        tfidf[nameDoc] = smoothed_tf

    #create_inverted_index(tfidf) esto no es el inverted index

    return length, idf_freq, index

def idf(doc_freq, n_docs):
    N = n_docs
    df = doc_freq
    return round(math.log10((N/df)+1),4)

def tf_idf(freq, doc_freq, n_docs):
    if doc_freq == 0: #si aparece
        return 0
    tf = 1+math.log10(freq)
    idf_ = idf(doc_freq, n_docs)

    return round(tf*idf_,4)

def tokenizar(texto):
    texto = texto
    tokens = nltk.word_tokenize(texto)
    tokenText = nltk.Text(tokens).tokens
    return tokenText

def eliminarStopWords(tokenText):
    print(os.getcwd())
    customSW = open(os.path.join(os.path.dirname(__file__), 'stop_words_spanish.txt'), 'r')
    palabras_stoplist = customSW.read()
    customSW.close()
    palabras_stoplist = nltk.word_tokenize(palabras_stoplist.lower())
    resultado = [stemmer.stem(token) for token in tokenText if (token not in palabras_stoplist)]
    lstTokens = []
    for token in resultado:
        bandera = False
        for word in palabras_stoplist:
            if word in token:
                bandera = True
                break
        if bandera == False:
            lstTokens.append(token)

    return lstTokens

def preprocesar_textos(texto):
    tokenText = tokenizar(texto.lower())
    tokensLst = eliminarStopWords(tokenText)

    return tokensLst

base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "definitivo.csv")
path_index = os.path.join(base_dir, "spimi.txt")
blocks_dir = os.path.join(base_dir, "bloques")


ZERO_TRESHOLD = 0.000001

class InvertIndex:
    def __init__(self, index_file, abstracts_por_bloque=10000, dataFile=""):
        self.index_file = index_file
        self.index = {}
        self.idf = {}
        self.length = {}
        self.BLOCK_LIMIT = abstracts_por_bloque
        self.lista_de_bloques = []
        self.data_path = data_path  # Updated data path
        self.path_index = path_index  # Updated path to index file


    def loadData(self):
        data = pd.read_csv(self.data_path)
        data["id"] = data["id"].astype(str)
        return data

    def SPIMIConstruction(self, n):
        data = self.loadData().head(n)

        dictTerms = defaultdict(list)
        block_n = 1

        for idx, row in data.iterrows():
            if idx % 20000 == 0: print("Estamos en el index ", idx)
            abstract = row["concatenated"]
            docID = row["id"]
            tokensAbstract = preprocesar_textos(abstract)
            #Crear postingList
            term_freq = defaultdict(int)
            for term in tokensAbstract:
                term_freq[term] += 1

            for term, freq in term_freq.items():
                if sys.getsizeof(dictTerms) > self.BLOCK_LIMIT:
                    sorted_block = sorted(dictTerms.items(), key=itemgetter(0))
                    block_name = "bloque-"+str(block_n)+".txt"
                    block_path = os.path.join(blocks_dir, block_name)
                    with open(block_path, "w") as file_part:
                        json.dump(sorted_block, file_part, indent=2)
                    sorted_block = {} #clear
                    block_n += 1
                    dictTerms = defaultdict(list) #clear
                dictTerms[term].append((docID, freq))

        if dictTerms:
            sorted_block = sorted(dictTerms.items(), key=itemgetter(0))
            block_name = "bloque-"+str(block_n)+".txt"
            block_path = os.path.join(blocks_dir, block_name)
            with open(block_path, "w") as file_part:
                json.dump(sorted_block, file_part, indent=2)
            dictTerms = defaultdict(list)

    def listFiles(self):
        filepaths = blocks_dir
        files = []

        for file_name in os.listdir(filepaths):
            file_path = os.path.join(filepaths, file_name)
            if os.path.isfile(file_path):
                files.append(file_path)
        return files #list of pathnames

    def merge(self, block1, block2):
        merge_final = OrderedDict()

        for term, ids in block1.items():
            if term in merge_final:
                merge_final[term]+= ids
            else:
                merge_final[term] = ids

        for term, ids in block2.items():
            if term in merge_final:
                merge_final[term]+= ids
            else:
                merge_final[term] = ids
        bloque_ordenado = OrderedDict(sorted(merge_final.items(), key=lambda x: x[0]))

        return bloque_ordenado

    def write_index_tf_idf(self, inverted_dict, n_documents):
        with open(self.path_index, "w") as index:
            for term, ids in inverted_dict.items():
                docFrec = len(ids) #en cuantos docs aparece?
                index.write(f"{term}:")
                for doc_tf_id in ids:
                    doc_id = doc_tf_id[0]
                    tf = doc_tf_id[1]
                    termdoc_tfidf = tf_idf(tf, docFrec, n_documents)

                    index.write(f"{doc_id},{termdoc_tfidf};")
                index.write("\n")

    def write_index(self, inverted_dict, filename):
        with open(filename, "w") as index:
            for term, ids in inverted_dict.items():
                index.write(f"{term}:{ids};")
                index.write("\n")

    #Se encarga de hacer el merge de blocks, e indexar
    def index_blocks(self):
        blocks = []
        files = self.listFiles()
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as file:
                block = json.load(file)
                blocks.append(block)


        while 1 < len(blocks):
            merged_blocks = []
            for i in range(0,len(blocks), 2):
                if i+1 <len(blocks): #si ya no hay mas con que agarrar, o sea el ultimo
                    combinados = self.merge(dict(blocks[i]), dict(blocks[i+1]))
                    merged_blocks.append(combinados)
                else:#solo append al final
                    merged_blocks.append(blocks[i])
            blocks = merged_blocks #actualiza el nuevo merge
        ordenar_merge = OrderedDict(sorted(blocks[0].items(), key=lambda x: x[0]))

        return ordenar_merge

    #QUERY
    def cos_Similarity(self, query, cosine_docs):
        cosine_scores = defaultdict(float)
        for docId in cosine_docs:
            doc = cosine_docs[docId]
            q = query
            sum_ = 0
            sum_ += round(np.dot(q/(np.linalg.norm(q)),doc/(np.linalg.norm(doc))),5)
            cosine_scores[docId] = sum_
        return cosine_scores

    def load_Index(self):
        result = []
        with open(self.path_index, 'r') as file:
            document = file.read()

            lines = document.split('\n')
            for line in lines:
                if line:
                    key, posting_list = line.split(':', 1)
                    result.append((key, posting_list)) #linea de strings, key con posting_list en string
        return result

        #IMPLEMENTAR BINARY!
    #Index Data es cada linea del documento como un set Term, postinglist
    #siendo postinglist toda una string de docId, tf_idf; docId2, tf_idf;
    def binary_search(self, term, index_data):
        left = 0
        right = len(index_data) - 1
        while left <= right:
            mid = (left + right) // 2
            current_term = index_data[mid][0]
            if current_term == term:
                return index_data[mid][1].split(";")[:-1]
            elif term < current_term:
                right = mid - 1
            else:
                left = mid + 1

        return None

    #Sequential Search on Index
    def loop(self, term, index_data):
        for data in index_data:
            term_index = data[0]
            docId_scores = data[1]
            if term_index == term:
                return docId_scores.split(";")[:-1]
        return None

    def retrieve_k_nearest(self, query, k):
        start_time = time.time()
        data = self.loadData()
        query = preprocesar_textos(query)
        index_data = self.load_Index()
        cos_to_evaluar = defaultdict(dict)
        idf_query=defaultdict(float)
        query_tfidf = []

        for term in query:
            term_data = self.binary_search(term, index_data)
            if term_data is None:
                continue

            idf_query[term] = round(math.log10((len(data)/len(term_data)) + 1),4)

            for docId_tfidfin in term_data:
                docId = docId_tfidfin.split(",")[0]
                tf_idf = docId_tfidfin.split(",")[1]
                cos_to_evaluar[docId][term] = tf_idf
                #va guardando en cada doc, el tf idf en orden de los querys keywords

            tf_ = calculate_tf(term, query)
            idf_ = idf_query[term]
            query_tfidf.append(tf_*idf_)

        #Crear vectores caracteristicos
        cosine_docs = defaultdict(list)

        for docId in cos_to_evaluar:
            for term in query:
                if term in cos_to_evaluar[docId]:
                    cosine_docs[docId].append(float(cos_to_evaluar[docId][term]))
                else:
                    cosine_docs[docId].append(0)

        scores = self.cos_Similarity(query_tfidf, cosine_docs)

        # Ordenar los documentos por puntuación de similitud de coseno en orden descendente
        scores = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        scores = scores[:k]

        temp = []
        scores_values = []
        for result in scores:
            temp.append(result[0])
            scores_values.append(result[1])


        # INDICES para hallar en el dataframe
        matching_indices = data.loc[data["id"].isin(temp)].index
        end_time = time.time()

        execution_time = round((end_time - start_time) * 1000, 3) # ms

        return matching_indices, scores_values, execution_time

    #PRUEBAS

    def prueba(self, n):
        #Merge completo
        self.SPIMIConstruction(n)
        merge_final = self.index_blocks()
        self.write_index_tf_idf(merge_final, len(merge_final))

    def prueba2(self):
        k = 5
        results, respuesta, scores = self.retrieve_k_nearest("I need shoes blue for men", k)
        data = self.loadData()
        return data.iloc[results], respuesta, scores


"""
index = InvertIndex(index_file="spimi.txt")
index.prueba()
results,tiempo = index.prueba2()
print(results, tiempo)
"""