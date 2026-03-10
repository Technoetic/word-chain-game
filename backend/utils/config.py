from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    anthropic_base_url: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"
    deepgram_api_key: str = ""
    korean_dict_api_key: str = ""
    korean_dict_api_url: str = "https://stdict.korean.go.kr/api/search.do"
    timer_duration: int = 15
    max_combo: int = 5
    ws_cors_origins: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
