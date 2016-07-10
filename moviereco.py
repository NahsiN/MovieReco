# -*- coding: utf-8 -*-

import sqlite3
import ipdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------- #
# STEP 1: Parse sql data into Python
# Read contents from database file
db_path = 'MyVideos99.db'
# open a connection to database
conn = sqlite3.connect(db_path)
# open a cursor object
cur = conn.cursor()

# Read relevant info from database
cur.execute("""SELECT c00 as 'MovieName', c05 as 'Rating', c07 as 'Year',
            c14 as 'Genres' FROM movie WHERE Genres != '' LIMIT 10""")
col_names = cur.description
data = cur.fetchall()
cur.execute("SELECT name AS 'Genres' FROM genre")
genres = cur.fetchall()

# close database
# conn.commit()  # commit your changes
conn.close()

# Parse the SQL data into a dataframe
# strip the tuples in genres list
genres = set([genre[0] for genre in genres])
# Parse this data into a nicer pandas format
# remove the 6 None entries in col_names due to adhering with Python's DB-API
# standard
col_names = [cols[0] for cols in col_names]
# create a dict for a pandas dataframe
table_dict = {}
for key in col_names:
    table_dict[key] = [entry[col_names.index(key)] for entry in data]
df = pd.DataFrame(table_dict)

# convert every entry in Genres column to a set. E.g.,
# 'Animation / Comedy' --> {'Animation', 'Comedy'}
# for each_movie_genres in df.loc[:, 'Genres']:
# genres_list = each_movie_genres.split('/')
ipdb.set_trace()
for i in range(0, df.Genres.size):
    # split string using '/' and then strip whitespaces from each element in
    # list
    genres_list = df.Genres[i].split('/')
    df.Genres[i] = set([genre.strip() for genre in genres_list])

# ----------------------------------------------------------------------- #
