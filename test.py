import ollama


# Define the dummy function for geolocation
def get_geolocation(name):
    print(f"Dummy function called to get geolocation for: {name}")
    # Return dummy coordinates for the location
    return {"latitude": "-35.0281", "longitude": "138.8074"}


# Define the dummy function for weather
def get_current_weather(latitude, longitude):
    print(f"Dummy function called with latitude: {latitude}, longitude: {longitude}")
    # Return dummy weather data
    return {"temperature": "22°C", "condition": "Sunny"}


# Simulate chat and tool invocation
response = ollama.chat(
    model="llama3.2",
    messages=[
        {
            "role": "user",
            "content": "What is the weather in `Hahndorf, South Australia`?",
        }
    ],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_geolocation",
                "description": "Get the geographical coordinates of a place",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the place for which to get the coordinates",
                        },
                    },
                    "required": ["name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "string",
                            "description": "The Latitude of the location, along with North/South Hemisphere",
                        },
                        "longitude": {
                            "type": "string",
                            "description": "The Longitude of the location, along with East/West",
                        },
                    },
                    "required": ["latitude", "longitude"],
                },
            },
        },
    ],
)

print(response["message"])

# Handle response
if "tool_calls" in response["message"]:
    tools = response["message"]["tool_calls"]
    coordinates = None

    for tool in tools:
        if tool["function"]["name"] == "get_geolocation":
            params = tool["function"]["arguments"]
            name = params.get("name")
            coordinates = get_geolocation(name)  # Call geolocation function
            print("Coordinates:", coordinates)

        if tool["function"]["name"] == "get_current_weather" and coordinates:
            latitude = coordinates["latitude"]
            longitude = coordinates["longitude"]
            weather_data = get_current_weather(
                latitude, longitude
            )  # Call weather function
            print("Weather Data:", weather_data)
            break
else:
    print("No function call detected in the response.")
