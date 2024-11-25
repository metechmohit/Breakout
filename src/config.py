import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# API Endpoints
SERPAPI_BASE_URL = "https://serpapi.com/search"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Google Sheets Configuration
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# LLM Configuration
LLM_MODEL = "mixtral-8x7b-32768"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 150

# Search Configuration
SEARCH_RESULTS_PER_QUERY = 5
SEARCH_REGION = "us"

# Rate Limiting
RATE_LIMIT_DELAY = 1  # seconds
MAX_RETRIES = 3