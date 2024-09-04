import os
import requests
import json
import praw
from datetime import datetime

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
    data = json.loads(request['payload'])  # Get data from request payload
    subreddit_name = data['subreddit']
    subreddit = reddit.subreddit(subreddit_name)
    
    for submission in subreddit.top(limit=10):
        if submission.is_video:
            video_url = submission.media['reddit_video']['fallback_url']
            video_title = submission.title.replace(" ", "_") + '.mp4'
            
            # Download video
            download_video(video_url, video_title)
            
            # Save video metadata to Appwrite database
            db = Appwrite.database.Database(client)
            db.createDocument(
                collectionId='videos',
                documentId='unique()',
                data={
                    'title': submission.title,
                    'url': video_url,
                    'subreddit': subreddit_name,
                    'downloaded_at': str(datetime.now())
                }
            )

    return json.dumps({'success': True, 'message': 'Videos downloaded and saved successfully.'})

