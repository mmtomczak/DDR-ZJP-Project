import requests
import base64
from urllib.parse import urlencode


class SpotifyAPI:
    """ Spotify API object used to extract music data

    Args:
        client_id (str): ID of API client
        client_secret (str): Secret of API client

    Attributes:
        TOKEN_URL (str): URL used to get access token
        API_BASE_URL (str): base of URL used to access data from API
        __client_id (str): ID of client - used to authorize API access
        __client_secret (str): Secret of client - used to authorize API access
        access_response (:obj:`json`): json object of Spotify API response
        access_token (str): access token used to authorize information extraction
    """
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    API_BASE_URL = 'https://api.spotify.com/v1/'

    def __init__(self, client_id, client_secret):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.access_response = self.generate_access_response()
        self.access_token = self.access_response['access_token']

    def generate_access_response(self):
        """
        Generates API access response

        Returns:
            json object containing response data
        """
        authentication_string = f"{self.__client_id}:{self.__client_secret}"
        authentication_string_encoded = authentication_string.encode()

        headers = {
            'Authorization': f"Basic {base64.b64encode(authentication_string_encoded).decode()}",
            'Content-Type': "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "client_credentials"
        }

        response = requests.post(self.TOKEN_URL, data=data, headers=headers)
        return response.json()

    def get_base_headers(self):
        """
        Returns headers used to authorize API data access

        Returns:
            headers dict containing authorization data
        """
        headers = {
            'Authorization': f"Bearer {self.access_token}"
        }
        return headers

    def get_categories_for_country(self, country_code):
        """
        Returns all playlist categories for given country

        Args:
            country_code: country code in ISO A2 format

        Returns:
            json object containing response data
        """
        url = f"{self.API_BASE_URL}browse/categories"
        headers = self.get_base_headers()
        data = urlencode({
            "country": country_code
        })
        request_url = f"{url}?{data}"
        response = requests.get(request_url, headers=headers)
        return response.json()

    def get_playlists_from_category(self, category_id, country_code):
        """
        Returns all playlists that are connected to given category in given country

        Args:
            category_id: id of category
            country_code: country code in ISO A2 format

        Returns:
            json object with response data
        """
        url = f"{self.API_BASE_URL}browse/categories/{category_id}/playlists"
        headers = self.get_base_headers()
        data = urlencode({
            "country": country_code
        })
        request_url = f"{url}?{data}"
        response = requests.get(request_url, headers=headers)
        return response.json()

    def get_tracks_from_playlist(self, playlist_id):
        """
        Returns all tracks present in given playlist

        Args:
            playlist_id: id of playlist

        Returns:
            json object with response data
        """
        url = f"{self.API_BASE_URL}playlists/{playlist_id}/tracks"
        headers = self.get_base_headers()
        response = requests.get(url, headers=headers)
        return response.json()

    def get_track_features(self, song_id):
        """
        Returns track features of given song

        Args:
            song_id: id of song

        Returns:
            json object with response data
        """
        url = f"{self.API_BASE_URL}audio-features/{song_id}"
        headers = self.get_base_headers()
        response = requests.get(url, headers=headers)
        return response.json()

    def get_track_audio_analysis(self, song_id):
        """
        Returns audio analysis data of given song

        Args:
            song_id: id of song

        Returns:
            json object with response data
        """
        url = f"{self.API_BASE_URL}audio-analysis/{song_id}"
        headers = self.get_base_headers()
        response = requests.get(url, headers=headers)
        return response.json()

    def get_artist_info(self, artist_id):
        """
        Returns information about given artist

        Args:
            artist_id: id of artist

        Returns:
            json object with response data
        """
        url = f"{self.API_BASE_URL}artists/{artist_id}"
        headers = self.get_base_headers()
        response = requests.get(url, headers=headers)
        return response.json()


