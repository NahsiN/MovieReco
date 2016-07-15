# -*- coding: utf-8 -*-
"""
Author: Nishan Singh Mann (nishan.singh.mann@gmail.com)

Main setup file that reads in from the SQlite database and runs the algorithm.
"""

import sqlite3
#import ipdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from time import time
from datetime import timedelta
import sys
from algos import gen_corr_matrix, gen_recomm_pts

# ----------------------------------------------------------------------- #
# STEP 1: Parse sql data into Python
# Read contents from database file
#db_path = 'MyVideos99_NoBollywood.db'
try:
    db_path = sys.argv[1]
except:
    print('Please specify database. Exiting.')
    sys.exit()

start = time()
# open a connection to database
conn = sqlite3.connect(db_path)
# open a cursor object
cur = conn.cursor()

# Read relevant info from database
try:
    cur.execute("""SELECT idMovie, c00 as 'MovieName', c05 as 'Rating', c07 as 'Year',
            c14 as 'Genres' FROM movie WHERE Genres != '' LIMIT 1000""")
except:
    print('{0} Either this database does not exist or something else went wrong. Exiting.'.format(db_path))
    sys.exit()
# since the first column name will be idMovie which we want to use as an
# index instead, we filter it out
col_names = cur.description[1:]
data = cur.fetchall()

cur.execute("SELECT genre_id, name AS 'Genres' FROM genre")
genres = cur.fetchall()

cur.execute("""SELECT genre_id,  media_id as "idMovie" FROM genre_link
                WHERE media_type = 'movie' """)
genres_link = cur.fetchall()

# close database
# conn.commit()  # commit your changes
conn.close()
end = time()
elapsed_time = timedelta(seconds=end - start)
print('Data of {0} movies from SQL file loaded. {1}'.format(len(data), elapsed_time))

# Parse the SQL data into a dataframe
# strip the tuples in genres list
start = time()
# genre_ids 0 based indexing
genre_ids = np.array([genre[0] for genre in genres]) - 1
genres = [genre[1] for genre in genres]
# genres.sort()  # sort genres alphabetically IN-place
# Parse this data into a nicer pandas format
# remove the 6 None entries in col_names due to adhering with Python's DB-API
# standard
col_names = [cols[0] for cols in col_names]
# create a dict for a pandas dataframe
table_dict = {}
for key in col_names:
    # table_dict[key] = [entry[col_names.index(key)] for entry in data]
    table_dict[key] = [entry[col_names.index(key) + 1] for entry in data]

# Create dataframe
# WHAT GUARANTEE IS THERE IS THERE THAT TWO DIFFERENT "for entry in data" WILL
# ITERATE IN THE SAME ORDER? I CAN ONLY HOPE
# convert to 0 based notation by subtracting 1
idsMovie = np.array([entry[0] for entry in data]) - 1
df_kodi_movie = pd.DataFrame(table_dict, index=idsMovie)

# convert every entry in Genres column to a set. E.g.,
# 'Animation / Comedy' --> {'Animation', 'Comedy'}
# for each_movie_genres in df_kodi_movie.loc[:, 'Genres']:
# genres_list = each_movie_genres.split('/')
# range doesn't work because there exists some idMovie whose genre is empty
# and so has been filtered out by the SQL query.
# for i in range(0, df_kodi_movie.index.size)`:
for i in df_kodi_movie.index:
    # split string using '/' and then strip whitespaces from each element in
    # list
    genres_list = df_kodi_movie.Genres[i].split('/')
    df_kodi_movie.Genres[i] = set([genre.strip() for genre in genres_list])

df_kodi_genre = pd.DataFrame({'Genres': genres}, index=genre_ids)

genres_link_genres = np.array([entry[0] for entry in genres_link]) - 1
genres_link_idMovies = np.array([entry[1] for entry in genres_link]) - 1

# if you look, the list genress_link_genres has repeating elements. The good
# thing about Pandas is that it allows duplicate indices. So for e.g.
# df_kodi_genre_link.loc[0] will list all idMovies with genre_id=0.
# That's awesome!
df_kodi_genre_link = pd.DataFrame({'idMovie': genres_link_idMovies}, index=genres_link_genres)

