import re
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import pandas as pd
import googleapiclient.discovery
import googleapiclient.errors
import json
import psycopg2
from sqlalchemy import create_engine
load_dotenv()

def main(update:bool=False):
    
# Step 1: Webscrape Charon
    if update:
        # Request website html
        charon_url = 'https://charoncreative.com/creator'
        response = requests.get(url=charon_url)
        if response.status_code == 200:
            print("request successful")
            with open('web_scrape.html', 'w') as file:
                file.write(response.text)
        else:
            response.raise_for_status()
    
# Step 2: Parse HTML with Beautiful Soup
        # Open html
        with open('./data/web_scrape.html') as file:
            data = file.read()
            
        # Beautiful Soup instance
        soup = BeautifulSoup(data, 'lxml')
        
        # Get creator names
        creators = soup.select('.mobile_section .txt._txt_wrap')
        creators = [creator.get_text(strip=True) for creator in creators]
        # print(f"크리에이터 리스트: {creators}")
        print(f"크리에이터 개수: {len(creators)}")
        
        # Get creator youtube links
        youtube_links = soup.select('.pc_section .inline-blocked a')
        youtube_links = [link['href'] for link in youtube_links if link['href'].startswith('https://www.youtube.com/')]
        # print(f"크리에이터 링크: {youtube_links}")
        print(f"링크 개수: {len(youtube_links)}")

# Step 3: Parse handlers with Regex and get channel_id with Youtube's API
        # Create list for creator dictionaries
        charon_dict = []
        for name, link in zip(creators, youtube_links):
            handler = get_handler(link)
            channel_id = get_channel_id(handler)
            if channel_id is None:
                channel_id = handler
            entry = {
                'name':name, 
                'link':link, 
                'handler':handler, 
                'channel_id':channel_id}
            charon_dict.append(entry)

# Step 4: Export Data to CSV with creator's name, link, handler, channel_id     
        # Make pandas dataframe and export csv
        df = pd.DataFrame(charon_dict)
        df.to_csv('./data/creator_channel.csv',index=False)

# Step 5: Get channel info with Youtube's API through channel ids
        # Read csv in Step 4 and extract channel ids
        channel_ids = pd.read_csv('./data/creator_channel.csv')['channel_id']
        # Number of elements in each sublist
        chunk_size = 50
        # Initialize a list to store the sublists
        chunks = []
        # Iterate over the values in chunks
        for i in range(0, len(channel_ids), chunk_size):
            chunk = channel_ids[i:i + chunk_size].to_list()
            chunks.append(chunk)
        # Empty list for df concat of chunks
        dataframes = []
        for chunk in chunks:
            channel_ids = ','.join(chunk)
            channel_stats = get_channel_stats(channel_ids)
            dataframes.append(channel_stats)
        combined_df = pd.concat(dataframes, ignore_index=True)
        
# Step 6: Export Data to CSV with creator's channel_id, channel_name, created_at, country, playlist_id, view_count, subscriber_count, video_count
        combined_df.to_csv('./data/channel_stats.csv',index=False)

# Step 7: Get all the video ids from the playlist id from Step 6
        playlist_videos_dict = []
        playlist_ids = pd.read_csv('./data/channel_stats.csv')['playlist_id'].to_list()
        for playlist_id in playlist_ids:
            try:
                video_ids = get_video_ids(playlist_id)
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
                pass
            else:
                for video_id in video_ids:
                    entry = {
                        'playlist_id':playlist_id,
                        'video_id':video_id
                    }
                    playlist_videos_dict.append(entry)
        df = pd.DataFrame(playlist_videos_dict)
# Step 8: Export Data to CSV with creator's playlist_id and video_id
        df.to_csv('./data/playlist_video.csv', index=False)

# Step 9: Extract video stats using the video ids
        # Read csv in Step 8 and extract video ids
        video_ids = pd.read_csv('./data/playlist_video.csv')['video_id']
        # # Number of elements in each sublist
        chunk_size = 50
        # # Initialize a list to store the sublists
        chunks = []
        # # Iterate over the values in chunks
        for i in range(0, len(video_ids), chunk_size):
            chunk = video_ids[i:i + chunk_size].to_list()
            chunks.append(chunk)
        # Empty list for df concat of chunks
        dataframes = []
        for chunk in chunks:
            video_ids = ','.join(chunk)
            video_stats = get_video_stats(video_ids)
            print(video_stats)
            dataframes.append(video_stats)
        combined_df = pd.concat(dataframes, ignore_index=True)
        combined_df = combined_df.replace({'\n': ' ', '\r': ' '}, regex=True)
# Step 10: Export Data to CSV with creator's video_id and its stats (too many to write)
        combined_df.to_csv('./data/video_stats.csv', index=False)

# Step 11: Extract video category names from video category ids

        df_video_categories = get_video_category_names(region_code='kr')
        df_video_categories.to_csv('./data/category_id_name.csv', index=False)
    
# Step 12: Connect all Data to PostgreSQL database

        # Database connection parameters
        db_params = {
            "host":"127.0.0.1",
            "database":"charon-analysis",
            "user":"postgres",
            "password":os.environ.get('PASSWORD'),
            "port":"5432"
        }

        # Create a connection to the PostgreSQL server
        conn = psycopg2.connect(
            host=db_params['host'],
            database=db_params['database'],
            user=db_params['user'],
            password=db_params['password']
        )

        # Create SQLAlchemy Engine with necessary URI
        engine = create_engine(f'postgresql://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}/{db_params["database"]}')

        # Define the file paths for your CSV files
        csv_files = {
            'creator_channel': './data/creator_channel.csv',
            'channel_stats': './data/channel_stats.csv',
            'playlist_video':'./data/playlist_video.csv',
            'video_stats':'./data/video_stats.csv',
            'category_id_name':'./data/category_id_name.csv'
        }

        # Load and display the contents of each CSV file to check
        for table_name, file_path in csv_files.items():
            print(f"Contents of '{table_name}' CSV file:")
            df = pd.read_csv(file_path)
            print(df.head(2))  # Display the first few rows of the DataFrame
            print("\n")
            
        # Loop through the CSV files and import them into PostgreSQL
        for table_name, file_path in csv_files.items():
            df = pd.read_csv(file_path)
            df.to_sql(table_name, engine, if_exists='replace', index=False)
    
    
    
