# -*- coding: utf-8 -*-
"""
Author: Nishan Singh Mann (nishan.singh.mann@gmail.com)

Contains the two algorithms for genrating genre correlation matrix and
recommendation points
"""

import numpy as np
import ipdb
import pandas as pd

def gen_corr_matrix(df_kodi_movie, df_kodi_genre, df_kodi_genre_link):
    """
    Creates the genre correlation matrix.

    Parameters
    ----------
    df_kodi_movie: Pandas dataframe with info about movie
    df_kodi_genre: dataframe with info about genres
    df_kodi_genre_link : link between genre and idMovie

    Returns
    -------
    df_genre_corrs: Genre correlation matrix
    """

    # create a list of genres
    genres = df_kodi_genre.loc[:, 'Genres'].sort_values().tolist()

    # Initialize correaltion matrix
    df_genre_corrs = pd.DataFrame(index=genres, columns=genres)
    df_genre_corrs.iloc[:, :] = 0

    # MAIN ALGO constructs genre correlation matrix
    # loop over genres (i)
    for gi in genres:
        # select all movies having genre gi
        gi_id = df_kodi_genre[df_kodi_genre.Genres == gi].index  # id for genre gi
        try:
            movie_ids = df_kodi_genre_link.loc[gi_id]
        except KeyError:
            print('No movies with genre={0} found'.format(gi))
            # empty dataframe so that the l156 loop is skipped
            movie_ids = pd.DataFrame(columns=['idMovie'])
        # movie_ids = []
        # # BIGGEST TIME HOG
        # for k in df_kodi_movie.index:
        #     if gi in df_kodi_movie.loc[k, 'Genres']:
        #         movie_ids.append(k)
        #if len(movie_ids) == 0:
        #    print('No movies with genre={0} found'.format(gi))

        # loop over the other genres (j)
        # this statement relies on genres being alphabetically SORTED
        genres_geq_gi = [gj for gj in genres if gj >= gi]
        # for gj in genres:
        for gj in genres_geq_gi:
            # create genre set G_ij
            g_ij = {gi, gj}
            # consider only those movies that have gi as a genre
            # if len(movie_ids) == 0:
            #     pass
            # else:
            # loop only over the movies that have genre gi to determine
            # correaltions
            # for k in movie_ids:
            for k in movie_ids.loc[:, 'idMovie']:
                # computes intersection of G_ij with movie genre set
                common_genres = g_ij & df_kodi_movie.loc[k, 'Genres']
                if len(common_genres) == 2 and gi != gj:
                    df_genre_corrs.loc[gi, gj] += 1
                    df_genre_corrs.loc[gj, gi] += 1
                elif len(common_genres) == 1 and gi == gj:
                    df_genre_corrs.loc[gi, gj] += 1

    # Normalize the total movie count for genre gi to unity
    for gi in genres:
        if df_genre_corrs.loc[gi, gi] != 0:
            # test = df_genre_corrs.loc[gi, :]/df_genre_corrs.loc[gi, gi]
            df_genre_corrs.loc[gi, :] = df_genre_corrs.loc[gi, :]/df_genre_corrs.loc[gi, gi]
            if (df_genre_corrs.loc[gi, :] > 1).any():
                raise AssertionError('Correlation matrix has entries exceeding 1. Investigate.')

    return df_genre_corrs


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
    # common genres between user preferred genres and movie genre set
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


