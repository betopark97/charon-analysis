-- Review the Final Table made from Data Wrangling with Pandas
SELECT * FROM charon_data;

-- Create a View to make all necessary queries for Data Analysis
-- Purpose: make column order comfortable, and change necessary data types

-- DROP Existing View
DROP VIEW IF EXISTS charon_data_analysis;

-- Create a View
CREATE VIEW charon_data_analysis AS
SELECT
	name
	,channel_name
	,created_at::date
	,country::CHAR(2)
	,channel_view_count
	,subscriber_count
	,video_count
	,title
	,published_at::timestamp
	,published_day
	,category_name
	,duration
	,duration_seconds::bigint
	,video_view_count
	,like_count
	,comment_count
	,default_audio_language
	,tags
	,description
FROM charon_data;

/* In the Data Analysis process the preprocessed data will be used to make insights 
to what the data is trying to say. This will involve answering questions through 
descriptive statistics and inferential statistics.

This involves specifying dependent and independent variables.
According to Youtube's Monetary Policy, there are various ways to generate money, 
but the main and constant way is through views because other ways such as putting 
advertisements in between videos is also dependent on views. 
That is why all types of metrics will be based on views as the independent variable.

`Descriptive Stats`
- 1. Who in Charon has the biggest channel in terms of subscription? in terms of total views?
- 2. Which are the most watched and least watched videos for each creator?
- 3. Does covering a wider range of category improve total views of the channel?
- 4. Does the upload period of the year, month, day, time matter?
- 5. What category is the most trending?
- *. How does advertisement videos compare to non-advertisement videos on views performance?
- *. Is there a drop or increase in views to consecutive videos after advertisement?
- 6. Is the length of the video related to views? Does it have a different effect in different categories?
- *. Is there a relationship between how frequent the uploads are? or how consistent the upload times are?
- 7. Does the visuals of the creator being face, no-face, or virtual matter?
- *. Does having an intro or outro matter?
- *. Does having subtitles or no-subtitles matter? (subtitles of same language)
- 8. Does the length of the title show a difference in views performance?
- *. Does likes and comments have a relationship with views?
- *. How big of an impact is there on amount of subscribers and views?
*/

SELECT * FROM charon_data_analysis;

-- 1.1 Order Creators from Most to Least Subscribers
SELECT
	name
	,MAX(subscriber_count) AS subscriber_count
FROM charon_data_analysis
GROUP BY name
ORDER BY subscriber_count DESC;

-- 1.2 Order Creaters from Most to Least Views
SELECT
	name
	,MAX(subscriber_count) AS subscriber_count
	,MAX(channel_view_count) AS total_views
	,ROUND(AVG(video_view_count),2) AS avg_views_per_video
FROM charon_data_analysis
GROUP BY name
ORDER BY avg_views_per_video DESC;

-- 2.1 Which are the most watched videos for each creator?
WITH ranked_views AS (
SELECT
	name
	,title
	,video_view_count AS views
	,RANK() OVER(PARTITION BY name ORDER BY video_view_count DESC) AS rank_top
FROM charon_data_analysis
WHERE video_view_count <> 0
)
SELECT 
	name
	,views
	,title
FROM ranked_views
WHERE rank_top <= 5
ORDER BY name, views DESC;

-- 2.2 Which are the least watched videos for each creator?
WITH ranked_views AS (
SELECT
	name
	,title
	,video_view_count AS views
	,RANK() OVER(PARTITION BY name ORDER BY video_view_count) AS rank_bot
FROM charon_data_analysis
WHERE video_view_count <> 0
)
SELECT 
	name
	,views
	,title
FROM ranked_views
WHERE rank_bot <= 5
ORDER BY name, views;