def get_handler(url: str) -> str:
    # Get handlers from the youtube links
    pattern = r'/(@[\w-]+)|/channel/([^/?]+)|/c/([\w-]+)'
    match = re.search(pattern, url)
    if match:
        # Extract the matched group
        handle, channel_id, custom_url = match.groups()
        # Choose the non-empty group
        extracted = handle or channel_id or custom_url
        return extracted
    print("No match found for URL:", url)
    
def get_channel_id(handler: str) -> str:
    load_dotenv()
    youtube_api_key = os.environ.get('YOUTUBE_API_KEY1')
    api_service_name = 'youtube'
    api_version = 'v3'
    youtube = googleapiclient.discovery.build(
        api_service_name,
        api_version,
        developerKey=youtube_api_key
    )
    # Create a search request for the given handle
    search_request = youtube.search().list(
        part='snippet',
        q=handler,
        type='channel'
    )
    # Execute the search request and get the response
    search_response = search_request.execute()
    # Iterate over the items in the search response
    for item in search_response['items']:
        # Check if the 'channelId' key is present in the 'snippet' dictionary
        if 'channelId' in item['snippet']:
            # Return the channel ID if found
            return item['snippet']['channelId']
    # Return None if no channel ID is found
    return None
    
def get_channel_stats(channel_id: str) -> pd.DataFrame:
    load_dotenv()
    youtube_api_key = os.environ.get('YOUTUBE_API_KEY1')
    api_service_name = 'youtube'
    api_version = 'v3'
    youtube = googleapiclient.discovery.build(
        api_service_name,
        api_version,
        developerKey=youtube_api_key
    )
    # Create a request for the channel statistics of the given channel ID
    request = youtube.channels().list(
        part='snippet,contentDetails,statistics',
        id=channel_id
    )
    # Execute the request and get the response
    response = request.execute()
    
    # Loop through the necessary items and make a Dataframe
    df_data = []
    for item in response['items']:
        data = {
            'channel_id':item.get('id'),
            'channel_name': item['snippet'].get('title'),
            'created_at':item['snippet'].get('publishedAt'),
            'country':item['snippet'].get('country'),
            'playlist_id':item['contentDetails']['relatedPlaylists'].get('uploads'),
            'view_count':item['statistics'].get('viewCount'),
            'subscriber_count':item['statistics'].get('subscriberCount'),
            'video_count':item['statistics'].get('videoCount'),
        }
        df_data.append(data)
    df = pd.DataFrame(df_data)
    
    # Return the Pandas Dataframe
    return df
    
def get_video_ids(playlist_id: str) -> list:
    load_dotenv()
    youtube_api_key = os.environ.get('YOUTUBE_API_KEY1')
    api_service_name = 'youtube'
    api_version = 'v3'
    youtube = googleapiclient.discovery.build(
        api_service_name,
        api_version,
        developerKey=youtube_api_key
    )
    video_ids = []
    next_page_token = None
    
    while True:
        request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids

def get_video_stats(video_id: str) -> pd.DataFrame:
    load_dotenv()
    youtube_api_key = os.environ.get('YOUTUBE_API_KEY1')
    api_service_name = 'youtube'
    api_version = 'v3'
    youtube = googleapiclient.discovery.build(
        api_service_name,
        api_version,
        developerKey=youtube_api_key
    )
    request = youtube.videos().list(
        part='snippet,contentDetails,statistics',
        id=video_id
    )
    response = request.execute()
    df_data = []
    for item in response['items']:
        data = {
            'video_id':item.get('id'),
            'published_at':item['snippet'].get('publishedAt'),
            'title':item['snippet'].get('title'),
            'description':item['snippet'].get('description'),
            'thumbnails':item['snippet']['thumbnails']['default'].get('url'),
            'tags':item['snippet'].get('tags'),
            'category_id':item['snippet'].get('categoryId'),
            'default_audio_language':item['snippet'].get('defaultAudioLanguage'),
            'duration':item['contentDetails'].get('duration'),
            'view_count':item['statistics'].get('viewCount'),
            'like_count':item['statistics'].get('likeCount'),
            'comment_count':item['statistics'].get('commentCount'),
        }
        df_data.append(data)
    df = pd.DataFrame(df_data)
    
    return df

def get_video_category_names(region_code: str) -> pd.DataFrame:
    load_dotenv()
    youtube_api_key = os.environ.get('YOUTUBE_API_KEY1')
    api_service_name = 'youtube'
    api_version = 'v3'
    youtube = googleapiclient.discovery.build(
        api_service_name,
        api_version,
        developerKey=youtube_api_key
    )
    request = youtube.videoCategories().list(
        part='snippet',
        regionCode=region_code
    )
    response = request.execute()
    df_data = []
    for item in response['items']:
        data = {
            'category_id':item.get('id'),
            'category_name':item['snippet'].get('title')
        }
        df_data.append(data)
    df = pd.DataFrame(df_data)
    
    return df

if __name__ == '__main__':
    main(update=False)