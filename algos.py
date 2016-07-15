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
            df_genre_corrs.loc[gi, :] = df_genre_corrs.loc[gi, :]/df_genre_corrs.loc[gi, gi]

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
