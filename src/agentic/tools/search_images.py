from taskflowai import WikipediaTools
from src.agentic.logger import logging
from src.agentic.exception import CustomException
import sys

class WikiImages:
    @classmethod
    def search_images(cls):
        try:
            logging.info("Searching images using WikipediaTools.")
            images = WikipediaTools.search_images
            logging.info("Images searched successfully.")
            return images
        except Exception as e:
            logging.info("Failed to search images from Wikipedia.")
            raise CustomException(sys, e)

# import requests
# from src.agentic.logger import logging
# from src.agentic.exception import CustomException
# import sys

# GOOGLE_API_KEY = "AIzaSyDkPsFe64dAlXcL231vXRSQ1EdSpjNB1Dg"

# class WikiImages:
#     @classmethod
#     def search_images(cls, location):
#         try:
#             logging.info(f"Searching images for places in: {location} using Google Places API.")
#             url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=places+to+visit+in+{location}&key={GOOGLE_API_KEY}"
#             response = requests.get(url)
            
#             if response.status_code == 200:
#                 places_data = response.json().get("results", [])
#                 if not places_data:
#                     logging.warning("No places found for the given location.")
#                     return None
                
#                 image_urls = []
#                 for place in places_data:
#                     if "photos" in place:
#                         photo_reference = place["photos"][0]["photo_reference"]
#                         photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_API_KEY}"
#                         image_urls.append(photo_url)
                
#                 logging.info("Image search completed successfully.")
#                 return image_urls if image_urls else None
#             else:
#                 logging.error("Failed to retrieve place images from Google API.")
#                 return None
#         except Exception as e:
#             logging.error("Failed to search images.", exc_info=True)
#             raise CustomException(sys, e)
