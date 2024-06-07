# Charon Creative Youtube Data Analysis

## Introduction
Youtube among many other platforms for content creators, has a very complex recommender system that uses countless amount of features on its algorithms. This project is done to find insights on some of the features that are available to the public and try to find which features show a significant impact in the growth of a Youtube channel. As many may already know, there are countless creators and many of them share different motivations for which most are not consistent or not active. That is why I chose to gather data from the Youtubers I watch on a regular basis at first, when shortly after I realized that most of them are part of a company called 'Charon Creative'. This is a South Korean company for online content creators covering platforms like Instagram, TikTok, and more, but mostly Youtube. It is hard to try and make inferences for Youtube Content all around the world because various reasons like different time zones, languages, demographics, etc. So I will try and make Data Analysis on Youtube Data targeted to the South Korean audience.

## Objectives
The objectives of this project as mentioned in the introduction is to find some kind of correlation or relationship between publicly available data and views from an automated process. I chose the average (mean) views per video to be the independent variable because after all that is the default for a Youtube Content Creator to generate money from the platform. There are many other factors such as having subscribers but that just acts as a threshold for the Youtuber to be able to do more things to interact with the platform such as, for example, having a certain amount of subscribers to generate money (different amounts for different regions) by 1,000 views or to add commercial ads to their videos, etc. Various features that will be taken into account for the views will be factors such as time, title length, video genre (category), facial appearance, length of video, etc.  
Questions to answer will be the following:
1. Who in Charon has the biggest channel in terms of subscription? in terms of total views?
2. Which are the most watched and least watched videos for each creator?
3. Does covering a wider range of category improve total views of the channel?
4. Does the upload period of the year, month, day, time matter?
5. What category is the most trending?
6. Is the length of the video related to views? Does it have a different effect in different categories?
7. Does the visuals of the creator being face, no-face, or virtual matter?
8. Does the length of the title show a difference in views performance? 

## Steps of the project
As mentioned in the Objectives section, this project will be an automated process to be able to gather data. For that this project uses Python, Jupyer Notebook, PostgreSQL, and csv/excel/google spreadsheets. 
The steps are as follows:  

