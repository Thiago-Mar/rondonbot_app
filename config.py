from dotenv import load_dotenv
import os

load_dotenv()  # lê o .env

class Config:
    
    API_BASE_PORT = 5000
    CORS_ORIGINS = ["*"] # libera tudo


config = {
    "desenvolvimento": Config
}
 