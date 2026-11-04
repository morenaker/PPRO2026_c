from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://ordinace:ordinace_dev@localhost:5432/ordinace"
    timezone: str = "Europe/Prague"
    # Výchozí délka termínu v minutách (viz README, rozhodnutí D1).
    default_appointment_minutes: int = 15
    # Podpis session cookie. Vývojová hodnota; mimo lokální vývoj nastavit přes SECRET_KEY.
    secret_key: str = "dev-only-secret-key-change-me"
    # Ukázkové účty (jen demo, viz README D12). Přepsatelné přes env.
    demo_admin_password: str = "admin-demo"
    demo_reception_password: str = "recepce-demo"


settings = Settings()