1. Gather necessary Youtube Data for every Charon Creator for Data Analysis (Python)
    - Request website html from [Charon Creative](https://charoncreative.com/creator)
    - Use Beautiful Soup to parse the html and find the Youtuber's name and youtube link. By reading the Youtube Documentation in the Youtube link there is a '@' followed by an id and that is called a handler. Use regex (regular expression) to parse the hander and use the Youtube Data v3 API to get the channel id of that Youtuber and save it into a csv called [creator_channel.csv](./data/creator_channel.csv). 
    - Use the channel id column from creator_channel.csv to get data for individual channels such as channel id, channel, name, created date, country, total views, video count, subscriber count and most importantly the playlist id because this id is used to get information of the videos. Then save this in a csv called [channel_stats.csv](./data/channel_stats.csv).
    - Use the playlist id column from channel_stats.csv to get data of all the video ids from each playlist id that will be used for retrieving the video data, so this is like a junction table in SQL to connect channel_id and its video data. Then save this in a csv called [playlist_video.csv](./data/playlist_video.csv).
    - Use the playlist_video.csv to retrieve the data for all the videos such as the video id, published date, title, description, thumbnails, tags, category id, default audio language, duration, view count, like count, and comment count. Then save this in a csv called [video_stats.csv](./data/video_stats.csv).
    - Finally, the names of the video categories (genres) will be collected too because it will be used for data analysis. It seems that from the previous csv, only the codes for each category can be retrieved and so a separate API call will be done to get all codes alongside the names. Then this will be saved in a csv called [category_id_name.csv](./data/category_id_name.csv).
2. Connect data to PostgreSQL. (PostgreSQL)
    - All of the csv files retrieved in Step 1 will be imported in a SQL database. The choice of database in this project was PostgreSQL and there seems to be an error when importing through the latest pgAdmin4 so a python script was used with psycopg2 and SQLAlchemy. This can be found under the commented line of `# Step 12: Connect all Data to PostgreSQL database` in the [main.py](./main.py).
3. Join necessary tables for Data Analysis. (SQL)
    - All the tables that were introduced to the database is joined to make one table so that the SQL queries that are being done will look cleaner when making descriptive statistical analysis. This is done as the query in the [data_prep.sql](./data_prep.sql).
4. Perform Exploratory Data Analysis for insights. (Jupyter Notebook)
    - EDA will be performed on the data from the above joined table such as looking at the comformity of the data, null values, and more to be cleaned and wrangled.
    - EDA was performed in the Exploratory Data Analysis section in the [eda.ipynb](./eda.ipynb).
    - The changes that will be done to the data are as follows in the Data Wrangling section.
5. Data Wrangling. (Jupter Notebook)
    - Change create_at, published_at from ISO 8601 UTC(Coordinated Universal Time) to KST(Korean Standard).
    - Add a feature to show what day of the week the video was uploaded, this feature will be the column published_day.
    - Add a feature to show the ISO 8601 duration in total amount of seconds. The Youtube Data API returns the duration of videos in a format like 12M21S and to make calculations it is converted into seconds as 12 minutes * 60 + 21 seconds = 741.
    - Remove P and T strings from the ISO 8601 duration for better readability in which P stands for Period and T stands for Time (Period is for year, month, week, day, whereas Time is for hour, minute, second, etc.)
    - Change the null values in like_count and comment_count to 0 and into int64/bigint.
    - It seems that some creators from Charon are not active in Youtube anymore, maybe because they are targetting other SNS platforms, so they will be excluded from the analysis, to be more specific, include only creators who have been active in the last 6 months (due to policy regarding payments, where if your channel is inactive for longer than 6 months, you are not sponsored anymore).
    - Apply all the changes above and make a final DataFrame to save as a csv called [charon_data.csv](./data/charon_data.csv) and import in PostgreSQL just as in Step 2: Connect data to PostgreSQL.
    - For more details check the Data Wrangling section in [eda.ipynb](./eda.ipynb)
6. Make necessary queries for visuals (plots, charts, etc.). (SQL)
    - In the Data Analysis process the preprocessed data will be used to make insights to what the data is trying to say. This will involve answering questions through descriptive statistics and inferential statistics.
    - This involves specifying dependent and independent variables. According to Youtube's Monetary Policy, there are various ways to generate money but the main way and constant is through views because other ways such as putting advertisements in between videos is also dependent on views. That is why all types of metrics will be based on views as the independent variable.
    - The following questions are from brainstorming for different types of statistics that I thought would be good to try and observe, from which I tried to make SQL queries, if possible, to find some patterns detectable to the human eye. For more details refer to [data_analysis.sql](./data_analysis.sql)
    - `Queries that will be used for Descriptive Statistics`
        - Who in Charon has the biggest channel in terms of subscription? in terms of total views?
        - Which are the most watched and least watched videos for each creator?
        - Does covering a wider range of category improve total views of the channel?
        - Does the upload period of the year, month, day, time matter?
        - What category is the most trending?
        - Is the length of the video related to views? Does it have a different effect in different categories?
        - Does the visuals of the creator being face, no-face, or virtual matter?
        - Does the length of the title show a difference in views performance? 
    - `Queries that will be used for Inferential Statistics (Hypothesis Testing)`
        - Does the upload time matter? (4.2)
        - What category is the most trending? (5)
        - Is the length of the video related to views? Shorts vs. Videos (6.1)
        - Does it have a different effect in different categories? (6.2)
        - From only normal videos (not shorts), which types of video   lengths have the most views? (6.3)
        - From only normal videos (not shorts), which types of video lengths have the most views by category? (6.4)  
        - Does the visuals of the creator being face, no-face, or virtual matter?  
        - Does the length of the title show a difference in views performance? 
7. Perform Hypothesis Testing for findings from queries. (Jupyter Notebook)
    - In this sections the queries that somewhat seem like it has a strong correlation only by eye will be analyzed with hypothesis testing to see if it is statistically significant.
    - From performing queries there were various insights that showed a noticeable difference in numbers for various features and so these queries were used to perform T-Tests, ANOVA, and Post-Hoc Tests.
    - The findings that has shown to be statistically significant among the queries that were performed for Inferential Statistics in the above step were:
        - Uploading videos between time range 22:00 ~ 23:59:59 KST has shown to have significantly more views than any other time ranges. This could be because most Korean people either go to work or to an academy until late and return home to have dinner, shower, and then watch Youtube before going to sleep around that time.
        - Shorts (videos that are less than 1 minute long) has shown to have significantly more views than normal videos ranging from 1 minute or more. This could be because most shorts are watched without choice, which means that videos are content that the audience filters by themselves but shorts are mostly watched by sliding the screen upwards so even if the audience wants to or not they are given the benefit of the doubt. 
        - From normal videos videos ranging from 5 to 20 minutes have shown to have significantly more views than videos shorter than 5 minutes or longer than 20 minutes. This could be because people would like something that keeps them engaged for a certain amount of time but want to watch various videos before going to sleep.
        - The Youtuber's face appearing on the videos or not also has shown to have a statistically significant difference in the amount of views and subscribers. Virtual Youtubers, have significantly more average video views than Youtubers that show their faces, and Youtubers who show their real faces have significantly more average video views than Youtubers that don't show their faces. This might be because through watching the facial emotions of the Youtubers the audience feels more psychological connection with the Youtuber and makes it more engaging to watch the videos and virtuals ranking on top because such thing is a trend in South Korea at the moment.
        - Lastly, the title lengths also show to have a statistically significant difference between groups. The shortest title lengths were categorized from 0 to 4 syllables because South Korea uses the Chinese four character phrases called 사자성어. The rest of the categories were grouped by clustering different title lengths and the analysis shows that all groups showed statistical significance between each other going from shortest having the most amount of views to longest titles having the least amount of views in order. This might be because shorter titles have more impact and when titles get to long it gets complex and audiences what to know what the video will be about before clicking.
        - All queries related to category showed no meaningful patterns, probably because most of the Youtubers from Charon target the Gaming category.
8. Create Visuals and Dashboard in Tableau. (Tableau)
    - All of the Visuals were created from the queries from Steps 6 and 7 queries' [csv files](./data/tableau/)
    - The Tableau Public Viz is in the following [link](https://public.tableau.com/app/profile/roberto.parkr/viz/CharonCreativeAnalysis/OverallStats)
    - The Dashboard was created with the queries from Steps 6 and 7.
    - There are 4 dashboards that were created, which can be observed by clicking the tabs at the top. The 4 dashboards include `Overall Statistics` for Charon Creators, `Statistics by Creator` in which you can interact to look at different statistics for each individual creator, `Category Trends` to look at different statistics for different categories, although most of the creators create content for the Gaming category, and lastly `Inferential Statistics` to look at all the queries that showed statistical significance. 
9. (Optional) Use the [gspread API](./g_spread.py) to export of all these values to a google spreadsheet if working in a team. To use this API refer to its document with this [link](https://docs.gspread.org/en/latest/index.html).

## Limitations and Discussion
In this section the limitations of the project and improvements that could be made for the project will be discussed.  

`Limitations`
1. It was not a self-made API so there was a limit to how many API calls you can make through the Youtube Data v3 API. Although the API call limit was enough as the amount of creators in Charon at the moment are not that many to worry about this, it is certainly a limitation when beginning the project without optimized code (for whoever tries to do a similar project).
2. The amount of accessible analytical data is also limited to publicly available data as features such as views, region, category, published time, etc. This would be much of a less problem if maybe I was a data analyst at the company Charon Creative itself, so that I can use the Youtube Analytics API to access more information like the retention, or distribution of mostly rewatched parts of the videos.
3. Another limitation is that I am not part of the company and so I can't interact with their content and it would be much better if I can actually perform more complex analysis with more data features for machine learning or perform A/B Testing with different types of video editing or thumbnails for the videos.

`Improvements`
1. For the future, optimizing the code to make classes to manage the data would improvement the time efficiency. It would look something like [yt_manager.py](./yt_manager.py)
2. Apply data wrangling for different csv because I joined all the csv first and then performed data wrangling, there is only one table from which we make SQL queries for data analysis, which would make the process very inefficient and slow if the dataset was way larger.
3. Apply machine learning clustering techniques for making different categories for the queries involing time like what time the videos were uploaded, categorizing video length, and title length, because these were done with heuristics.
4. Perform Computer Vision techniques to analyze if there are certain thumbnails that attract more viewers than other thumbnails. It may be complicated but would be a good analysis to see if there is a certain pattern, for example, in a lot of Charon Creative videos' thumbnails you can see that the Youtuber's face is photoshopped into other photos.

## Sources
### Get Charon
https://charoncreative.com/creator
### Get Youtube Data API v3
https://console.cloud.google.com  
https://developers.google.com/youtube/v3  
https://support.google.com/youtube/answer/72857?hl=en  
### Get gspread
https://docs.gspread.org/en/latest/index.html
### Get PostgreSQL
https://www.postgresql.org
### Get Tableau Public
https://public.tableau.com/app/profile/roberto.parkr/vizzes