# determine index of coincidence for preferred_genres_set={gi, gj} for all i,j
def index_of_coincidence(num_users, df_movie, df_genre_corrs, genre_corrs_matrices, genres):
    """
    Generate average index of coincidence for the top 3 predictions.
    This tests how stable the predictions are w.r.t. perturbations to the genre correaltion
    matrix

    Parameters
    ----------
    num_users : number of users
    df_genre_corrs : Genre correlation matrix for whole dataset
    df_movie :
    genre_corrs_matrices : Correlation matrices generated for each user's collection
    NOTE: num_users <= N.
    genres : list of genres that determines the couples [gi, gj] for which
    the index of coincidence is calculated


    Returns
    -------
    avg_IOC : average index of coincidence for the top 3 recommendations
    genre_couples_R1_ioc : index of coincidence for the top (1st) recommendation
                           for each genre couple possible from the list of
                           genres.
    genre_couples_R2_ioc : index of coincidence for the second recommendation
    genre_couples_R3_ioc : index of coincidence for the third recommendation
    """

    recomm_movies_var = pd.DataFrame(columns=['PreferredGenresSet', 'MovieName_R1', 'R1Points', 'MovieName_R2', 'R2Points', 'MovieName_R3', 'R3Points'])
    num_genres = len(genres)
    total_count = -1

    # genres = df_genre.loc[:, 'Genres'].sort_values().tolist()
    genres.sort()
    # To avoid changing the dataframe df_genre_corrs in-place
    df_genre_corrs_user = df_genre_corrs.copy()

    for user_i in range(0, num_users):
        print('\nUser number = {0}'.format(user_i))
        # use the randomly generated corr matrix for each user
        df_genre_corrs_user.iloc[:, :] = genre_corrs_matrices[:, :, user_i]
        # selecting one on the diagonals didn't make much difference
        # tmp_corrs_matrix = genre_corrs_matrices[:, :, user_i]
        # tmp_corrs_matrix[np.diag_indices_from(tmp_corrs_matrix)] = 1
        # df_genre_corrs_user.iloc[:, :] = tmp_corrs_matrix
        # loop through all possible {gi, gj} couples to determine top 3 recommendations
        for gi in genres:
        # for gi in ['Action', 'Adventure', 'Animation', 'Children\'s']:
            genres_geq_gi = [gj for gj in genres if gj >= gi]
            # genres_geq_gi = [gj for gj in ['Action', 'Adventure', 'Animation', 'Children\'s'] if gj >= gi]
            for gj in genres_geq_gi:
                # count_genre_sets += 1
                total_count += 1
                preferred_genres_set = set([gi, gj])
                recomm_movies_var.loc[total_count, 'PreferredGenresSet'] = preferred_genres_set
                # print('Total count = {0}, Genre tuple = {1}'.format(total_count, preferred_genres_set))
                # number of elements in upper triangular is N(N+1)/2
                print('Total count = {0} of {1}. Genre couple = {2}'.format(total_count, num_users*0.5*num_genres*(num_genres + 1) - 1, preferred_genres_set))

                # loop over movies
                for k in df_movie.index:
                    df_movie.loc[k, 'Recommendation Points'] = gen_recomm_pts(df_genre_corrs_user, preferred_genres_set, df_movie.loc[k, 'Genres'], float(df_movie.loc[k, 'Rating']))
                # Normalize recommendation points column
                df_movie.loc[:, 'Recommendation Points'] = df_movie.loc[:, 'Recommendation Points']/df_movie.loc[:, 'Recommendation Points'].max()
                # select top 3 recommendations
                top_3_recomms = df_movie[['MovieName', 'Recommendation Points', 'Genres', 'Rating', 'Year']].sort_values(by=['Recommendation Points'], ascending=False).head(3)

                # add entries to dataframe indexed by total_count
                recomm_movies_var.loc[total_count, 'MovieName_R1'] = top_3_recomms.loc[top_3_recomms.index[0], 'MovieName']
                recomm_movies_var.loc[total_count, 'R1Points'] = top_3_recomms.loc[top_3_recomms.index[0], 'Recommendation Points']
                recomm_movies_var.loc[total_count, 'MovieName_R2'] = top_3_recomms.loc[top_3_recomms.index[1], 'MovieName']
                recomm_movies_var.loc[total_count, 'R2Points'] = top_3_recomms.loc[top_3_recomms.index[1], 'Recommendation Points']
                recomm_movies_var.loc[total_count, 'MovieName_R3'] = top_3_recomms.loc[top_3_recomms.index[2], 'MovieName']
                recomm_movies_var.loc[total_count, 'R3Points'] = top_3_recomms.loc[top_3_recomms.index[2], 'Recommendation Points']
                # recomm_genre_corrs_variance.loc[total_count, '']


    i = -1
    j = -1
    genre_couples_ioc = np.zeros((num_genres, num_genres), dtype='float')
    genre_couples_R1_ioc = np.zeros((num_genres, num_genres), dtype='float')
    genre_couples_R2_ioc = np.zeros((num_genres, num_genres), dtype='float')
    genre_couples_R3_ioc = np.zeros((num_genres, num_genres), dtype='float')

    # for gi in ['Action', 'Adventure', 'Animation', 'Children\'s']:
    for gi in genres:
        i += 1
        j = i
        # genres_geq_gi = [gj for gj in ['Action', 'Adventure', 'Animation', 'Children\'s'] if gj >= gi]
        genres_geq_gi = [gj for gj in genres if gj >= gi]
        for gj in genres_geq_gi:
            # print('(i,j)=({0},{1})'.format(i, j))
            preferred_genres_set = set([gi, gj])
            # filter movies accordinig to genre_couple {gi, gj}
            recomm_movies_genre_set = recomm_movies_var[recomm_movies_var.loc[:, 'PreferredGenresSet'] == preferred_genres_set]
            movies_R1 = recomm_movies_genre_set.loc[:, 'MovieName_R1']
            movies_R2 = recomm_movies_genre_set.loc[:, 'MovieName_R2']
            movies_R3 = recomm_movies_genre_set.loc[:, 'MovieName_R3']
            R1_points_mean = recomm_movies_genre_set.loc[:, ['R1Points']].mean()
            R2_points_mean = recomm_movies_genre_set.loc[:, ['R2Points']].mean()
            R3_points_mean = recomm_movies_genre_set.loc[:, ['R3Points']].mean()

            # ioc = index of coincidence
            # value_counts counts the number of times a unique entry occurs
            R1_ioc = movies_R1.value_counts(normalize=True).max()
            R2_ioc = movies_R2.value_counts(normalize=True).max()
            R3_ioc = movies_R3.value_counts(normalize=True).max()
            # avg_ioc = np.mean(np.array([R1_ioc, R2_ioc, R3_ioc]))
            # compute average index of coincidence by weighting using recommendation
            # points
            avg_ioc = np.average(np.array([R1_ioc, R2_ioc, R3_ioc]), weights = np.squeeze(np.array([R1_points_mean, R2_points_mean, R3_points_mean])/np.sum([R1_points_mean, R2_points_mean, R3_points_mean])))
            print('Genre Set={0}. R1 IOC = {1}. Average IOC = {2}'.format(preferred_genres_set, R1_ioc, avg_ioc))
            # print('Genre Set={0}. Average IOC = {1}'.format(preferred_genres_set, avg_ioc))
            genre_couples_ioc[i, j] = avg_ioc
            genre_couples_ioc[j, i] = avg_ioc
            genre_couples_R1_ioc[i, j] = R1_ioc
            genre_couples_R2_ioc[i, j] = R2_ioc
            genre_couples_R3_ioc[i, j] = R3_ioc
            genre_couples_R1_ioc[j, i] = genre_couples_R1_ioc[i, j]
            genre_couples_R2_ioc[j, i] = genre_couples_R2_ioc[i, j]
            genre_couples_R3_ioc[j, i] = genre_couples_R3_ioc[i, j]
            j += 1

    return (genre_couples_ioc, genre_couples_R1_ioc, genre_couples_R2_ioc, genre_couples_R3_ioc, recomm_movies_var)
    # perturb correlation matrix using normal dist. for each user
    # for i in range(0, df_genre_corrs_copy.index.size):
    #     for j in range(0, df_genre_corrs_copy.index.size):
    #         # ASSUME a normal distribuition. You need to justify later
    #         # perturb only off diagonal elements for now. because
    #         # the genre should always be perfectly correlated to
    #         # itself
    #         if i != j:
    #             # THIS WILL CHANGE THE DATAFRAME IN-PLACE. MUTABLE OBJECT
    #             # df_genre_corrs.iloc[i, j] = df_genre_corrs.iloc[i, j] + genre_corrs_std_matrix[i, j]*np.random.randn(1)
    #             # df_genre_corrs_copy.iloc[i, j] = df_genre_corrs_copy.iloc[i, j] + genre_corrs_std_matrix[i, j]*np.random.randn(1)
    #             df_genre_corrs_copy.iloc[i, j] = df_genre_corrs_copy.iloc[i, j]
    #             # this is needed to make sure one doesn't end up with negative correlations which will end up subtracting points
    #             if df_genre_corrs_copy.iloc[i, j] < 0:
    #                 df_genre_corrs_copy.iloc[i, j] = 0
