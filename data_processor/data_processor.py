#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Creates a graph from the datasets.
"""

import sys
from os import path
from time import time
import collections


nId = -1
def getNextnId():
    global nId
    nId = nId + 1
    return nId 

class Node(object):
    """

    """
    def __init__(self, id, name, type="user"):
        self.id = str(id)
        self.neighbors = []
        self.name = name
        self.type = type
        self.rating = {}

class Movie(object):
    """
    
    """
    def __init__(self, name):
        self.name = name
        self.director = None
        self.actors = []
        self.genres = []

def load_movie_data():
    """
    Load the data about the movies into a dictionary The dictionary maps a movie ID 
    to a movie object, Also store the unique directors, actors, and genres
    """

    movies_directors_filedir = "./data/movie_directors.dat"
    movies_actors_filedir = "./data/movie_actors.dat"
    movies_genres_filedir = "./data/movie_genres.dat"
    movies_filedir = "./data/movies.dat"

    i= 0
    movies = {} # 10197
    with open(movies_filedir, "r", encoding="GB18030", errors="ignore") as fin:
        fin.readline()
        for line in fin: 
            m_id, name = line.strip().split("\t")[:2]
            movies['m'+m_id] = Movie(name)

    directors = set([]) # 10155
    with open(movies_directors_filedir, 'r', encoding='GB18030', errors="ignore") as fin:
        fin.readline()
        for line in fin:  
            m_id, director = line.strip().split()[:2]
            if "m"+m_id in movies:
                movies["m"+m_id].director = director
            directors.add(director)

    actors = set([]) 
    with open(movies_actors_filedir, 'r', encoding='GB18030', errors="ignore") as fin:
        fin.readline()
        for line in fin:
            m_id, actor = line.strip().split()[:2]
            if "m"+m_id in movies:
                movies["m"+m_id].actors.append(actor)
            actors.add(actor)

    genres = set([])
    with open(movies_genres_filedir, "r", encoding='GB18030', errors='ignore') as fin:
        fin.readline()  # burn metadata line
        for line in fin:
            i = i+1
            m_id, genre = line.strip().split()
            if "m"+m_id in movies:
                movies["m"+m_id].genres.append(genre)
            genres.add(genre)

    return movies, directors, actors, genres        
            
def records_to_graph():
    """
    
    """
    # Output files for the graph
    adjlist_file = open("./out.adj", 'w')
    node_list_file = open("./nodelist.txt", 'w')

    num_ratings = 0
    ratings = collections.defaultdict(dict)
    with open("./data/train_user_ratings.dat", "r", encoding='GB18030', errors='ignore') as fin:
        fin.readline()  # burn metadata line
        for line in fin:
            ls = line.strip().split("\t")
            user, movie, rating = ls[:3]
            rating = str(int(round(float(rating))))   
            # 二重字典嵌套 'u170': {'m1': '3', 'm2': '2', ......}
            ratings["u"+user]["m"+movie] = rating  
            num_ratings += 1
    
    movies, directors, actors, genres = load_movie_data()

    nodelist = []
    nodedict = {}

    for key, value in movies.items():
        newNode = Node(getNextnId(), value.name,'movie')
        nodedict[key] = newNode
        nodelist.append(newNode)
        for r in range(0,6):
            ratingNode = Node(getNextnId(), key+'_'+str(r),'rating')
            nodedict[key+'_'+str(r)] = ratingNode
            nodelist.append(ratingNode)
    
    # adding users in the nodedict
    for user in ratings:
        newUser = Node(getNextnId(), user,'user')
        nodedict[user] = newUser
        nodelist.append(newUser)

    # adding actor objects in the nodedict and nodelist
    for a in list(actors):
        newNode = Node(getNextnId(), a,'actor')
        nodedict[a] = newNode
        nodelist.append(newNode)

    # adding director in the nodedict and nodelist
    for d in list(directors):
        newNode = Node(getNextnId(), d,'director')
        nodedict[d] = newNode
        nodelist.append(newNode)

    # adding genre in the nodedict and nodelist
    for g in list(genres):
        newNode = Node(getNextnId(), g,'genre')
        nodedict[g] = newNode
        nodelist.append(newNode)  

    # user-rating/movie - movie rating
    for user, rating in ratings.items():
        for m, r in rating.items():
            userNode = nodedict[user]
            ratingNode = nodedict[m+'_'+r]
            movieNode = nodedict[m]
            userNode.neighbors.append(ratingNode)
            ratingNode.neighbors.append(userNode)
            movieNode.neighbors.append(ratingNode)
            ratingNode.neighbors.append(movieNode)
    
    # movie - director/actor/genre
    for k,v in movies.items():
        movieNode = nodedict[k]
        if movies[k].director != None:
            dirNode = nodedict[v.director]
            movieNode.neighbors.append(dirNode)
            dirNode.neighbors.append(movieNode)
        actor_list = v.actors
        for a in actor_list:
            actorNode = nodedict[a]
            actorNode.neighbors.append(movieNode)
            movieNode.neighbors.append(actorNode)
        for g in v.genres:
            genreNode = nodedict[g]
            genreNode.neighbors.append(movieNode)
            movieNode.neighbors.append(genreNode)  
   
        # Write out the graph
    for node in nodelist:
        node_list_file.write("%s\t%s\t%s\n" % (node.id, node.name, node.type))
        adjlist_file.write("%s " % node.id)
        for n in node.neighbors:
            adjlist_file.write("%s " % n.id)
        adjlist_file.write("\n")
    adjlist_file.close()
    node_list_file.close()
    
    return nodedict


records_to_graph()
    
