# Movie Recommendation Algorithm: Scientific Testing Branch

If you are viewing this branch, please see the [README](https://github.com/NahsiN/MovieReco/blob/master/README.md)
on the master branch for the scope of the project. This branch exists for running
various scientific tests on my algorithm. The basic idea is to study how the recommendations vary
depending upon the user's genre preferences. As it stands, if you use your own
movie collection or the ml-100k dataset, the algorithm will generate the same
recommendations for _everybody_ because the correaltion matrix is unchanged.
But what if we change the correaltion matrix, how much do the recommendations
change?

To answer this, I use the ml-100k dataset which contains 1682 movies to generate
100 randomly sampled subsets with 150 elements each. In other words, this
simulates 100 different Kodi users each with their own movie collection of 150
movies. Since each user has a different collection, their genre correlation
matrix will naturally differ. And I want to study how the recommendations change
when each user uses their own correlation matrix on the ml-100k dataset.

Other technicalities aside, I use the index of coincidence as a measure to test
the variability of the recommendations. I consider two genres at a time. So for
example, from {Action, Adventure, Comedy}, I consider the subsets
{Action}, {Adventure}, {Comedy}, {Action, Adventure}, {Adventure, Comedy}
and {Action, Comedy}. Using these 6 subsets as the user preffered genres,
I calculate the average index of coincidence for each subset. For the plots
see below.
A value close 1 indicates that the top 3 recommendations for each user do not
vary much and vice versa.

### Figures
[{Action, Adventure}](https://github.com/NahsiN/MovieReco/blob/movielens_statistics/avg_ioc_Action_Adventure_100.pdf)

[{Action, Adventure, Comedy}](https://github.com/NahsiN/MovieReco/blob/movielens_statistics/avg_ioc_Action_Adventure_Comedy_100.pdf)

[{Action, Adventure, Comedy, Drama}](https://github.com/NahsiN/MovieReco/blob/movielens_statistics/avg_ioc_Action_Adventure_Comedy_Drama_100.pdf)

[{Action, Adventure, Comedy, Drama, Romance}](https://github.com/NahsiN/MovieReco/blob/movielens_statistics/avg_ioc_Action_Adventure_Comedy_Drama_Romance_100.pdf)

[{Action, Adventure, Comedy, Drama, Romance, Thriller}](https://github.com/NahsiN/MovieReco/blob/movielens_statistics/avg_ioc_Action_Adventure_Comedy_Drama_Horror_Romance_Thriller_100.pdf)
