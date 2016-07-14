SELECT 
	idMovie, c00 as 'MovieName',  c05 as 'Rating', c07 as 'Year',  c14 as 'Genre'
FROM 
	movie 
WHERE
	Genre = ''
LIMIT 
	10000;