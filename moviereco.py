# -*- coding: utf-8 -*-
"""
Author: Nishan Singh Mann (nishan.singh.mann@gmail.com)

Main setup file that reads in from the SQlite database and runs the algorithm.
"""

import sqlite3
import ipdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from time import time
from datetime import timedelta
import sys
from algos import gen_corr_matrix, gen_recomm_pts
from myio import parse_kodi_database

# ----------------------------------------------------------------------- #
# STEP 1: Parse sql data into Python
# Read contents from database file
#db_path = 'MyVideos99_NoBollywood.db'
try:
    db_path = sys.argv[1]
except:
    print('Please specify database. Exiting.')
    sys.exit()

(df_kodi_movie, df_kodi_genre, df_kodi_genre_link) = parse_kodi_database(db_path)
sys.exit()



# ----------------------------------------------------------------------- #
# STEP 2, Compute genre correlations
# create genre correlations dataframe
start = time()
df_genre_corrs = gen_corr_matrix(df_kodi_movie, df_kodi_genre, df_kodi_genre_link)
end = time()
elapsed_time = timedelta(seconds=end-start)
print('Genre correlations matrix created. {0}'.format(elapsed_time))

# Visualize genre correlations
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
plt.title('Genre Correlations Matrix')
plt.show()

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
