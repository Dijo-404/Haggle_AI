Haggle.ai: Autonomous Negotiation Agent

An AI-powered negotiation assistant designed to help businesses secure better deals from vendors. This project was developed for the OpenAI Open Model Hackathon.

Features

AI-Generated Counter-Offers: Generates three distinct negotiation strategies (Polite, Firm, and Term Swap).

Vendor Response Simulation: Allows you to test proposals and anticipate vendor reactions before sending them.

Savings Dashboard: Provides analytics to track negotiation wins and total savings over time.

Dual LLM Support: Offers the flexibility to switch between local Ollama models and the OpenAI API.

Persistent Storage: Utilizes an SQLite database to save and manage your negotiation history.

Prerequisites

Python 3.11+

LLM Access (choose one):

A local Ollama installation with a downloaded model (e.g., llama3.1:8b).

An active OpenAI API key.

Voice Transcription (Optional):

FFmpeg: Required for audio processing if you plan to use voice input.

macOS: brew install ffmpeg

Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg

Windows: Download the executable from ffmpeg.org and add it to your system's PATH.

Quick Setup

1. Clone and Install

# Clone the repository
git clone <your-repo-url>
cd haggle-ai

# Create a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt


2. Configure Environment

# Copy the environment template to create your configuration file
cp .env.example .env

# Edit the .env file with your preferred settings and API keys
nano .env # or use a different text editor


3. Choose Your LLM Engine

Option A: Using Ollama (Local)

Install Ollama: If you haven't already, download and install from the official Ollama website.

Pull the Model: Download the recommended model from the command line.

ollama pull llama3.1:8b


Start the Server: Ensure the Ollama server is running in the background.

ollama serve


Update .env: Set the following variables in your .env file.

ENGINE=ollama
OLLAMA_MODEL=llama3.1:8b


Option B: Using OpenAI (Cloud)

Get API Key: Retrieve your API key from the OpenAI Platform.

Update .env: Set the following variables in your .env file.

ENGINE=openai
OPENAI_API_KEY=your_sk_api_key_here
OPENAI_MODEL=gpt-4o-mini


4. Run the Application

streamlit run app.py


The application will launch in your default web browser, typically at http://localhost:8501.

Demo Script

Sample Vendor Message

Use this sample message to test the application's functionality:

Hi John,

Your annual SaaS subscription renewal is coming up next month. 
The new rate will be $6,000/year for the Professional plan.

Please confirm by Friday so we can process the renewal.

Best regards,
Sarah from VendorCorp


Demo Steps

Navigate to the "Negotiate" page from the sidebar.

Paste the sample vendor message into the provided text area.

Enter the relevant pricing context:

Previous/Current Price: $500 (per month)

Your Target Price: $400 (per month)

Service Type: SaaS Subscription

Relationship Length: 1-3 Years

Click "Generate Counter-Offers" to have the AI create three proposals.

Review the three generated strategies: Polite, Firm, and Term Swap.

Select a strategy by clicking its corresponding "Use Approach" button.

Click "Simulate Vendor Reply" to preview a likely response from the vendor.

Click "Save Negotiation" to record the outcome and update your dashboard.

Navigate to the "Dashboard" to view your aggregated savings and performance metrics.

Project Structure

haggle-ai/
├── app.py             # Main Streamlit UI application
├── agent.py           # Core negotiation logic and proposal generation
├── llm.py             # Wrapper for handling Ollama and OpenAI API calls
├── prompts.py         # Contains all system prompts and text templates
├── db.py              # SQLite database connection and operations
├── requirements.txt   # Python project dependencies
├── .env.example       # Template for environment variables
├── .env               # Your local configuration (create from example)
├── README.md          # This documentation file
└── haggle_ai.db       # SQLite database file (created automatically on run)


Configuration Options

Switching LLM Engines

You can switch between LLM providers at any time by editing your .env file.

# For local processing with Ollama
ENGINE=ollama
OLLAMA_MODEL=llama3.1:8b

# For cloud processing with OpenAI
ENGINE=openai
OPENAI_API_KEY=your_sk_api_key_here
OPENAI_MODEL=gpt-4o-mini


Available Models

Ollama:

llama3.1:8b (Recommended)

llama3:8b

mistral:7b

OpenAI:

gpt-4o-mini (Recommended for its balance of cost and performance)

gpt-4o (Higher quality, suitable for more complex negotiations)

gpt-3.5-turbo (Fast and budget-friendly option)

Testing the LLM Connection

You can verify your configuration and connection to the selected LLM service by running:

python llm.py


A successful connection will output a confirmation message and a test response from the model.

Troubleshooting

"Ollama connection error": Ensure the Ollama server is running with ollama serve. Use ollama list to verify that you have downloaded the required model.

"OpenAI API error": Double-check that your API key in the .env file is correct and that your OpenAI account has sufficient credits.

"Database is locked": This can occur if multiple instances of the application are running. Close all instances and restart. If the problem persists, deleting haggle_ai.db will reset the database (note: this will erase all saved data).

"ModuleNotFoundError": Re-install the required packages using pip install -r requirements.txt. It's best practice to use a virtual environment.

Deployment

Local Development

Run the application directly using Streamlit.

streamlit run app.py


Streamlit Community Cloud

Push your project to a public or private GitHub repository.

Connect your GitHub account to Streamlit Community Cloud.

Create a new app and select your repository.

In the advanced settings, add your .env variables (like OPENAI_API_KEY) as secrets.

Deploy the application.

Docker

A Dockerfile is provided for containerized deployment.

FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]


Build and run the container:

docker build -t haggle-ai .
docker run -p 8501:8501 -v $(pwd)/.env:/app/.env haggle-ai


Contributing

Contributions are welcome. Please follow these steps:

Fork the repository.

Create a new feature branch (git checkout -b feature/your-feature-name).

Make your changes and commit them with descriptive messages.

Ensure your code adheres to the project's style guidelines.

Submit a pull request for review.

Code Style

This project uses black for code formatting and flake8 for linting.

# Format code
black .

# Check for style issues
flake8 .


License

This project is licensed under the MIT License. See the LICENSE file for details.
