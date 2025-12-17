from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://criptoid:criptoid@criptoid-db:5432/criptoid"
    quotes_service_url: str = "http://criptoid-quotes:9000"

settings = Settings()
