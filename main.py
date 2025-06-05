import asyncio
import json
import logging
import os
import shutil
from contextlib import AsyncExitStack
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client



class LLMClient:
    """Manages communication with the LLM provider."""

    def __init__(self, api_key: str) -> None:
        self.api_key: str = api_key

    def get_response(self, messages: list[dict[str, str]]) -> str:
        """Get a response from the LLM.

        Args:
            messages: A list of message dictionaries.

        Returns:
            The LLM's response as a string.

        Raises:
            httpx.RequestError: If the request to the LLM fails.
        """
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "messages": messages,
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "temperature": 0.7,
            "max_tokens": 4096,
            "top_p": 1,
            "stream": False,
            "stop": None,
        }

        try:
            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

        except httpx.RequestError as e:
            error_message = f"Error getting LLM response: {str(e)}"
            logging.error(error_message)

            if isinstance(e, httpx.HTTPStatusError):
                status_code = e.response.status_code
                logging.error(f"Status code: {status_code}")
                logging.error(f"Response details: {e.response.text}")

            return (
                f"I encountered an error: {error_message}. "
                "Please try again or rephrase your request."
            )


# Load environment variables
load_dotenv()
GROQ_API_KEY = "gsk_vbr85rIiP7tEf96gcD3zWGdyb3FYrOTRVhyOuR1H1yDx5Wl4Ayjm"
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Set it in .env file or environment.")

# Initialize LLM client
llm_client = LLMClient(api_key=GROQ_API_KEY)

# Mock flight database
flights = [
    {"flight_id": 1, "departure": "New York", "destination": "London", "date": "2025-06-10", "price": 500},
    {"flight_id": 2, "departure": "New York", "destination": "London", "date": "2025-06-10", "price": 600},
    {"flight_id": 3, "departure": "Paris", "destination": "Tokyo", "date": "2025-06-11", "price": 800},
    {"flight_id": 4, "departure": "New York", "destination": "Paris", "date": "2025-06-12", "price": 450},
]

def parse_user_input(user_input):
    # Use LLM to extract departure, destination, and date
    prompt = f"""
    You are a travel assistant. Extract the departure city, destination city, and travel date (in YYYY-MM-DD format) from the user's input.
    Return the result as a JSON object with keys: 'departure', 'destination', 'date'.
    If the date is vague (e.g., 'next week'), use 2025-06-10 as a default.
    If any information is missing or unclear, set the value to null.
    Example input: "Book a flight from New York to London on June 10, 2025"
    Example output: {{"departure": "New York", "destination": "London", "date": "2025-06-10"}}
    User input: {user_input}
    """
    messages = [{"role": "user", "content": prompt}]
    response_str = llm_client.get_response(messages)
    try:
        return json.loads(response_str)
    except Exception:
        # fallback: try to extract JSON from response
        import re
        match = re.search(r"\{.*\}", response_str, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise

def search_flights(departure, destination, date):
    matching_flights = []
    for flight in flights:
        if (departure and flight["departure"] == departure) and \
           (destination and flight["destination"] == destination) and \
           (date and flight["date"] == date):
            matching_flights.append(flight)
    return matching_flights

def generate_flight_options_response(matching_flights):
    if not matching_flights:
        prompt = "No flights were found. Generate a friendly response apologizing and suggesting the user try different dates or destinations."
    else:
        flight_list = "\n".join([f"Flight ID: {f['flight_id']}, {f['departure']} to {f['destination']}, Date: {f['date']}, Price: ${f['price']}" for f in matching_flights])
        prompt = f"""
        You are a travel assistant. Generate a friendly response listing these flights:
        {flight_list}
        Ask the user to choose a flight by entering its Flight ID.
        """
    messages = [{"role": "user", "content": prompt}]
    return llm_client.get_response(messages)

def confirm_booking(flight_id, flights):
    selected_flight = next((f for f in flights if f["flight_id"] == flight_id), None)
    if not selected_flight:
        prompt = "The selected flight ID is invalid. Generate a friendly response asking the user to choose a valid Flight ID."
    else:
        prompt = f"""
        You are a travel assistant. Generate a friendly confirmation message for booking:
        Flight ID: {selected_flight['flight_id']}, {selected_flight['departure']} to {selected_flight['destination']}, Date: {selected_flight['date']}, Price: ${selected_flight['price']}
        """
    messages = [{"role": "user", "content": prompt}]
    return llm_client.get_response(messages)

def main():
    print("Welcome to the Smart Flight Booking Agent!")
    user_input = input("Tell me your flight request (e.g., 'Book a flight from New York to London on June 10, 2025'): ")

    # Step 1: Parse user input with LLM
    try:
        parsed_input = parse_user_input(user_input)
        departure = parsed_input.get("departure")
        destination = parsed_input.get("destination")
        date = parsed_input.get("date")
    except Exception as e:
        print("Sorry, I couldn't understand your request. Please try again.")
        return

    # Step 2: Search for flights
    matching_flights = search_flights(departure, destination, date)

    # Step 3: Generate response with flight options
    response = generate_flight_options_response(matching_flights)
    print("\n" + response)

    # Step 4: Book flight if applicable
    if matching_flights:
        try:
            flight_id = int(input("\nEnter the Flight ID to book: "))
            confirmation = confirm_booking(flight_id, matching_flights)
            print("\n" + confirmation)
        except ValueError:
            print("Please enter a valid Flight ID number.")

if __name__ == "__main__":
    main()