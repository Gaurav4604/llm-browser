import ollama
import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


url = "https://api.open-meteo.com/v1/forecast"


# Define the dummy function for weather
def get_current_weather(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m",
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    print(f"function called with latitude: {latitude}, longitude: {longitude}")
    # Return dummy weather data
    # Process first location. Add a for-loop for multiple locations or weather models
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
    }
    hourly_data["temperature_2m"] = hourly_temperature_2m

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    print(hourly_dataframe)


# Simulate chat and tool invocation
response = ollama.chat(
    model="llama3.2",
    messages=[
        {
            "role": "user",
            "content": "Is it going to rain tomorrow in Saitama, Japan?",
        }
    ],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "integer",
                            "description": "The Latitude with Decimal point of the location, along with North/South Hemisphere",
                        },
                        "longitude": {
                            "type": "integer",
                            "description": "The Longitude with Decimal point of the location, along with East/West",
                        },
                    },
                    "required": ["latitude", "longitude"],
                },
            },
        },
    ],
)

print(response["message"]["tool_calls"])

# Handle response
if response["message"]["tool_calls"] is not None:
    tools = response["message"]["tool_calls"]
    # coordinates = None

    for tool in tools:
        # if tool["function"]["name"] == "get_geolocation":
        #     params = tool["function"]["arguments"]
        #     name = params.get("name")
        #     coordinates = get_geolocation(name)  # Call geolocation function
        #     print("Coordinates:", coordinates)

        if tool["function"]["name"] == "get_current_weather":
            latitude = tool["function"]["arguments"]["latitude"]
            longitude = tool["function"]["arguments"]["longitude"]
            weather_data = get_current_weather(
                latitude, longitude
            )  # Call weather function
            print("Weather Data:", weather_data)
            break
else:
    print("No function call detected in the response.")
