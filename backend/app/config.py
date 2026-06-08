import os
from dotenv import load_dotenv

load_dotenv()

class config:
    SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-charge-in-prod")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres@localhost:5432/symptomtrack"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    from datetime import timedelta
    JWT_ACCESS_TOKEN_EXPRESS = timedelta(days=7)