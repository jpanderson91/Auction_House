import requests
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

print('Generating Access Token ...')

def create_access_token(client_id, client_secret, region='us'):
    data = {'grant_type': 'client_credentials'}
    response = requests.post('https://%s.battle.net/oauth/token' % region, data=data, auth=(client_id, client_secret))
    return response.json()

def get_tichondrius(token):
    url = "https://us.api.blizzard.com/data/wow/connected-realm/3684/auctions"
    params = {
        "namespace": "dynamic-us",
        "locale": "en_US",
        "access_token": token
    }
    print(f"GET {url}")  # Added print statement before the request
    response = requests.get(url, params=params)
    print("Status code:", response.status_code)
    print("Response text:", response.text)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch auctions: {response.status_code}")
    return response.json()["auctions"]

# Get credentials from environment variables
client_id = os.environ.get('BLIZZARD_CLIENT_ID')
client_secret = os.environ.get('BLIZZARD_CLIENT_SECRET')

response = create_access_token(client_id, client_secret, region='us')
print(response)  # Print the API response for debugging
token = response['access_token']

tichondrius_auctions = get_tichondrius(token)
auction_df = pd.DataFrame(tichondrius_auctions)

auction_df = auction_df.rename(columns={"id": "auction_id",})
auction_df = pd.concat([auction_df.drop(['item'], axis=1), auction_df['item'].apply(pd.Series)], axis=1)

auction_df['collection_year'] = datetime.now().strftime('%Y')
auction_df['collection_month'] = datetime.now().strftime('%m')
auction_df['collection_day'] = datetime.now().strftime('%d')
auction_df['collection_hour'] = datetime.now().strftime('%H')

filename = datetime.now().strftime('Tichondrius_US-%Y-%m-%d-%H-%M.csv')
print('Exporting Data ...')
auction_df.to_csv(filename, index=False)

print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret}")
