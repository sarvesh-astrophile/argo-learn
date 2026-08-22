try:
    import httpx
except ImportError:
    raise ImportError("The 'httpx' module is required. Run 'pip install httpx' to install the library.")

from typing import Any

from agno.tools import Toolkit

class GoogleMapsTool(Toolkit):
    def __init__(self, google_maps_api_key: str, **kwargs: Any):
        self.api_key: str = google_maps_api_key
        self.base_url: str = 'https://maps.googleapis.com/maps/api'

        tools = [
            self.get_place_maps_url
        ]

        super().__init__(name='google_maps_tool', tools=tools, **kwargs)


    def get_place_maps_url(self, place_name: str) -> str:
        """
        Get the Google Maps URL for a specific place using the place name.

        Args:
            place_name (str): The name of the place to search for.

        Returns:
            str: The Google Maps URL for the place.
        """
        search_endpoint = f'{self.base_url}/place/textsearch/json'
        params = {
            'query': place_name,
            'key': self.api_key,
            'fields': 'place_id'
        }

        try:
            response = httpx.get(search_endpoint, params=params)
            _ = response.raise_for_status()
            data: dict[str, Any] = response.json()
            if 'results' in data and data['results']:
                place_id: str = data['results'][0]['place_id']

                # Create a Google Maps URL using the place_id
                maps_url = f'https://www.google.com/maps/place/?q=place_id:{place_id}'
                return maps_url
            return f'No results found for place: {place_name}'

        except httpx.HTTPStatusError as e:
            return f'HTTP error occurred: {str(e)}'
        except Exception as e:
            return f'Unexpected error: {str(e)}'
