from dotenv import load_dotenv
import os


_ = load_dotenv()

google_maps_api_key = os.getenv("GOOGLE_MAPS_PLACES_API_KEY")
if not google_maps_api_key:
    raise RuntimeError("API_KEY is not set. Add it to your .env file.")

exa_api_key = os.getenv("EXA_API_KEY")
if not exa_api_key:
    raise RuntimeError("EXA_API_KEY is not set. Add it to your .env file.")
