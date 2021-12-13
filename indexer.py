import json
import math
from lxml import etree
import os
import time

# define tokenizer
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
import nltk

nltk.download('punkt')
tokenizer = RegexpTokenizer(r'\w+')
# define lemmatizer

lemmatizer = WordNetLemmatizer()
DOCUMENTS = "./Documents/"
TAG_DOCNO = "DOCNO"


class Indexer(object):
    BASE = 100

    def __init__(self, path_index, lemmatizer=True, stop_list_frequency=0.75):
        self.index = False
        self.path_index = path_index
        self.posting_list = {}
        self.stop_list = []
        self.documents = []
        self.documents_normalisation = None
        self.max_length_doc = 0
        self.lemmatizer = lemmatizer
        self.stop_list_frequency = 0.98
        if os.path.isfile(path_index):
            with open(path_index) as file:
                self.__dict__ = json.loads(file.read())
                self.index = True

    def index_word_of_doc(self, word, docid, position):
        if lemmatizer:
            word = lemmatizer.lemmatize(word)
        word = word.lower()

        # create posting list by step
        if word not in self.posting_list:
            self.posting_list[word] = {}
        if docid not in self.posting_list[word]:
            self.posting_list[word][docid] = []
        self.posting_list[word][docid].append(position)

        #  create set of documents by step
        self.documents.append(docid)

    def index_end(self):
        self.index = True

        self.documents_normalisation = {}
        nb_word_by_docs = {}

        self.documents = list(set(self.documents))

        # create documents_normalisation
        for doc in self.documents:
            self.documents_normalisation[doc] = 0
            for word in self.posting_list:
                if doc in self.posting_list[word]:
                    self.documents_normalisation[doc] += (self.tf_idf(word, doc) ** 2)
                    nb_word_by_docs.setdefault(doc, 0)
                    nb_word_by_docs[doc] += len(self.posting_list[word][doc])

        # define the documents with the maximal length of words
        self.max_length_doc = max(nb_word_by_docs.values())

        # create a stop list
        self.create_stop_list()

        # save the index to json format
        with open(self.path_index, "w+") as file:
            file.write(self.toJson())

    def create_stop_list(self):
        temp = self.posting_list.copy()
        for word in self.posting_list:
            if len(self.posting_list[word]) / len(self.documents) >= self.stop_list_frequency:
                self.stop_list.append(word)
                del temp[word]
        del self.posting_list
        self.posting_list = temp
        print(self.stop_list)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def tf(self, word, document):
        tf = 0
        if word in self.posting_list and document in self.posting_list[word]:
            tf = len(self.posting_list[word][document])
        return math.log10(1 + tf)

    def idf(self, word):
        N = len(self.documents)
        df = 0
        if word in self.posting_list:
            df = len(self.posting_list[word])
        return math.log10(N / df) if df != 0 else 0

    def tf_idf(self, word, document):
        return self.tf(word, document) * self.idf(word)

    def tf_normalisation(self, word, document):
        if document not in self.documents_normalisation:
            return 0
        return self.tf(word, document) / (math.sqrt(self.documents_normalisation[document]))

    def proximity(self, query):
        query = query.lower()
        query = tokenizer.tokenize(query)
        # -------
        query = query.lower()
        query = tokenizer.tokenize(query)
        score = {}
        old_word = None
        for word in query:
            if old_word is None:
                old_word = word
                continue
            for doc in self.documents:
                score.setdefault(doc, 0)
                try:
                    list1 = self.posting_list[word][doc]
                    list2 = self.posting_list[old_word][doc]
                    min = math.inf
                    for e1 in list1:
                        for e2 in list2:
                            diff = abs(e1 - e2)
                            if diff < min:
                                min = diff
                    score[doc] += min
                except Exception as e:
                    if not (word in self.stop_list or old_word in self.stop_list):
                        score[doc] += self.max_length_doc
            old_word = word

        for doc in score:
            score[doc] = ((self.max_length_doc - (score[doc] / len(query))) / self.max_length_doc)

        score = {key: value for key, value in score.items() if value != 0}
        return dict(sorted(score.items(), key=lambda item: -item[1]))

    def cosine(self, query):
        query = query.lower()
        query = tokenizer.tokenize(query)
        # -------
        query_normalisation = self.query_weights(query)
        score = {}
        for word in query:
            for doc in self.documents:
                score.setdefault(doc, 0)
                score[doc] += (query_normalisation[word] * self.tf_normalisation(word, doc))
        score = {key: value for key, value in score.items() if value != 0}
        return dict(sorted(score.items(), key=lambda item: -item[1]))

    def fuzzy(self, query):
        cos = self.cosine(query)
        prox = self.proximity(query)

        for doc in prox:
            try:
                cos[doc] += prox[doc]
            except:
                pass

        cos = {key: value for key, value in cos.items() if value != 0}
        return dict(sorted(cos.items(), key=lambda item: -item[1]))

    def correction_query(self, query: str):
        seuil = 0.5
        query = query.lower()
        query = tokenizer.tokenize(query)
        # -------
        words = {}
        min_distance = {}
        length = 0

        for word in query:
            min_distance[word] = math.inf
            for word_index in self.posting_list:
                distance = nltk.edit_distance(word, word_index)
                if distance < min_distance[word]:
                    distance[word] = distance
                    words[word] = word_index
            length += min_distance[word]

        if len(query.replace(" ", "")) * seuil >= length:
            return "".join(words.values())
        else:
            return ""

    def query(self, query):
        resp = self.fuzzy(query)
        if resp == {}:
            new_query = self.correction_query(query)
            return self.fuzzy(new_query), new_query
        return resp, None

    def query_weights(self, query):
        count_words_query = {}
        for word in query:
            count_words_query.setdefault(word, 0)
            count_words_query[word] += 1

        for word in count_words_query:
            count_words_query[word] = math.log10(1 + count_words_query[word])

        norms = 0
        for word in count_words_query:
            norms += count_words_query[word]

        for word in count_words_query:
            count_words_query[word] /= math.sqrt(norms)

        return count_words_query


def indexer_xml(indexer, location_doc):
    files = [f for f in os.listdir(location_doc) if os.path.join(location_doc, f)]
    nb_doc = 0
    for filename in files:
        tree = etree.parse(location_doc + filename)
        documents = tree.getroot()
        for doc in documents:
            nb_doc += 1
            position = 0
            docno = None
            text = []
            for section in doc:
                if section.tag == TAG_DOCNO:
                    docno = section.text.strip()
                else:
                    text += tokenizer.tokenize(section.text)
            for word in text:
                indexer.index_word_of_doc(word, docno, position)
                position += 1
    indexer.index_end()

    return indexer
