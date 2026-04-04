import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-jwt-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost:3306/ecommerce_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
