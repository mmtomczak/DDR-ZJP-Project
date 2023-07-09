from spotify_api import SpotifyAPI
import time

CATEGORY_ID = 'toplists'


class Extractor:
    """ Extractor object used to extract relevant information from json data from Spotify API

    Args:
        client_id (str): ID of client used to gain access to Spotify API
        client_secret (str): Secret of client used to gain access to Spotify API

    Attributes:
        API_INSTANCE (:obj:`SpotifyAPI`): SpotifyAPI class object
    """

    def __init__(self, client_id, client_secret):
        self.API_INSTANCE = SpotifyAPI(client_id, client_secret)

    def extract_top50_global(self, category_id):
        """
        Returns "Top 50 Global" playlist information

        Args:
            category_id: id of Top 50 playlist category

        Returns:
            dict of name and id of Top 50 Global playlist
        """
        playlists = self.API_INSTANCE.get_playlists_from_category(category_id, 'PL')
        for item in playlists['playlists']['items']:
            if "Top 50" in item['name'] and "Świat" in item['name']:
                playlist_info = {
                    'name': item['name'],
                    'id': item['id']
                }
                return playlist_info

    def extract_top50_playlist(self, category_id, country_code):
        """
        Returns Top 50 playlist data for given country

        Args:
            category_id: category name of Top 50 playlist
            country_code: code of country in ISO A2 format

        Returns:
            dict containing Top 50 playlist name and id
        """
        playlists = self.API_INSTANCE.get_playlists_from_category(category_id, country_code)
        for item in playlists['playlists']['items']:
            if "most played tracks" in item['description'] and \
                    "Global" not in item['description'] and \
                    "USA" not in item['description']:
                playlist_info = {
                    'name': item['name'],
                    'id': item['id']
                }
                return playlist_info

    def extract_playlist_tracks(self, playlist_id):
        """
        Returns song data from given playlist

        Args:
            playlist_id: id of playlist

        Returns:
            dict of songs and corresponding data
        """
        tracks_raw_data = self.API_INSTANCE.get_tracks_from_playlist(playlist_id)
        tracks_final_data = []
        for item in tracks_raw_data['items']:
            track_data_dict = {
                'name': item['track']['name'],
                'artists': [artist['name'] for artist in item['track']['artists']],
                'id': item['track']['id'],
                'album': item['track']['album']['name'],
                'release_date': item['track']['album']['release_date'],
                'artists_followers': [],
                'popularity': item['track']['popularity']
            }
            for artist in item['track']['artists']:
                artist_id = artist['id']
                artist_data = self.API_INSTANCE.get_artist_info(artist_id)
                track_data_dict['artists_followers'].append(artist_data['followers']['total'])
            tracks_final_data.append(track_data_dict)
        return tracks_final_data

    def extract_track_features(self, track_id):
        """
        Returns dict of songs features

        Args:
            track_id: ID of song

        Returns:
            dict of song features data
        """
        features = self.API_INSTANCE.get_track_features(track_id)
        features_needed_data = {
            'acousticness': features['acousticness'],
            'danceability': features['danceability'],
            'duration_ms': features['duration_ms'],
            'energy': features['energy'],
            'instrumentalness': features['instrumentalness'],
            'liveness': features['liveness'],
            'loudness': features['loudness'],
            'speechiness': features['speechiness'],
            'tempo': features['tempo'],
            'valence': features['valence']
        }
        return features_needed_data

    def extract_track_audio_analysis(self, track_id):
        """
        Returns data about song audio analysis

        Args:
            track_id: ID of song

        Returns:
            dict of song audio analysis data
        """
        analysis = self.API_INSTANCE.get_track_audio_analysis(track_id)
        analysis_data = {
            'end_of_fade_in': analysis['track']['end_of_fade_in'],
            'start_of_fade_out': analysis['track']['start_of_fade_out'],
            'sections_number': len(analysis['sections']),
            'segments_number': len(analysis['segments'])
        }
        return analysis_data

    def add_tracks_information(self, tracks):
        """
        Adds audio features and analysis data for song in songs list

        Args:
            tracks: list of songs

        Returns:
            list of songs with added data
        """
        for track in tracks:
            track['features'] = self.extract_track_features(track['id'])
            track['analysis'] = self.extract_track_audio_analysis(track['id'])
        return tracks

    def extract_raw_data(self, countries):
        """
        Extract Top 50 playlist data for given countries

        Args:
            countries: list of country names in ISO A2 format

        Returns:
            dict of Top 50 data by country
        """
        country_data = {}
        top50_global = self.extract_top50_global(CATEGORY_ID)
        tracks = self.extract_playlist_tracks(top50_global['id'])
        print(top50_global['name'])
        country_data['GLOBAL'] = self.add_tracks_information(tracks)
        for country in countries:
            top50_playlist = self.extract_top50_playlist(CATEGORY_ID, country)
            print(top50_playlist['name'])
            tracks = self.extract_playlist_tracks(top50_playlist['id'])
            country_data[country] = self.add_tracks_information(tracks)
            time.sleep(2)
        print(f"{'*'*20}  DATA EXTRACTED  {'*'*20}")
        return country_data

    @staticmethod
    def format_extracted_data(country_data):
        """
        Formats raw country Top 50 playlist data to be suitable for DataFrame

        Args:
            country_data: dict of Top 50 playlist data by country

        Returns:
             dict of formatted data
        """
        formatted_data = {
            'market': [],
            'rank': [],
            'name': [],
            'artists': [],
            'artists_followers': [],
            'id': [],
            'album': [],
            'release_date': [],
            'popularity': [],
            'acousticness': [],
            'danceability': [],
            'duration_ms': [],
            'energy': [],
            'instrumentalness': [],
            'liveness': [],
            'loudness': [],
            'speechiness': [],
            'tempo': [],
            'valence': [],
            'end_of_fade_in': [],
            'start_of_fade_out': [],
            'sections_number': [],
            'segments_number': []
        }
        for country_code in country_data:
            # track number(position) at Top 50 playlist
            track_number = 1
            for track in country_data[country_code]:
                formatted_data['market'].append(country_code)
                formatted_data['rank'].append(track_number)
                track_number += 1
                formatted_data['name'].append(track['name'])
                formatted_data['artists'].append(track['artists'])
                formatted_data['artists_followers'].append(track['artists_followers'])
                formatted_data['id'].append(track['id'])
                formatted_data['album'].append(track['album'])
                formatted_data['release_date'].append(track['release_date'])
                formatted_data['popularity'].append(track['popularity'])
                formatted_data['acousticness'].append(track['features']['acousticness'])
                formatted_data['danceability'].append(track['features']['danceability'])
                formatted_data['duration_ms'].append(track['features']['duration_ms'])
                formatted_data['energy'].append(track['features']['energy'])
                formatted_data['instrumentalness'].append(track['features']['instrumentalness'])
                formatted_data['liveness'].append(track['features']['liveness'])
                formatted_data['loudness'].append(track['features']['loudness'])
                formatted_data['speechiness'].append(track['features']['speechiness'])
                formatted_data['tempo'].append(track['features']['tempo'])
                formatted_data['valence'].append(track['features']['valence'])
                formatted_data['end_of_fade_in'].append(track['analysis']['end_of_fade_in'])
                formatted_data['start_of_fade_out'].append(track['analysis']['start_of_fade_out'])
                formatted_data['sections_number'].append(track['analysis']['sections_number'])
                formatted_data['segments_number'].append(track['analysis']['segments_number'])
        return formatted_data
