# -*- coding: utf-8 -*-
"""
All the I/O routines I use depending upon the dataset used.
The goal is to parse the dataset/s into standardized dataframes used for
generating genre correlation matrix

Author: Nishan Singh Mann (nishan.singh.mann@gmail.com)
"""

import sqlite3
import numpy as np
import pandas as pd
from time import time
import datetime
import ipdb

def parse_kodi_database(fname):
    """
    Parses Kodi's database into a pandas dataframe

    Parameters
    ----------
    fname : filename of SQLite database

    Returns
    -------
    df_kodi_movie : Dataframe with all the relevant movie info
    df_kodi_genre : dataframe for genre and their genreIDs
    df_kodi_genre_link : Link between what movie has what genre
    """

    start = time()
    # open a connection to database
    conn = sqlite3.connect(fname)
    # open a cursor object
    cur = conn.cursor()

    # Read relevant info from database
    try:
        cur.execute("""SELECT idMovie, c00 as 'MovieName', c05 as 'Rating', c07 as 'Year',
                c14 as 'Genres' FROM movie WHERE Genres != '' LIMIT 1000""")
    except:
        print('{0} Either this database does not exist or something else went wrong. Exiting.'.format(fname))
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
    elapsed_time = datetime.timedelta(seconds=end - start)
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
    elapsed_time = datetime.timedelta(seconds=end-start)
    print('Data parsed into pandas tables. {0}'.format(elapsed_time))

    return (df_kodi_movie, df_kodi_genre, df_kodi_genre_link)
    # ----------------------------------------------------------------------- #


def parse_movielens_database_100k(fname_item, fname_genre, fname_data):
    """
    Parses movielens database and returns dataframes compatible with my notation

    Parameters
    ----------
    fname_item : filename of u.item file
    fname_genre : filename of u.genre file
    fname_data : filename of u.data

    Returns
    -------
    Returns dataframes using the same notation as my Kodi dataframes in the
    method above.
    df_movie :
    df_genre :
    df_genre_link :
    """

    # movie_info = ['idMovie', 'MovieName', 'ReleaseDate', 'VideoReleaseDate', 'ImdbUrl']
    movie_info = ['MovieName', 'Year', 'VideoReleaseDate', 'ImdbUrl']
    genres = ['unknown', 'Action', 'Adventure', 'Animation', 'Children\'s', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
    item_col_names = movie_info + genres
    # ratings_col_names = ['idUser', 'idMovie', 'Rating', 'unix_timestamp']
    data_col_names = ['idUser', 'Rating', 'unix_timestamp']


    # latin-1 encoding is critical
    # use idMovie as index
    # './MovieLens/ml-100k/u.item'
    ml_item = pd.read_csv(fname_item, sep='|', encoding='latin-1', names=item_col_names, header=None, index_col=0)
    # './MovieLens/ml-100k/u.genre'
    ml_genre = pd.read_csv(fname_genre, sep='|', header=None, names=['Genres'], index_col=1, encoding='latin-1')
    # use idMovie as index
    # './MovieLens/ml-100k/u.data'
    ml_data = pd.read_csv(fname_data, sep='\t', header=None, names=data_col_names, index_col=1, encoding='latin-1')
    print('MovieLens databases reading complete.')

    # digest above data into ['Genres', 'MovieName', 'Rating', 'Year'] for df_movie
    # shift index to 0 based notation
    ml_item.index = ml_item.index - 1
    ml_data.index = ml_data.index - 1

    # build df_movie
    df_movie = ml_item.loc[:, ['MovieName', 'Year']]

    # build genres and ratings column
    ml_item_subframe = ml_item.loc[:, genres]  # subframe with only genres
    genres_list = []
    for idMovie in ml_item_subframe.index:
        # select only nonzero genre columns since genre of movie is indicated with 1
        nonzero_genre_cols = ml_item_subframe.loc[idMovie, :].nonzero()
        genres_list.append(set(ml_item_subframe.columns[nonzero_genre_cols].tolist()))
        # TIME HOG
        # df_movie.loc[idMovie, 'Rating'] = ml_data.loc[idMovie, 'Rating'].mean()
    df_movie.loc[:, 'Genres'] = genres_list
    df_movie.loc[:, 'Rating'] = ml_data.groupby(level=0).mean()  # much faster than l169

    # build df_genre
    df_genre = ml_genre.copy()
    # build genre links
    idMovies_array = np.empty(0, dtype=int)
    idGenres_array = np.empty(0, dtype=int)
    for idGenre in df_genre.index:
        # genre associated with idGenre. type str
        genre = df_genre.loc[idGenre, 'Genres']
        # find movie ids having genre
        try:
            idMovies = ml_item[ml_item.loc[:, genre] == 1].index
        except (KeyError):
            print('No movies with genre={0} found'.format(genre))
        # genre id needs to be repeated for the number of movies found
        idsGenre = np.repeat(idGenre, idMovies.size)
        idMovies_array = np.append(idMovies_array, idMovies)
        idGenres_array = np.append(idGenres_array, idsGenre)

    df_genre_link = pd.DataFrame({'idMovie': idMovies_array}, index=idGenres_array)

    return(df_movie, df_genre, df_genre_link)

    # convert 01-Jan-1995 to datetime object. leave for now
    # datetime.datetime.strptime('01-Jan-1995', '%d-%b-%Y')

def parse_movielens_database_20m():
    """
    Parse the 20M dataset
    """
    pass
