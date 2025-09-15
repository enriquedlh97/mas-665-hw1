"""Configuration settings for the Enrique Crew system."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Calendly configuration
    calendly_link: str = Field(
        default="https://calendly.com/your-handle/30min",
        env="CALENDLY_LINK",
        description="Public Calendly link for Enrique's calendar",
    )

    # MCP Server configuration
    mcp_server_url: str = Field(
        default="http://localhost:3000",
        env="MCP_SERVER_URL",
        description="URL of the Playwright MCP server",
    )

    # Timezone configuration
    timezone: str = Field(
        default="America/New_York",
        env="TIMEZONE",
        description="Timezone for scheduling",
    )

    # OpenAI configuration
    openai_api_key: str | None = Field(
        default=None, env="OPENAI_API_KEY", description="OpenAI API key for LLM"
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        env="OPENAI_MODEL",
        description="OpenAI model to use for LLM",
    )
    openai_temperature: float = Field(
        default=0.7,
        env="OPENAI_TEMPERATURE",
        description="Temperature for OpenAI model (0.0-2.0)",
    )

    # Backend selection
    booking_backend: str = Field(
        default="playwright_mcp",
        env="BOOKING_BACKEND",
        description="Backend to use: 'playwright_mcp' or 'calendly_api'",
    )

    # Debug mode
    debug: bool = Field(default=False, env="DEBUG", description="Enable debug mode")

    # CrewAI configuration
    verbose: bool = Field(
        default=True, env="VERBOSE", description="Enable verbose output from agents"
    )
    memory_enabled: bool = Field(
        default=True, env="MEMORY_ENABLED", description="Enable conversation memory"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
