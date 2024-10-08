import os
import requests
import json
import praw
from datetime import datetime
from appwrite.client import Client
from appwrite.services.database import Database

# Initialize the Appwrite client
client = Client()
client.set_endpoint(os.environ.get('https://api.panoapps.com/v1'))  # Your Appwrite endpoint
client.set_project(os.environ.get('66d8b20b000c13f95e6f'))  # Your Appwrite project ID
client.set_key(os.environ.get('ceedb7bc0ef5926898d8c4560cd1ef5942842e9919f5a34d0a1ee43ee0c7906430511d8ca7884293c169c4324d8d3534938bc3d2ddd703ef63589509913dc675f9b39b377ba694ddfac49dc2a7cc1455899023bbd3383165f7de987a0e853637b97cf8ea7f17501a4326c6515079dea07e5af438be8742d224d82ae29a978e83'))  # Your Appwrite API key

# Initialize the Reddit instance with environment variables
reddit = praw.Reddit(
    client_id=os.environ.get('BkTY-vpw82ZuDf3CKoQQwg'),
    client_secret=os.environ.get('VbOr1BBDCd2bnkL0mkTJ9Z7kah8h_w'),
    user_agent=os.environ.get('Necessary-Ad9670')
)

def download_video(url, filename):
    response = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

def main(request):
    try:
        # Parse the request payload
        data = json.loads(request['payload'])  
        subreddit_name = data.get('subreddit')

        # Check if subreddit name is provided
        if not subreddit_name:
            return json.dumps({'success': False, 'message': 'Subreddit name is missing.'})

        subreddit = reddit.subreddit(subreddit_name)
        video_data = []

        for submission in subreddit.top(limit=10):
            if submission.is_video:
                video_url = submission.media['reddit_video']['fallback_url']
                video_title = submission.title.replace(" ", "_") + '.mp4'
                
                # Download video
                download_video(video_url, video_title)
                
                # Prepare video metadata
                video_metadata = {
                    'title': submission.title,
                    'url': video_url,
                    'subreddit': subreddit_name,
                    'downloaded_at': str(datetime.now())
                }
                
                video_data.append(video_metadata)

        # Initialize the Appwrite Database service
        db = Database(client)

        # Save each video's metadata to Appwrite database
        for video in video_data:
            db.create_document(
                collection_id='videos',
                document_id='unique()',  # Generate a unique ID for each document
                data=video
            )

        return json.dumps({'success': True, 'message': 'Videos downloaded and saved successfully.'})

    except Exception as e:
        print(f"Error occurred: {e}")
        return json.dumps({'success': False, 'error': str(e)})
