# -*- coding: utf-8 -*-

import sqlite3
import ipdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from time import time
from datetime import timedelta

# ----------------------------------------------------------------------- #
# STEP 1: Parse sql data into Python
# Read contents from database file
db_path = 'MyVideos99_All.db'
start = time()
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
end = time()
elapsed_time = timedelta(seconds=end - start)
print('Data of {0} movies from SQL file loaded. {1}'.format(len(data), elapsed_time))

# Parse the SQL data into a dataframe
# strip the tuples in genres list
start = time()
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
end = time()
elapsed_time = timedelta(seconds=end-start)
print('Data parsed into a pandas table. {0}'.format(elapsed_time))
# ----------------------------------------------------------------------- #

# ----------------------------------------------------------------------- #
# STEP 2, Compute genre correlations
# create genre correlations dataframe

def gen_corr_matrix(df_kodi):
    """
    Creates the genre correlation matrix.

    Parameters
    ----------
    df_kodi: Pandas dataframe with all the relevant info

    Returns
    -------
    df_genre_corrs: Genre correlation matrix
    """

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

    return df_genre_corrs


start = time()
df_genre_corrs = gen_corr_matrix(df_kodi)
end = time()
elapsed_time = timedelta(seconds=end-start)
print('Genre correlations matrix created. {0}'.format(elapsed_time))


# Visualize genre correlations
# plt.figure()
# plt.spy(df_genre_corrs, markersize=3)
plt.figure()
plt.pcolormesh(np.array(df_genre_corrs, dtype=float), cmap='gnuplot', edgecolor=None)
plt.colorbar()
# create labels
x_points = []
x_labels = []
for i in range(0, df_genre_corrs.index.size):
    x_points.append(i + 0.5)
    x_labels.append('{0:.3}'.format(df_genre_corrs.index[i]))
plt.xticks(x_points, x_labels)
plt.yticks(x_points, x_labels)
plt.xlim(0, df_genre_corrs.index.size)
plt.ylim(0, df_genre_corrs.index.size)
plt.show()

# ----------------------------------------------------------------------- #

# ----------------------------------------------------------------------- #
# STEPS 3 and 4. Specify user preferred genres and compute recommendation
# points for each movie
preferred_genres_set = {'Drama', 'Comedy'}

def gen_recomm_pts(df_genre_corrs, preferred_genres_set, movie_genres_set, avg_movie_rating):
    """
    Given user preferred genres, a movie's genre set and it's rating, generate
    recommendation points for the movie based on genre correaltions

    Parameters
    ----------
    df_genre_corrs: genre correlations matrix
    preffered_genre_set : a set of preferred genres
    movie_genres_set: set of genres of a movie
    avg_movie_rating: average movie rating

    Returns
    -------
    recomm_pts: Recommendation points for the movie.
    """

    if type(avg_movie_rating) is not float:
        raise AssertionError('Average movie rating should be float')
    # see if there is overlap between the preferred genres and movie's
    # genres
    prefactor = avg_movie_rating/len(preferred_genres_set)
    recomm_pts = 0
    # common genres between user preffered genres and movie genre set
    gi_common = preferred_genres_set & movie_genres_set
    # if len(gi_common) != 0:
    # loop over comon genres
    for gi in gi_common:
        # loop over the movie genre set
        for gj in movie_genres_set:
            if gi == gj:
                recomm_pts += prefactor*df_genre_corrs.loc[gi, gj]
            else:
                if len(movie_genres_set) == 1:
                    raise AssertionError('Division by 0 imminent. Please investigate.')
                recomm_pts += prefactor*df_genre_corrs.loc[gi, gj]/(len(movie_genres_set) - 1)

    # loop over user preffered genres NOT common to both user preffered
    # set and movie genre set
    for gi in preferred_genres_set - gi_common:
        for gj in movie_genres_set:
            recomm_pts += prefactor/len(movie_genres_set)*df_genre_corrs.loc[gi, gj]

    return recomm_pts

start = time()
# loop over movies
for k in range(0, df_kodi.index.size):
    df_kodi.loc[k, 'Recommendation Points'] = gen_recomm_pts(df_genre_corrs, preferred_genres_set, df_kodi.loc[k, 'Genres'], float(df_kodi.loc[k, 'Rating']))

# Normalize recommendation points column
df_kodi.loc[:, 'Recommendation Points'] = df_kodi.loc[:, 'Recommendation Points']/df_kodi.loc[:, 'Recommendation Points'].max()
end = time()
elapsed_time = timedelta(seconds=end-start)
print('Finished generating recommendation points. {0}'.format(elapsed_time))
print('Preferred genres = {0}'.format(preferred_genres_set))
print(df_kodi.sort_values(by=['Recommendation Points'], ascending=False).head(10))
