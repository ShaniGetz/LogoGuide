from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestNeighbors
import json
import numpy as np
from sklearn.decomposition import PCA
from scipy import spatial


def import_glove_embeddings():
    with open('./local_static/glove_animal_embeddings.json') as f:
        dict_animals_vec = json.load(f)
    animals_names = []
    animals_vecs = []
    for animal, animal_vec in dict_animals_vec.items():
        animals_names.append(animal)
        animals_vecs.append(animal_vec)
    pca = PCA(n_components=3)
    result = pca.fit_transform(np.array(animals_vecs))
    for i in range(len(animals_vecs)):
        key = animals_names[i]
        value = result[i]
        dict_animals_vec[key] = value
    return dict_animals_vec


def import_logos_dict():
    with open('./local_static/logos_dict.json') as f:
        logos_dict = json.load(f)
    return logos_dict


def import_animals_photos():
    with open('./local_static/animals_photos.json') as f:
        dict_animals_photos = json.load(f)
    return dict_animals_photos


def format_logo_lst(nearest_neighbors, data_name_lst, logos_dict):
    formatted_nn_lst = []
    for i in range(len(nearest_neighbors[1][0])):
        index = nearest_neighbors[1][0][i]
        name = data_name_lst[index]
        try:
            name = name.replace(' ', '-')
            distance = nearest_neighbors[0][0][i]
            src = logos_dict[name]
            formatted_nn_lst.append([name, distance, src])
        except:
            print("No logo for: " + name)

    return formatted_nn_lst


def format_animal_lst(input, get_neighbors_model, data_features_full):
    dict_animals_photos = import_animals_photos()
    neighbors_animal_dict = make_neighbors_animal_dict(input,
                                                       get_neighbors_model,
                                                       data_features_full)
    formatted_nn_animal_lst = []
    for index, distance in neighbors_animal_dict.items():
        str_name = switch_num_to_animal(str(index))
        photo_src = dict_animals_photos[str_name]
        formatted_nn_animal_lst.append([str_name, distance, photo_src])
    return formatted_nn_animal_lst


def make_neighbors_animal_dict(input, get_neighbors_model, data_features_full):
    neighbors = get_neighbors_model.kneighbors(input)
    neighbors_animal_dict = {}
    temp = []
    sum_distance = 0
    for i in range(len(neighbors[1][0])):
        index = neighbors[1][0][i]
        vec = data_features_full[index]
        if vec[5] == 0:
            continue
        distance = 1 / neighbors[0][0][i]
        sum_distance += distance
        temp.append([vec, distance])
    for item in temp:
        item[1] = item[1] / sum_distance
    for j in range(len(temp)):
        if temp[j][0][5] != 0:
            if temp[j][0][5] in neighbors_animal_dict.keys():
                neighbors_animal_dict[temp[j][0][5]] += temp[j][1]
            else:
                neighbors_animal_dict[temp[j][0][5]] = temp[j][1]

    return neighbors_animal_dict


def switch_num_to_animal(num):
    if num == '1':
        return 'bird'
    elif num == '2':
        return 'eagle'
    elif num == '3':
        return 'lion'
    elif num == '4':
        return 'horse'
    elif num == '5':
        return 'fox'
    elif num == '6':
        return 'human'
    elif num == '7':
        return 'bull'
    elif num == '8':
        return 'duck'
    elif num == '9':
        return 'deer'
    elif num == '10':
        return 'butterfly'
    elif num == '11':
        return 'bear'
    elif num == '12':
        return 'bat'
    elif num == '13':
        return 'camel'
    elif num == '14':
        return 'tiger'


def make_neighbors_animal_vec(neighbors_animal_dict, dict_animals_vec):
    temp = []
    neighbors_animal_vec_lst = []
    average_vec = []
    for animal in neighbors_animal_dict:
        animal_str = switch_num_to_animal(str(animal))
        temp.append([animal_str, neighbors_animal_dict[animal]])
    # model = Word2Vec([animals], size=100, window=5, min_count=1, workers=4)
    for lst in temp:
        animal_vec = np.array(dict_animals_vec[lst[0]])
        neighbors_animal_vec_lst.append([animal_vec, lst[1]])
    for lst in neighbors_animal_vec_lst:
        average_vec.append(lst[0] * lst[1])
    vec = 0
    for i in range(len(average_vec)):
        vec += average_vec[i]

    return vec


def closest_animal(dict_animals_vec, vec):
    animals_vec_lst = []
    for animal in dict_animals_vec:
        animals_vec_lst.append(dict_animals_vec[animal])
    A = animals_vec_lst
    tree = spatial.KDTree(A)
    res = tree.query(vec)
    index = res[1]
    res = animals_vec_lst[index]
    for animal, v in dict_animals_vec.items():
        if np.array_equal(v, res):
            return animal


def find_animal(input, get_neighbors_model, full_features):
    neighbors_animal_dict = make_neighbors_animal_dict(
        input, get_neighbors_model, full_features)
    dict_animals_vec = import_glove_embeddings()
    vec = make_neighbors_animal_vec(neighbors_animal_dict,
                                    dict_animals_vec)
    animal = closest_animal(dict_animals_vec, vec)

    return animal
