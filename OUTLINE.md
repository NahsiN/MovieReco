### Outline of workflow
1. [ ] Read in Kodi SQL database
  - [x] parse Movie name, set of genres G_M, Year, Rating from sqlite db into
    a pandas dataframe object
  - [ ] watch status
  - [x] get rid of three different sci fi genres

2. [x] Compute r_ij, genre correlation matrix based on Choi2012 (First implementation)
3. [x] Compute recommendation points and display them
