# -*- coding: utf-8 -*-
"""
Author: Nishan Singh Mann (nishan.singh.mann@gmail.com)
PLEASE CHECK OUT GITHUB REPOSITORY FOR FULL CODE

Repository: https://github.com/NahsiN/MovieReco/tree/movielens_statistics

Main setup file that reads in the Movielens database and runs statistics
mimicking 100 or so different users with their movie collections and different
correlation matrices
quantities of interest
1) genre correlation matrix
2) genre correlation matrix for 100 users each with 150 movies
3) The index of coincidence between two genres
"""

import sqlite3
import ipdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from time import time
from datetime import timedelta
import sys
from algos import gen_corr_matrix, gen_recomm_pts, index_of_coincidence
from parsers import parse_kodi_database, parse_movielens_database_100k

# ----------------------------------------------------------------------- #
# STEP 1: Parse sql data into Python
# Read contents from database file
# db_path = 'MyVideos99_NoBollywood.db'
# try:
#     db_path = sys.argv[1]
# except:
#     print('Please specify database. Exiting.')
#     sys.exit()
# (df_movie, df_genre, df_genre_link) = parse_kodi_database(db_path)

# for movielens
# try:
#     item_path = sys.argv[1]
#     genre_path = sys.argv[2]
#     data_path = sys.argv[3]
# except:
#     print('Please specify item, genre, data paths. Exiting')
#     sys.exit()
item_path = './MovieLens/ml-100k/u.item'
genre_path = './MovieLens/ml-100k/u.genre'
data_path = './MovieLens/ml-100k/u.data'
(df_movie, df_genre, df_genre_link) = parse_movielens_database_100k(item_path, genre_path, data_path)



# ----------------------------------------------------------------------- #
# STEP 2, Compute genre correlations
# create genre correlations dataframe
num_users = 100
num_movies_per_user = 150
num_genres = df_genre.index.size
sample_users = np.random.random_integers(df_movie.index.min(), df_movie.index.max(), size=(num_users, num_movies_per_user))

# ENSURE the movie ids generated for each user are unique.
user_i = 0
while user_i < num_users:
    unique_sample_movies = 0
    while unique_sample_movies < num_movies_per_user:
        sample_movies = np.random.random_integers(df_movie.index.min(), df_movie.index.max(), size=(1, num_movies_per_user))
        unique_sample_movies = np.unique(sample_movies).size
    sample_users[user_i, :] = sample_movies
    print('{0} unique movies set for user number {1} generated.'.format(num_movies_per_user, user_i))
    user_i += 1

genre_corrs_matrices = np.zeros((num_genres, num_genres, num_users), dtype='float')
genre_corrs_mean_matrix = np.zeros((num_genres, num_genres), dtype='float')
genre_corrs_std_matrix = np.zeros((num_genres, num_genres), dtype='float')

for user_i in range(0, num_users):
    print('User number={0}'.format(user_i))
    df_movie_subset = df_movie.loc[sample_users[user_i, :]]
    df_genre_link_subset = df_genre_link[df_genre_link.loc[:, 'idMovie'].isin(df_movie_subset.index)]
    df_genre_corrs = gen_corr_matrix(df_movie_subset, df_genre, df_genre_link_subset)
    genre_corrs_matrices[:, :, user_i] = np.array(df_genre_corrs)

for i in range(0, num_genres):
    for j in range(0, num_genres):
        genre_corrs_mean_matrix[i, j] = np.mean(genre_corrs_matrices[i, j, :])
        genre_corrs_std_matrix[i, j] = np.std(genre_corrs_matrices[i, j, :])

start = time()
df_genre_corrs = gen_corr_matrix(df_movie, df_genre, df_genre_link)
end = time()
elapsed_time = timedelta(seconds=end-start)
print('Genre correlations matrix created. {0}'.format(elapsed_time))

# Visualize genre correlations
fig = plt.figure()
fig.add_axes([0.1,0.1,0.85,0.85])

# create labels
x_points = []
x_labels = []
for i in range(0, df_genre_corrs.index.size):
    x_points.append(i + 0.5)
    x_labels.append('{0:.3}'.format(df_genre_corrs.index[i]))
plt.pcolormesh(genre_corrs_mean_matrix, cmap='gnuplot', edgecolor=None, vmin=0, vmax=1)
plt.xticks(x_points, x_labels)
plt.yticks(x_points, x_labels)
plt.colorbar(orientation='horizontal')
plt.xlim(0, df_genre_corrs.index.size)
plt.ylim(0, df_genre_corrs.index.size)
plt.title('Mean genre correlation matrix for {0} users'.format(num_users))
plt.savefig('mean_genre_corrs_matrix.pdf')

fig = plt.figure()
fig.add_axes([0.1,0.1,0.85,0.85])
plt.pcolormesh(genre_corrs_std_matrix, cmap='gnuplot', edgecolor=None, vmin=0, vmax=1)
plt.xticks(x_points, x_labels)
plt.yticks(x_points, x_labels)
plt.colorbar(orientation='horizontal')
plt.xlim(0, df_genre_corrs.index.size)
plt.ylim(0, df_genre_corrs.index.size)
plt.title('Std genre correlation matrix for {0} users'.format(num_users))
plt.savefig('std_genre_corrs_matrix.pdf')

