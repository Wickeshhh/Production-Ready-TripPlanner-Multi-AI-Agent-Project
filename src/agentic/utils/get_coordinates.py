import requests
from src.agentic.logger import logging
from src.agentic.exception import CustomException
import sys

GOOGLE_API_KEY = "AIzaSyDkPsFe64dAlXcL231vXRSQ1EdSpjNB1Dg"

class CoordinatesFetcher:
    @classmethod
    def get_coordinates(cls, city):
        try:
            logging.info(f"Fetching coordinates for city: {city}")
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={GOOGLE_API_KEY}"
            response = requests.get(url).json()
            
            if response.get("status") == "OK":
                location = response["results"][0]["geometry"]["location"]
                latitude, longitude = location["lat"], location["lng"]
                logging.info(f"Coordinates for {city}: ({latitude}, {longitude})")
                return latitude, longitude
            else:
                logging.error("Failed to retrieve coordinates.")
                return None, None
        except Exception as e:
            logging.error("Error fetching coordinates.", exc_info=True)
            raise CustomException(sys, e)
