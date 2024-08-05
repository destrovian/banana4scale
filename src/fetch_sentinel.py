import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from datetime import datetime, timedelta
import numpy as np
from pyproj import Proj, transform
import time
import yaml

param = yaml.load(open('env.yaml'), Loader=yaml.FullLoader)

# OAuth client credentials
client_id = param['sentinel']['client_id']
client_secret = param['sentinel']['client_secret']

# Create a session for OAuth2
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)

# Fetch token
token_url = 'https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token'
token = oauth.fetch_token(token_url=token_url, client_secret=client_secret, include_client_id=True)

# Sentinel Hub WMS URL and instance ID
API_URL = 'https://services.sentinel-hub.com/ogc/wms/{instance_id}'
INSTANCE_ID = param['sentinel']['instance_id']  # Replace this with your actual instance ID

# Define the bounding box for Ukraine (rough coordinates)
WEST, SOUTH, EAST, NORTH = 8.55, 47.3, 8.6, 47.35
LAYERS = ('OUTLINE')
DATE_FORMAT = '%Y-%m-%d'

def fetch_image(date, bbox, width, height, tile_id):
    headers = {
        'Authorization': f'Bearer {token["access_token"]}'
    }
    params = {
        'SERVICE': 'WMS',
        'REQUEST': 'GetMap',
        'VERSION': '1.3.0',
        'LAYERS': LAYERS,
        'FORMAT': 'image/png',
        'BBOX': bbox,
        'WIDTH': 2500,
        'HEIGHT': 2500,
        'CRS': 'EPSG:4326',
        'TIME': date.strftime(DATE_FORMAT)
    }
    response = oauth.get(API_URL.format(instance_id=INSTANCE_ID), headers=headers, params=params)
    if response.status_code == 200:
        with open(f'data/image_{tile_id}_{date.strftime(DATE_FORMAT)}.png', 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to fetch image for date {date.strftime(DATE_FORMAT)}")
        print(response.text)


# Constants for Earth's radius and converting degrees to kilometers
EARTH_RADIUS_KM = 6371
DEGREE_TO_KM = (2 * np.pi * EARTH_RADIUS_KM) / 360

# Function to convert latitude or longitude degrees to kilometers
def degrees_to_km(degrees):
    return degrees * DEGREE_TO_KM

# Function to fetch images for a 1km by 1km grid within the bounding box
def fetch_images_in_grid(west, south, east, north, width=1000, height=1000):
    # Calculate the number of horizontal and vertical cells needed
    horizontal_cells = int(np.ceil(degrees_to_km(east - west) / (width / 1000)))
    vertical_cells = int(np.ceil(degrees_to_km(north - south) / (height / 1000)))

    # Iterate over each cell in the grid
    for i in range(horizontal_cells):
        for j in range(vertical_cells):
            # Calculate the bounding box for the current cell
            cell_width_deg = (east - west) / horizontal_cells
            cell_height_deg = (north - south) / vertical_cells
            cell_west = west + (cell_width_deg * i)
            cell_east = cell_west + cell_width_deg
            cell_south = south + (cell_height_deg * j)
            cell_north = cell_south + cell_height_deg

            # Construct the bounding box for the current cell
            cell_bbox = f"{cell_south}, {cell_west}, {cell_north}, {cell_east}"

            # Fetch the image for the current cell
            print(f"Fetching image for cell: {cell_bbox}")
            fetch_image(datetime.now(), cell_bbox, width, height, f"tile_{i}_{j}")

            # Wait for 1 second before fetching the next image
            time.sleep(1)

# Example usage
fetch_images_in_grid(WEST, SOUTH, EAST, NORTH)