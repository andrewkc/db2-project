from BD2P2.preprocesamiento import *
from BD2P2.tfidf import *
import pandas as pd

import sys
import ast
import re
import json

import os
from operator import itemgetter
from collections import OrderedDict, defaultdict
import math
import numpy as np


class InvertIndex:
    def __init__(self, index_file, abstracts_por_bloque=10000, dataFile=""):
        self.index_file = index_file
        self.index = {}
        self.idf = {}
        self.length = {}
        self.BLOCK_LIMIT = abstracts_por_bloque
        self.lista_de_bloques = []
        self.data_path = "definitivo.csv" #data.csv
        self.path_index = "spimi.txt"


    def loadData(self):
        data = pd.read_csv(self.data_path)
        data["id"] = data["id"].astype(str)
        return data

    def SPIMIConstruction(self):
        data = self.loadData()

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
                    with open("C:/Users/diego/DataspellProjects/BD2P2/bloques/" + block_name, "w") as file_part:
                        json.dump(sorted_block, file_part, indent=2)
                    sorted_block = {} #clear
                    block_n += 1
                    dictTerms = defaultdict(list) #clear
                dictTerms[term].append((docID, freq))

        if dictTerms:
            sorted_block = sorted(dictTerms.items(), key=itemgetter(0))
            block_name = "bloque-"+str(block_n)+".txt"
            with open("C:/Users/diego/DataspellProjects/BD2P2/bloques/" + block_name, "w") as file_part:
                json.dump(sorted_block, file_part, indent=2)
            dictTerms = defaultdict(list)

    def listFiles(self):
        filepaths = "C:/Users/diego/DataspellProjects/BD2P2/bloques/"
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
        data = self.loadData()

        query = preprocesar_textos(query)

        index_data = self.load_Index()

        #print("query keywords ", query)

        cos_to_evaluar = defaultdict(dict)
        idf_query=defaultdict(float)
        query_tfidf = []

        for term in query:
            term_data = self.binary_search(term, index_data)
            #term_data = self.loop(term, index_data) #posting list
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
        for result in scores:
            temp.append(result[0])


        # INDICES para hallar en el dataframe
        matching_indices = data.loc[data["id"].isin(temp)].index

        return matching_indices

    #PRUEBAS

    def prueba(self):
        #Merge completo
        self.SPIMIConstruction()
        merge_final = self.index_blocks()
        self.write_index_tf_idf(merge_final, len(merge_final))

    def prueba2(self):
        k = 3
        results = self.retrieve_k_nearest("Quantum Theory of Integrals by Reimann", k)
        data = self.loadData()
        return data.iloc[results] #rows con los resultados para la data


# Crear una instancia de la clase InvertIndex
inverted_index = InvertIndex(index_file="your_index_file.txt", abstracts_por_bloque=10000, dataFile="definitivo.csv")

# Prueba la construcción del índice
inverted_index.SPIMIConstruction()

# Prueba la fusión de bloques e indexación
index = inverted_index.index_blocks()

# Escribe el índice en un archivo con TF-IDF
inverted_index.write_index_tf_idf(index, len(index))

# Opcional: Prueba la recuperación de los documentos más similares
k = 3
results = inverted_index.retrieve_k_nearest("Women", k)

# Opcional: Muestra los resultados
print(results)