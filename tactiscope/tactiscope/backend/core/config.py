import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    REKA_API_KEY: str = os.getenv("REKA_API_KEY", "")
    FASTINO_API_KEY: str = os.getenv("FASTINO_API_KEY", "")
    YUTORI_API_KEY: str = os.getenv("YUTORI_API_KEY", "")

    REKA_BASE_URL: str = "https://vision-agent.api.reka.ai"
    FASTINO_BASE_URL: str = "https://api.pioneer.ai"
    YUTORI_BASE_URL: str = "https://api.yutori.com"

    def validate(self) -> list[str]:
        errors = []
        if not self.REKA_API_KEY:
            errors.append("REKA_API_KEY is not set")
        if not self.FASTINO_API_KEY:
            errors.append("FASTINO_API_KEY is not set")
        if not self.YUTORI_API_KEY:
            errors.append("YUTORI_API_KEY is not set")
        return errors


settings = Settings()
