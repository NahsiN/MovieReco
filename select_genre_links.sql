SELECT 
	genre_id,  media_id as "idMovie"
FROM
	genre_link
WHERE
	media_type = 'movie'
LIMIT
	50
