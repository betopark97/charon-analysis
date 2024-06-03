import os
from dotenv import load_dotenv
import googleapiclient.discovery
import pandas as pd 

class YoutubeManager:
    
    def __init__(self, id) -> None:
        
        # Credentials to make API call to Youtube Data API v3
        load_dotenv()
        self.youtube_api_key = os.environ.get('YOUTUBE_API_KEY3')
        self.api_service_name = 'youtube'
        self.api_version = 'v3'
        self.youtube = googleapiclient.discovery.build(
            self.api_service_name, 
            self.api_version, 
            developerKey=self.youtube_api_key)
        
        # Labels for Youtube Channel
        self.channel_id = id
        

    def get_channel_stats(self) -> dict:
        # Create a request for the channel statistics of the given channel ID
        request = self.youtube.channels().list(
            part='snippet,contentDetails,statistics',
            id=self.channel_id
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