-- 3. Does covering a wider range of category improve total views of the channel?
WITH category_count_per_channel AS (
SELECT
	name
	,category_name
	,COUNT(*) 
FROM charon_data_analysis
GROUP BY name, category_name
), avg_view_per_channel AS (
SELECT
	name
	,ROUND(AVG(video_view_count),2) AS avg_view_count
FROM charon_data_analysis
GROUP BY name
)
SELECT 
	a.name
	,COUNT(category_name) AS category_count
	,MAX(avg_view_count) AS avg_view_count
FROM category_count_per_channel a
JOIN avg_view_per_channel b
	ON a.name = b.name
GROUP BY a.name
ORDER BY category_count DESC;

-- 4.1 Does the upload day matter?
-- Order of most viewed by day of the week for each Creator
SELECT
	name
	,published_day
	,ROUND(AVG(video_view_count),2) AS avg_view_count
FROM charon_data_analysis
GROUP BY name, published_day
ORDER BY name, avg_view_count DESC;
-- Order of most viewed by day of the week overall
SELECT
	published_day
	,ROUND(AVG(video_view_count),2) AS avg_view_count
FROM charon_data_analysis
GROUP BY published_day
ORDER BY avg_view_count DESC;

-- *** 4.2 Does the upload time matter?
WITH time_separation AS (
SELECT
	name
	,published_at::time AS published_at
	,CASE
        WHEN published_at::time BETWEEN '00:00:00' AND '01:59:59' THEN 1
        WHEN published_at::time BETWEEN '02:00:00' AND '03:59:59' THEN 2
        WHEN published_at::time BETWEEN '04:00:00' AND '05:59:59' THEN 3
        WHEN published_at::time BETWEEN '06:00:00' AND '07:59:59' THEN 4
        WHEN published_at::time BETWEEN '08:00:00' AND '09:59:59' THEN 5
        WHEN published_at::time BETWEEN '10:00:00' AND '11:59:59' THEN 6
        WHEN published_at::time BETWEEN '12:00:00' AND '13:59:59' THEN 7
        WHEN published_at::time BETWEEN '14:00:00' AND '15:59:59' THEN 8
        WHEN published_at::time BETWEEN '16:00:00' AND '17:59:59' THEN 9
        WHEN published_at::time BETWEEN '18:00:00' AND '19:59:59' THEN 10
        WHEN published_at::time BETWEEN '20:00:00' AND '21:59:59' THEN 11
        WHEN published_at::time BETWEEN '22:00:00' AND '23:59:59' THEN 12
    END AS time_cat
	,video_view_count
FROM charon_data_analysis
)
SELECT
	time_cat
	,ROUND(AVG(video_view_count),2) AS avg_view_count
FROM time_separation
GROUP BY time_cat
ORDER BY avg_view_count DESC;

-- *** 5. What category is the most trending?
WITH count_per_category AS (
SELECT
	category_name
	,COUNT(*) AS category_count
FROM charon_data_analysis
GROUP BY category_name
),
views_per_category AS (
SELECT
	category_name
	,ROUND(AVG(video_view_count),2) AS avg_view_count
FROM charon_data_analysis a
GROUP BY category_name
ORDER BY avg_view_count DESC
)
SELECT
	a.category_name
	,category_count
	,avg_view_count
FROM count_per_category a
JOIN views_per_category b
	ON a.category_name = b.category_name
ORDER BY avg_view_count DESC;

-- *** 6.1 Is the length of the video related to views? Shorts vs. Videos
SELECT 
	CASE
		WHEN duration_seconds <= 60 THEN 'shorts'
		WHEN duration_seconds > 60 THEN 'video'
	END AS content_type
	,ROUND(AVG(video_view_count),2) AS avg_view_count
FROM charon_data_analysis
GROUP BY content_type
ORDER BY avg_view_count;

-- *** 6.2 Does it have a different effect in different categories?
SELECT 
	CASE
		WHEN duration_seconds <= 60 THEN 'shorts'
		WHEN duration_seconds > 60 THEN 'video'
	END AS content_type
	,category_name
	,ROUND(AVG(video_view_count),2) AS avg_view_count
