from django.shortcuts import render
from .train_model import *
from .helper_functions import find_animal, import_glove_embeddings, format_logo_lst, import_logos_dict, format_animal_lst
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


data_name_lst, knn_model_description, knn_model_animals, get_neighbors_model_animals, get_neighbors_model_logos, vectorizer, tfidf_converter, full_features = train_nearest_neighbors()
glove_animal_embeddings = import_glove_embeddings()
logos_dict = import_logos_dict()

class LogoGuide(APIView):
    """
    The api endpoint of the logo guidelines.
    """

    def get(self, request):

        # Prepare the graph
        params = request.query_params
        if len(params) != 1:
            return Response("Please specify a source and a target.", status=status.HTTP_204_NO_CONTENT)
        else:
            input_description = params['description']
            input_vec = input_Tfidf(input_description, vectorizer, tfidf_converter)
            guidelines = knn_model_description.predict(input_vec)
            nearest_neighbors = get_neighbors_model_logos.kneighbors(input_vec)
            formatted_nn_lst = format_logo_lst(nearest_neighbors, data_name_lst,logos_dict)
            guidelines_animals = knn_model_animals.predict(input_vec)
            if (guidelines_animals[0][1] == 1):
                is_animal = guidelines_animals[0][4]
                animal = find_animal(input_vec, get_neighbors_model_animals, full_features)
                formatted_nn_animal_lst = format_animal_lst(input_vec, get_neighbors_model_animals, full_features)
            else:
                is_animal = None
                animal = None
                formatted_nn_animal_lst = None
            response = {
                'guidelines': guidelines,
                'is_animal': is_animal,
                'animal': animal,
                'nearest_neighbors': formatted_nn_lst,
                'nearest_animals': formatted_nn_animal_lst
            }

            return Response(response)