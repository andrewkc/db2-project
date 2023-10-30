import numpy as np
import math

def compute_tf(collection):
    doc_tf = {}
    total_tf = {}
    for doc_id, doc in enumerate(collection):
        doc_term_freq = {} #cuantas veces aparece cada term en cada doc
        for term in doc:
            if term in doc_term_freq:
                doc_term_freq[term] += 1
                total_tf[term] += 1
            else:
                if term not in total_tf:
                    total_tf[term] = 1
                doc_term_freq[term] = 1

        doc_tf[doc_id] = doc_term_freq

    total_tf = sorted(total_tf.items(), key= lambda tup: tup[1], reverse=True)
    return doc_tf, total_tf

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

    term_freq, orden_keywords = compute_tf(collection) # Contar la frecuencia de cada término en cada documento

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