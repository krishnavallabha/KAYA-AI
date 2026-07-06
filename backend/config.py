# manage app settings, db url, api keys... we use pydantic_settings to auto read config from env var 


import os 
from pydantic_settings import BaseSettings 


class Settings(BaseSettings):
    PROJECT_NAME:str = "FlowSense Backend"
    API_V1_STR:str = "/api/v1"
    DATABASE_URL:str = os.getenv("DATABASE_URL","sqlite:///./flowsense.db")
    OPENAI_API_KEY:str = os.getenv("OPENAI_API_KEY","")
    GEMINI_API_KEY:str = os.getenv("GEMINI_API_KEY","")

    class Config:
        case_sensitive = True 

settings = Settings()