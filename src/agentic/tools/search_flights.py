from taskflowai import AmadeusTools
from src.agentic.logger import logging
from src.agentic.exception import CustomException
import sys

class SearchFlights:
    @classmethod
    def search_flights_tool(cls):
        try:
            logging.info("Initiating flight search using AmadeusTools.")
            search_flights = AmadeusTools.search_flights
            logging.info("Flight search initiated successfully.")
            return search_flights
        except Exception as e:
            logging.info("Failed to initiate flight search.")
            raise CustomException(sys, e)

# import requests
# from src.agentic.logger import logging
# from src.agentic.exception import CustomException
# import sys
# import pandas as pd

# SERP_API_KEY ="59439eb88618e871652631bff6d148d56b78e42c291dbe86469d1b36e6957a10"

# class SearchFlights:
#     @classmethod
#     def get_iata_code(cls, city, iata_df):
#         """Fetch IATA code for a given city from CSV."""
#         try:
#             result = iata_df[iata_df["city_name"].str.lower() == city.lower()]
#             return result["iata_code"].values[0] if not result.empty else None
#         except Exception as e:
#             logging.error("Error fetching IATA code.", exc_info=True)
#             raise CustomException(sys, e)

#     @classmethod
#     def search_flights_tool(cls, origin, destination, outbound_date, return_date, currency="INR"):
#         try:
#             logging.info(f"Searching flights from {origin} to {destination} using SERP API.")
#             iata_df = pd.read_csv("india_airport_codes.csv")
#             origin_iata = cls.get_iata_code(origin, iata_df)
#             destination_iata = cls.get_iata_code(destination, iata_df)
            
#             if not origin_iata or not destination_iata:
#                 logging.error("Invalid origin or destination IATA code.")
#                 return None
            
#             url = f"https://serpapi.com/search.json?engine=google_flights&departure_id={origin_iata}&arrival_id={destination_iata}&outbound_date={outbound_date}&return_date={return_date}&currency={currency}&hl=en&api_key={SERP_API_KEY}"
#             response = requests.get(url)
            
#             if response.status_code == 200:
#                 logging.info("Flight search completed successfully.")
#                 return response.json()
#             else:
#                 logging.error("Failed to retrieve flight data from SERP API.")
#                 return None
#         except Exception as e:
#             logging.error("Failed to search flights.", exc_info=True)
#             raise CustomException(sys, e)
