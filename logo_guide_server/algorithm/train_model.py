import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestNeighbors
from nltk.corpus import stopwords


animals = ["human", "fox", "dog", "cat", "chicken", "penguin", "bunny",
           "horse", "tiger", "goat", "bear", "giraffe", "lion", "turtle", "cow",
           "pig", "wolf", "shark", "armadillo", "bird", "frog", "panda",
           "dragonfly", "toucan", "starfish", "salamander", "crab", "gecko", "meerkat",
           "bee", "cheetah", "chihuahua", "zebra", "mouse", "donkey", "duck",
           "squirrel", "lizard", "rabbit", "reindeer", "coyote", "shrimp",
           "turtle", "gorilla", "sheep", "deer", "moose", "leopard", "rat",
           "bat", "pony", "bull", "hippopotamus", "geese", "parrot", "spider", "crocodile",
           "butterfly", "pig", "raccoon", "whale", "seahorse", "chameleon",
           "jellyfish", "salmon", "raven", "albatross", "ox", "elephant",
           "alpaca", "octopus", "orca", "anchovy", "eagle", "ant", "owl",
           "impala", "otter", "orangutan", "ostrich", "alligator", "ibex", "hedgehog",
           "antelope", "ungulate", "ape", "opossum", "oyster", "anaconda",
           "iguana", "eel", "ibis", "oxen", "anteater", "camel"]


def import_data():
    data_name_lst = []
    data_summary_lst = []
    data_features_full = []
    data_features_lst = []
    with open('./local_static/company_descriptions.json') as f:
        dict = json.load(f)
        for logo in dict["logos"]:
            data_name_lst.append(logo["name"])
            data_summary_lst.append(logo["summary"])
            data_features_full.append((logo["features"]))
        for feature in data_features_full:
            data_features_lst.append(feature[:5])
    return data_name_lst, data_summary_lst, data_features_full, data_features_lst


def Tfidf(data_lst):
    # Bag of Words
    stop_word = set(stopwords.words('english'))
    vectorizer = CountVectorizer(max_features=1500, stop_words=stop_word,
                                 ngram_range=(1, 3))
    X = vectorizer.fit_transform(data_lst)

    # Finding TFIDF
    tfidf_converter = TfidfTransformer()
    X = tfidf_converter.fit_transform(X)

    return X, vectorizer, tfidf_converter


def learn(data_summary_lst, data_features_lst, n):
    X, vectorizer, tfidf_transformer = Tfidf(data_summary_lst)
    y = data_features_lst
    neigh = KNeighborsClassifier(n_neighbors=n, weights='distance')
    neigh.fit(X, y)
    return neigh


def get_neighbors(data_lst, n):
    X, vectorizer, tfidf_converter = Tfidf(data_lst)
    samples = X
    neigh = NearestNeighbors(n_neighbors=n)
    neigh.fit(samples)
    # input_vec = input_Tfidf(input, vectorizer, tfidf_converter)
    # res = neigh.kneighbors(input_vec)

    return neigh


def format_result_animal(vec):
    # if vec [0][1] == 1:
    if vec[0][4] == 0:
        return 'the image does not contain an animal'

    if vec[0][4] == 1:
        return 'the image contains an animal'


def input_Tfidf(input_str, vectorizer, tfidf_converter):
    # Bag of Words
    X = vectorizer.transform([input_str])

    # Finding TFIDF
    X = tfidf_converter.transform(X)

    return X


def train_nearest_neighbors():
    data_name_lst, data_summary_lst, data_features_full, data_features_lst = import_data()
    X, vectorizer, tfidf_converter = Tfidf(data_summary_lst)
    knn_model_description = learn(data_summary_lst, data_features_lst, 15)
    knn_model_animals = learn(data_summary_lst, data_features_lst, 3)
    get_neighbors_model_animals = get_neighbors(data_summary_lst, 35)
    get_neighbors_model_logos = get_neighbors(data_summary_lst, 15)

    return data_name_lst, knn_model_description, knn_model_animals, get_neighbors_model_animals, get_neighbors_model_logos, vectorizer, tfidf_converter, data_features_full