import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured in .env"
    )


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def init_db():

    with engine.begin() as connection:

        # -----------------------------------------
        # USERS
        # -----------------------------------------

        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(150) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    google_id VARCHAR(255) UNIQUE,
                    created_at TIMESTAMPTZ
                        DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
        )

        # -----------------------------------------
        # IRRIGATION HISTORY
        # -----------------------------------------

        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS irrigation_history (
                    id BIGSERIAL PRIMARY KEY,

                    location VARCHAR(150) NOT NULL,

                    state VARCHAR(150),

                    country VARCHAR(100),

                    latitude DOUBLE PRECISION NOT NULL,

                    longitude DOUBLE PRECISION NOT NULL,

                    soil_type VARCHAR(100),

                    temperature DOUBLE PRECISION,

                    humidity DOUBLE PRECISION,

                    rain DOUBLE PRECISION,

                    soil_moisture DOUBLE PRECISION,

                    evapotranspiration
                        DOUBLE PRECISION,

                    forecast_rain_24h
                        DOUBLE PRECISION,

                    irrigation_status
                        VARCHAR(50),

                    recommendation TEXT,

                    created_at TIMESTAMPTZ
                        DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
        )

        # Add user_id if old database already exists
        connection.execute(
            text(
                """
                ALTER TABLE irrigation_history
                ADD COLUMN IF NOT EXISTS user_id BIGINT;
                """
            )
        )

        # Foreign key
        connection.execute(
            text(
                """
                DO $$
                BEGIN

                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_constraint
                        WHERE conname =
                            'fk_irrigation_history_user'
                    ) THEN

                        ALTER TABLE irrigation_history

                        ADD CONSTRAINT
                            fk_irrigation_history_user

                        FOREIGN KEY (user_id)

                        REFERENCES users(id)

                        ON DELETE CASCADE;

                    END IF;

                END
                $$;
                """
            )
        )

        # Irrigation indexes
        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS
                idx_irrigation_history_created_at

                ON irrigation_history(
                    created_at DESC
                );
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS
                idx_irrigation_history_user_id

                ON irrigation_history(
                    user_id
                );
                """
            )
        )

        # -----------------------------------------
        # PREDICTION HISTORY
        # -----------------------------------------

        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS prediction_history (

                    id BIGSERIAL PRIMARY KEY,

                    user_id BIGINT NOT NULL,

                    location VARCHAR(150),

                    state VARCHAR(150),

                    country VARCHAR(100),

                    latitude DOUBLE PRECISION,

                    longitude DOUBLE PRECISION,

                    predicted_crop VARCHAR(50),

                    predicted_yield DOUBLE PRECISION,

                    yield_unit VARCHAR(100),

                    fertilizer_recommendation TEXT,

                    annual_rainfall DOUBLE PRECISION,

                    temperature DOUBLE PRECISION,

                    humidity DOUBLE PRECISION,

                    rain DOUBLE PRECISION,

                    soil_moisture DOUBLE PRECISION,

                    soil_temperature DOUBLE PRECISION,

                    season VARCHAR(50),

                    prediction_year INTEGER,

                    created_at TIMESTAMPTZ
                        DEFAULT CURRENT_TIMESTAMP,

                    CONSTRAINT
                        fk_prediction_history_user

                    FOREIGN KEY (user_id)

                    REFERENCES users(id)

                    ON DELETE CASCADE
                );
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS
                idx_prediction_history_user_id

                ON prediction_history(
                    user_id
                );
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS
                idx_prediction_history_created_at

                ON prediction_history(
                    created_at DESC
                );
                """
            )
        )