fig = plt.figure()
fig.add_axes([0.1,0.1,0.85,0.85])
plt.pcolormesh(np.array(df_genre_corrs, dtype=float), cmap='gnuplot', edgecolor=None, vmin=0, vmax=1)
plt.colorbar(orientation='horizontal')
plt.xticks(x_points, x_labels)
plt.yticks(x_points, x_labels)
plt.xlim(0, df_genre_corrs.index.size)
plt.ylim(0, df_genre_corrs.index.size)
plt.title('Genre correlations matrix for {0} movies'.format(df_movie.index.size))
plt.savefig('full_genre_corrs_matrix.pdf')

plt.show()

# ----------------------------------------------------------------------- #

# ----------------------------------------------------------------------- #
# STEPS 3 and 4. Specify user preferred genres and compute recommendation

# genres = ['Action', 'Adventure', 'Comedy', 'Drama', 'Romance', 'Horror', 'Thriller']
genres = ['Action', 'Adventure', 'Comedy', 'Drama', 'Romance', 'Horror', 'Thriller']
num_users_subset = num_users
(genre_couples_ioc, genre_couples_R1_ioc, genre_couples_R2_ioc, genre_couples_R3_ioc, recomm_movies_var) = index_of_coincidence(num_users_subset, df_movie, df_genre_corrs, genre_corrs_matrices, genres)

 # recomm_movies_var[recomm_movies_var.loc[:, 'PreferredGenresSet'] == set(['Action'])].loc[:, ['MovieName_R1', 'R1Points']]

# create labels
x_points = []
x_labels = []
for i in range(0, len(genres)):
    x_points.append(i + 0.5)
    x_labels.append('{0:.3}'.format(genres[i]))

fig = plt.figure()
fig.add_axes([0.1, 0.1, 0.85, 0.85])
plt.pcolormesh(genre_couples_ioc, cmap='gnuplot', edgecolor=None, vmin=0, vmax=1)
plt.xticks(x_points, x_labels)
plt.yticks(x_points, x_labels)
plt.colorbar(orientation='horizontal')
plt.xlim(0, len(genres))
plt.ylim(0, len(genres))
plt.title('Average index of coincidence for {0} users ({1} movies each)'.format(num_users_subset, num_movies_per_user))
plt.savefig('avg_ioc_' + '_'.join(genres) + '_' + str(num_users) + '.pdf')


# points for each movie
# prompt = ''
# while not (prompt == 'y' or prompt == 'n'):
#     prompt = str(input('Would you like to specify a genre set? If you want a list of genres, type l [y/n/l]: '))
#     if prompt == 'y':
#         genre_ids_input = input('Enter the genreIDs of interest. E.g. entering 0,1 means you are interested in {0}, {1}: '.format(df_genre.loc[0, 'Genres'], df_genre.loc[1, 'Genres']))
#         try:
#             preferred_genres_set = set([df_genre.loc[int(i), 'Genres'] for i in genre_ids_input.split(',')])
#             print('Preferred genres = {0}'.format(preferred_genres_set))
#             # perturb correaltion matrix
#             for i in range(0, df_genre_corrs.index.size):
#                 for j in range(0, df_genre_corrs.index.size):
#                     df_genre_corrs.iloc[i, j] = df_genre_corrs.iloc[i, j] + genre_corrs_std_matrix[i, j]*np.random.randn(1)
#             # loop over movies
#             for k in df_movie.index:
#                 df_movie.loc[k, 'Recommendation Points'] = gen_recomm_pts(df_genre_corrs, preferred_genres_set, df_movie.loc[k, 'Genres'], float(df_movie.loc[k, 'Rating']))
#             # Normalize recommendation points column
#             df_movie.loc[:, 'Recommendation Points'] = df_movie.loc[:, 'Recommendation Points']/df_movie.loc[:, 'Recommendation Points'].max()
#             print('Here are your top 10 recommendations.')
#             print(df_movie[['MovieName', 'Recommendation Points', 'Genres', 'Rating', 'Year']].sort_values(by=['Recommendation Points'], ascending=False).head(10))
#             prompt = ''
#         except:
#             print('Could not read genres, please specify correctly')
#             prompt = ''
#     elif prompt == 'l':
#         print('Here is the list of genres. Left Column: genreID, Right Column: Genre\n{0}'.format(df_genre.Genres.sort_values()))
#     elif prompt == 'n':
#         print('Thanks for trying out the algorithm. Feedback welcome.')
#         sys.exit()


# preferred_genres_set = {'Drama', 'Comedy'}
#
# start = time()
# # loop over movies
# for k in df_movie.index:
#     df_movie.loc[k, 'Recommendation Points'] = gen_recomm_pts(df_genre_corrs, preferred_genres_set, df_movie.loc[k, 'Genres'], float(df_movie.loc[k, 'Rating']))
#
# # Normalize recommendation points column
# df_movie.loc[:, 'Recommendation Points'] = df_movie.loc[:, 'Recommendation Points']/df_movie.loc[:, 'Recommendation Points'].max()
# end = time()
# elapsed_time = timedelta(seconds=end-start)
# print('Finished generating recommendation points. {0}'.format(elapsed_time))
# print('Preferred genres = {0}'.format(preferred_genres_set))
# print(df_movie.sort_values(by=['Recommendation Points'], ascending=False).head(10))
