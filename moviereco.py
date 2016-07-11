# -*- coding: utf-8 -*-

import sqlite3
import ipdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------- #
# STEP 1: Parse sql data into Python
# Read contents from database file
db_path = 'MyVideos99_Anime.db'
# open a connection to database
conn = sqlite3.connect(db_path)
# open a cursor object
cur = conn.cursor()

# Read relevant info from database
cur.execute("""SELECT c00 as 'MovieName', c05 as 'Rating', c07 as 'Year',
            c14 as 'Genres' FROM movie WHERE Genres != '' LIMIT 1000""")
col_names = cur.description
data = cur.fetchall()
cur.execute("SELECT name AS 'Genres' FROM genre")
genres = cur.fetchall()

# close database
# conn.commit()  # commit your changes
conn.close()
print('Data from SQL file loaded.')

# Parse the SQL data into a dataframe
# strip the tuples in genres list
genres = [genre[0] for genre in genres]
genres.sort()  # sort genres alphabetically IN-place
# Parse this data into a nicer pandas format
# remove the 6 None entries in col_names due to adhering with Python's DB-API
# standard
col_names = [cols[0] for cols in col_names]
# create a dict for a pandas dataframe
table_dict = {}
for key in col_names:
    table_dict[key] = [entry[col_names.index(key)] for entry in data]
df_kodi = pd.DataFrame(table_dict)

# convert every entry in Genres column to a set. E.g.,
# 'Animation / Comedy' --> {'Animation', 'Comedy'}
# for each_movie_genres in df_kodi.loc[:, 'Genres']:
# genres_list = each_movie_genres.split('/')
for i in range(0, df_kodi.Genres.size):
    # split string using '/' and then strip whitespaces from each element in
    # list
    genres_list = df_kodi.Genres[i].split('/')
    df_kodi.Genres[i] = set([genre.strip() for genre in genres_list])

print('Data parsed into a pandas table.')
# ----------------------------------------------------------------------- #

# ----------------------------------------------------------------------- #
# STEP 2, Compute genre correlations
# create genre correlations dataframe
df_genre_corrs = pd.DataFrame(index=genres, columns=genres)
df_genre_corrs.iloc[:, :] = 0

# MAIN ALGO constructs genre correlation matrix
# loop over genres (i)
for gi in genres:
    # select all movies having genre gi
    movie_ids = []
    for k in range(0, df_kodi.index.size):
        if gi in df_kodi.loc[k, 'Genres']:
            movie_ids.append(k)
    if len(movie_ids) == 0:
        print('No movies with genre={0} found'.format(gi))

    # loop over the other genres (j)
    for gj in genres:
        # create genre set G_ij
        g_ij = {gi, gj}
        # consider only those movies that have gi as a genre
        if len(movie_ids) == 0:
            pass
        else:
            # loop only over the movies that have genre gi to determine
            # correaltions
            for k in movie_ids:
                # computes intersection of G_ij with movie genre set
                common_genres = g_ij & df_kodi.loc[k, 'Genres']
                if len(common_genres) == 2 and gi != gj:
                    df_genre_corrs.loc[gi, gj] += 1
                elif len(common_genres) == 1 and gi == gj:
                    df_genre_corrs.loc[gi, gj] += 1

# Normalize the total movie count for genre gi to unity
for gi in genres:
    if df_genre_corrs.loc[gi, gi] != 0:
        df_genre_corrs.loc[gi, :] = df_genre_corrs.loc[gi, :]/df_genre_corrs.loc[gi, gi]

# Visualize genre correlations
plt.figure()
plt.spy(df_genre_corrs, markersize=3)
plt.figure()
plt.imshow(np.array(df_genre_corrs, dtype=float))
plt.colorbar()
plt.show()

# ----------------------------------------------------------------------- #

# ----------------------------------------------------------------------- #
# STEPS 3 and 4. Specify user preferred genres and compute recommendation
# points for each movie
preferred_genres_set = {'Action', 'Comedy'}

# loop over movies
for k in range(0, df_kodi.index.size):
    # see if there is overlap between the preferred genres and movie's
    # genres
    avg_movie_rating = float(df_kodi.loc[k, 'Rating'])
    prefactor = avg_movie_rating/len(preferred_genres_set)
    recomm_pts = 0
    if len(preferred_genres_set & df_kodi.loc[k, 'Genres']) != 0:
        # loop over preferred genres
        for gi in preferred_genres_set:
            # loop over the movie genre set
            for gj in df_kodi.loc[k, 'Genres']:
                if gi == gj:
                    recomm_pts += prefactor*df_genre_corrs.loc[gi, gj]
                else:
                    recomm_pts += prefactor*df_genre_corrs.loc[gi, gj]/(len(df_kodi.loc[k, 'Genres']) - 1)

    elif len(preferred_genres_set & df_kodi.loc[k, 'Genres']) == 0:
        for gi in preferred_genres_set:
            for gj in preferred_genres_set:
                recomm_pts += prefactor/len(df_kodi.loc[k, 'Genres'])*df_genre_corrs.loc[gi, gj]
    else:
        print('How did I fall here. Investigate')
    # print('Movie Name = {0}, Recommendation Points = {1}'.format(df_kodi.loc[k, 'MovieName'], recomm_pts))
    df_kodi.loc[k, 'Recommendation Points'] = recomm_pts

# Normalize recommendation points column
df_kodi.loc[:, 'Recommendation Points'] = df_kodi.loc[:, 'Recommendation Points']/df_kodi.loc[:, 'Recommendation Points'].max()
print('Preferred genres = {0}'.format(preferred_genres_set))
print(df_kodi.sort_values(by=['Recommendation Points'], ascending=False).head(10))
