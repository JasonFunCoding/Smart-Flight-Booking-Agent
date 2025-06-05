# Smart Flight Booking Agent

This project is a simple AI-powered command-line assistant for booking flights. It uses a Large Language Model (LLM) to understand natural language requests, extract travel details, and interact with users in a conversational manner.

## Features
- **Natural Language Understanding:** Users can type requests like "Book a flight from New York to London on June 10, 2025".
- **LLM-Powered Parsing:** The agent uses an LLM to extract departure city, destination, and date from user input.
- **Mock Flight Database:** Searches a small set of sample flights for matches.
- **Conversational Responses:** The LLM generates friendly, context-aware responses and confirmations.
- **Simple Booking Flow:** Users can select a flight by ID and receive a booking confirmation.

## Requirements
- Python 3.8+
- [httpx](https://www.python-httpx.org/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [mcp](https://pypi.org/project/mcp/) (for Model Context Protocol integration)

## Setup
1. **Clone the repository:**
   ```powershell
   git clone <this-repo-url>
   cd AIAgentBooking
   ```
2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
   Or install manually:
   ```powershell
   pip install httpx python-dotenv mcp
   ```
3. **Set up your API key:**
   - Create a `.env` file in the project root with:
     ```env
     GROQ_API_KEY=your_groq_api_key_here
     ```
   - Or set the `GROQ_API_KEY` environment variable.

## Usage
Run the agent from the command line:
```powershell
python main.py
```
Follow the prompts to enter your flight request and book a flight.

## Customization
- **Flight Data:** Edit the `flights` list in `main.py` to add or modify available flights.
- **LLM Model:** The code uses Groq's Llama-4 model by default. You can change the model or API endpoint in `main.py`.

## License
This project is for educational/demo purposes. See LICENSE if provided.
