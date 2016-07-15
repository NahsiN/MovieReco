# Movie Recommendation Algorithm for Kodi

This is a content-based [recommendation system](https://en.wikipedia.org/wiki/Recommender_system#cite_note-9)
for movies using genre correlations as outlined by [Choi, Ko and Han][Choi2012].
It uses Kodi's SQLite database provided by the user to generate a genre correlation matrix unique to the user. Given a set of prefered genres,
the program then uses the correaltion matrix to recommend movies.
This is only a proof of concept. Perhaps if there is enough interest and I have enough time, I will develop this further adding some of my own ideas in
the mix ;).

## Requirements
1. The [SciPy stack](https://www.scipy.org/install.html) for **Python3**.
    For Debian based distribuitions such as Ubuntu the following
    should suffice

    `` sudo apt-get install python3-numpy python3-scipy python3-matplotlib ipython3 ipython3-notebook python3-pandas python3-sympy python3-nose
    ``
2. A SQLite database for videos created by Kodi usually named MyVideos#.db.
  I have Jarvis v16.1 installed on my machine and the database is called MyVideos99.db.
  Please read the Kodi [wiki](https://www.scipy.org/install.html) to find your
  userdata folder.

## Usage
**Please** make a copy of your database. Let's call it Kodi.db. Run the program
as follows in your terminal

``
python3 moviereco.py Kodi.db
``

or in ipython3

``
%run moviereco.py Kodi.db
``

The program will read your SQLite database and generate the genre correaltion
matrix. If all goes well you will end up with the following prompt

``Would you like to specify a genre set? If you want a list of genres, type l [y/n/l]: ``

Typing _l_ will give you a list of genres and the associated genreIDs as read from your
database file. A sample ouput is as follows (Note: I use 0 based indexing whereas Kodi's original database uses 1 based indexing)

| genreID | Genre |
| ------- | ----- |
| 3   | Action |
| 5   | Adventure |
| 0   | Animation |
| 11  | Biography |
| 8   | Comedy    |

Typing _y_ will allow you to enter the genreIDs of interest, for example, if
you want to see Action, Adventure, Biography related movies, you would type
3,5,11

The algorithm will do it's thing and spit out the top 10 recommended movies
rated on a continuous scale ranging from 0 to 1. At this point, you can either continue
testing the algorithm by trying out difference genre combinations or quit by typing _n_.

__TIPS__: Try out some crazy genre combinations to see what the algorithm gives.
Examples: {'Sci-Fi', 'Sport'} (more to be listed)

Enjoy testing and feedback is always welcome. I will try to be punctual but with a
crazy schedule, I make no guarantees! If anyone knows how to generate fake
databases for Kodi to use as examples, please contact me.


References:

Choi, S. M., Ko, S. K., & Han, Y. S. (2012). A movie recommendation algorithm based on genre correlations. Expert Systems with Applications, 39(9), 8079–8085. http://doi.org/10.1016/j.eswa.2012.01.132

[Choi2012]: http://dx.doi.org/10.1016/j.eswa.2012.01.132
