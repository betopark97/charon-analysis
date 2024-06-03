-- Query all data by making appropriate joins to check Data Types and Clean Data
SELECT
	a.name
	,b.channel_name
	,b.created_at
	,b.country
	,b.view_count AS channel_view_count
	,b.subscriber_count
	,b.video_count
	,d.published_at
	,d.title
	,d.description
	,d.thumbnails
	,d.tags
	,d.category_id
	,e.category_name
	,d.default_audio_language
	,d.duration
	,d.view_count AS video_view_count
	,d.like_count
	,d.comment_count
FROM creator_channel a
FULL OUTER JOIN channel_stats b
	ON a.channel_id = b.channel_id
FULL OUTER JOIN playlist_video c
	ON b.playlist_id = c.playlist_id
FULL OUTER JOIN video_stats d
	ON c.video_id = d.video_id
INNER JOIN category_id_name e
	ON d.category_id = e.category_id
;

-- Changes needed are:
-- 1. Change created_at, published_at from text to KST (timestamp with timezone)
-- 2. Change duration to hour:minute:seconds and also to seconds
-- 3. Change like_count and comment_count to bigint
-- 4. It seems that some creators from Charon are not active in youtube anymore
--    maybe because they are targetting other SNS platforms so exclude those from analysis
-- 5. Create a View with the above changes