end = time()
elapsed_time = timedelta(seconds=end-start)
print('Data parsed into pandas tables. {0}'.format(elapsed_time))
# ----------------------------------------------------------------------- #

# ----------------------------------------------------------------------- #
# STEP 2, Compute genre correlations
# create genre correlations dataframe
start = time()
df_genre_corrs = gen_corr_matrix(df_kodi_movie, df_kodi_genre, df_kodi_genre_link)
end = time()
elapsed_time = timedelta(seconds=end-start)
print('Genre correlations matrix created. {0}'.format(elapsed_time))

# Visualize genre correlations
# plt.figure()
# plt.pcolormesh(np.array(df_genre_corrs, dtype=float), cmap='gnuplot', edgecolor=None)
# plt.colorbar()
# # create labels
# x_points = []
# x_labels = []
# for i in range(0, df_genre_corrs.index.size):
#     x_points.append(i + 0.5)
#     x_labels.append('{0:.3}'.format(df_genre_corrs.index[i]))
# plt.xticks(x_points, x_labels)
# plt.yticks(x_points, x_labels)
# plt.xlim(0, df_genre_corrs.index.size)
# plt.ylim(0, df_genre_corrs.index.size)
# plt.title('Genre Correlations Matrix')
# plt.show()

# ----------------------------------------------------------------------- #

# ----------------------------------------------------------------------- #
# STEPS 3 and 4. Specify user preferred genres and compute recommendation
# points for each movie
prompt = ''
while not (prompt == 'y' or prompt == 'n'):
    prompt = str(input('Would you like to specify a genre set? If you want a list of genres, type l [y/n/l]: '))
    if prompt == 'y':
        genre_ids_input = input('Enter the genreIDs of interest. E.g. entering 0,1 means you are interested in {0}, {1}: '.format(df_kodi_genre.loc[0, 'Genres'], df_kodi_genre.loc[1, 'Genres']))
        try:
            preferred_genres_set = set([df_kodi_genre.loc[int(i), 'Genres'] for i in genre_ids_input.split(',')])
            print('Preferred genres = {0}'.format(preferred_genres_set))
            print('Here are your top 10 recommendations.')
            # loop over movies
            for k in df_kodi_movie.index:
                df_kodi_movie.loc[k, 'Recommendation Points'] = gen_recomm_pts(df_genre_corrs, preferred_genres_set, df_kodi_movie.loc[k, 'Genres'], float(df_kodi_movie.loc[k, 'Rating']))
            # Normalize recommendation points column
            df_kodi_movie.loc[:, 'Recommendation Points'] = df_kodi_movie.loc[:, 'Recommendation Points']/df_kodi_movie.loc[:, 'Recommendation Points'].max()
            print(df_kodi_movie[['MovieName', 'Recommendation Points', 'Genres', 'Rating', 'Year']].sort_values(by=['Recommendation Points'], ascending=False).head(10))
            prompt = ''
        except:
            print('Could not read genres, please specify correctly')
            prompt = ''
    elif prompt == 'l':
        print('Here is the list of genres. Left Column: genreID, Right Column: Genre\n{0}'.format(df_kodi_genre.Genres.sort_values()))
    elif prompt == 'n':
        print('Thanks for trying out the algorithm. Feedback welcome.')
        sys.exit()

# preferred_genres_set = {'Drama', 'Comedy'}
#
# start = time()
# # loop over movies
# for k in df_kodi_movie.index:
#     df_kodi_movie.loc[k, 'Recommendation Points'] = gen_recomm_pts(df_genre_corrs, preferred_genres_set, df_kodi_movie.loc[k, 'Genres'], float(df_kodi_movie.loc[k, 'Rating']))
#
# # Normalize recommendation points column
# df_kodi_movie.loc[:, 'Recommendation Points'] = df_kodi_movie.loc[:, 'Recommendation Points']/df_kodi_movie.loc[:, 'Recommendation Points'].max()
# end = time()
# elapsed_time = timedelta(seconds=end-start)
# print('Finished generating recommendation points. {0}'.format(elapsed_time))
# print('Preferred genres = {0}'.format(preferred_genres_set))
# print(df_kodi_movie.sort_values(by=['Recommendation Points'], ascending=False).head(10))
