import os

from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

_ = load_dotenv()

# Set AGNO_DEBUG=false to silence debug output
DEBUG = os.getenv("AGNO_DEBUG", "true").lower() == "true"


def get_api_key(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is not set. Add it to your .env file.")
    return value


def get_model() -> OpenAIChat:
    return OpenAIChat(
        id="deepseek-v4-flash",
        base_url="https://api.deepseek.com",
        api_key=get_api_key("API_KEY"),
        # The provider rejects the "developer" role that agno maps "system" to by default
        role_map={
            "system": "system",
            "user": "user",
            "assistant": "assistant",
            "tool": "tool",
            "model": "assistant",
        },
    )


def get_db() -> SqliteDb:
    return SqliteDb(db_file="agent.db")
