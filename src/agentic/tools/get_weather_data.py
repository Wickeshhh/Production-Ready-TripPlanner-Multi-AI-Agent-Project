from taskflowai import WebTools
from src.agentic.logger import logging
from src.agentic.exception import CustomException
import sys

class GetWeatherData:
    @classmethod
    def fetch_weather_data(cls):
        try:
            logging.info("Fetching weather data using WebTools.")
            weather_data = WebTools.get_weather_data
            logging.info("Weather data fetched successfully.")
            return weather_data
        except Exception as e:
            logging.info("Failed to fetch weather data.")
            raise CustomException(sys, e)

# from taskflowai import WebTools
# from src.agentic.logger import logging
# from src.agentic.exception import CustomException
# import sys
# import openmeteo_requests
# import requests_cache
# import pandas as pd
# from retry_requests import retry
# from src.agentic.utils import get_coordinates

# # Setup Open-Meteo API client with cache and retry mechanism
# cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
# retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
# openmeteo = openmeteo_requests.Client(session=retry_session)

# class GetWeatherData:
#     @classmethod
#     def fetch_weather_data(cls, city):
#         try:
#             logging.info(f"Fetching weather data for {city} using Open-Meteo API.")
#             latitude, longitude = get_coordinates(city)
            
#             if latitude is None or longitude is None:
#                 logging.error("Invalid city name or coordinates not found.")
#                 return None
            
#             url = "https://api.open-meteo.com/v1/forecast"
#             params = {
#                 "latitude": latitude,
#                 "longitude": longitude,
#                 "hourly": "temperature_2m"
#             }
            
#             responses = openmeteo.weather_api(url, params=params)
#             response = responses[0]
            
#             hourly = response.Hourly()
#             hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
            
#             hourly_data = {"date": pd.date_range(
#                 start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
#                 end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
#                 freq=pd.Timedelta(seconds=hourly.Interval()),
#                 inclusive="left"
#             )}
#             hourly_data["temperature_2m"] = hourly_temperature_2m
            
#             weather_df = pd.DataFrame(data=hourly_data)
#             logging.info("Weather data fetched successfully.")
#             return weather_df
#         except Exception as e:
#             logging.error("Failed to fetch weather data.", exc_info=True)
#             raise CustomException(sys, e)