FROM charon_data_analysis
GROUP BY content_type, category_name
ORDER BY content_type, avg_view_count DESC;

-- *** 6.3 From only normal videos (not shorts), which types of video lengths have the most views?
WITH video_length_category AS (
SELECT
        category_name,
        CASE
            WHEN duration_seconds BETWEEN 60 AND 60*5 THEN 'short'
            WHEN duration_seconds BETWEEN 60*5+1 AND 60*20 THEN 'medium'
            WHEN duration_seconds > 60*20 THEN 'long'
        END AS video_length,
        video_view_count
    FROM charon_data_analysis
    WHERE duration_seconds > 60
)
SELECT
    video_length,
    ROUND(AVG(video_view_count), 2) AS avg_view_count
FROM video_length_category
GROUP BY video_length
ORDER BY avg_view_count DESC;

-- *** 6.4 From only normal videos (not shorts), which types of video lengths have the most views by category?
WITH video_length_category AS (
SELECT
        category_name
        ,CASE
            WHEN duration_seconds BETWEEN 60 AND 60*5 THEN 'short'
            WHEN duration_seconds BETWEEN 60*5+1 AND 60*20 THEN 'medium'
            WHEN duration_seconds > 60*20 THEN 'long'
        END AS video_length,
        video_view_count
    FROM charon_data_analysis
    WHERE duration_seconds > 60
)
SELECT
    category_name,
    video_length,
    ROUND(AVG(video_view_count), 2) AS avg_view_count
FROM video_length_category
GROUP BY category_name, video_length
ORDER BY video_length DESC, avg_view_count DESC;

-- *** 7. Does the visuals of the creator being face, no-face, or virtual matter?
WITH creator_category AS (
SELECT
	name
	,CASE
		WHEN name IN ('피닉스박', '죠니월드', '또시', '이재석', '모아요', '류제홍', '코뚱잉', '인섹', '김용녀', '돌카사', '학살', '막눈', '강인경', '한동숙', '꼴랑이', '윤가놈', '스틸로', '명훈', '랄로', '괴물쥐', '소행성612', '핑크자크', '버니버니', '신해조', '이석현') THEN 'face'
		WHEN name IN ('삐야기', '스나랑', '후즈') THEN 'virtual'
		WHEN name IN ('냄새', '링규링규링', '지명', '2수연', '전쓰트', '정동글', '프로젝트롤', '헤이스트', '른쿄', '블루위키', '아빠킹', '김데데', '도개', 'THIRD', '미남홀란드', '종원TV', '꼬예유', 'ATK', '추털이', '순규박', '모양몬', '이클리피아', '멀럭킹', '송사리', '제갈병춘', 'PAKA', '지보배', '핑맨', '흐쟁이', '미야', '고수달') THEN 'no-face'
	END AS creator_type
	,subscriber_count
	,channel_view_count
	,video_view_count
	,video_count
FROM charon_data_analysis
)
SELECT
	creator_type
	,ROUND(AVG(video_view_count),2) AS avg_view_count
	,ROUND(AVG(subscriber_count),2) AS avg_subscriber_count
FROM creator_category
GROUP BY creator_type;

-- *** 8. Does the length of the title show a difference in views performance?
WITH title_length_category AS (
SELECT
	CASE
		WHEN LENGTH(title) BETWEEN 0 AND 4 THEN 'short'
		WHEN LENGTH(title) BETWEEN 5 AND 20 THEN 'medium'
		WHEN LENGTH(title) BETWEEN 21 AND 35 THEN 'long'
		WHEN LENGTH(title) >= 36 THEN 'very long'
	END AS title_length
	,video_view_count AS view_count
FROM charon_data_analysis
)
SELECT
	title_length
	,ROUND(AVG(view_count),2) AS avg_view_count
FROM title_length_category
GROUP BY title_length
ORDER BY avg_view_count DESC;