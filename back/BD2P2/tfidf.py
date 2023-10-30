import nltk
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
import os

stemmer = SnowballStemmer('english')
nltk.download('punkt')

def tokenizar(texto):
    texto = texto
    tokens = nltk.word_tokenize(texto)
    tokenText = nltk.Text(tokens).tokens
    return tokenText

def eliminarStopWords(tokenText): #elegir stopwords
    print(os.getcwd())
    customSW = open('stop_words_spanish.txt','r')
    palabras_stoplist = customSW.read() #.splitlines()
    customSW.close()
    palabras_stoplist = nltk.word_tokenize(palabras_stoplist.lower())
    stoplist = ["0","1","2","3","4","5","6","7","8","9","_","--", "\\",
                "^",">",'.',"@","=","$" , '?', '[', ']', '¿',"(",")",
                '-', '!',"<", '\'',',', ":","``","''", ";", "»", '(-)',
                "+","0","/", "«", "{", "}", "--", "|","`","~","#","&"]
    palabras_stoplist += stoplist
    #Reducir palabras

    #Sacamos lexema si no esta en stoplist
    resultado = [stemmer.stem(token) for token in tokenText if (token not in palabras_stoplist)]

    #La idea es eliminar todas esas palabras que son de Latex
    lstTokens = []
    for token in resultado:
        bandera = False
        for word in stoplist:
            if word in token:
                bandera = True
                break
        if bandera == False:
            lstTokens.append(token)

    return lstTokens

def preprocesar_textos(texto):
    tokenText = tokenizar(texto)
    tokensLst = eliminarStopWords(tokenText)

    return tokensLst