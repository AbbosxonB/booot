from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str = Field(alias="BOT_TOKEN")
    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")

    student_ticket_cooldown_minutes: int = Field(default=30, alias="STUDENT_TICKET_COOLDOWN_MINUTES")
    remind_after_minutes: int = Field(default=60, alias="REMIND_AFTER_MINUTES")
    escalate_after_minutes: int = Field(default=180, alias="ESCALATE_AFTER_MINUTES")

    superadmins: str = Field(default="", alias="SUPERADMINS")

    def superadmin_ids(self) -> set[int]:
        if not self.superadmins.strip():
            return set()
        return {int(x.strip()) for x in self.superadmins.split(",") if x.strip()}


settings = Settings()
