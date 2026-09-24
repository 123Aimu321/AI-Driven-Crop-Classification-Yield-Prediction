# app/main.py
import httpx
import asyncio
import time

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Query,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from pydantic import BaseModel

from sqlalchemy import text
from sqlalchemy.orm import Session


from app.db.database import (
    get_db,
    init_db,
)

from app.services.auth_service import (
    authenticate_user,
    create_user,
)

from app.services.location_service import (
    reverse_geocode,
    search_location,
)

from app.services.soil_service import (
    get_soil_data,
)

from app.services.weather_service import (
    get_weather,
)

from app.services.climate_service import (
    get_annual_rainfall,
)

from app.services.crop_service import (
    predict_crop,
)

from app.services.yield_service import (
    predict_yield,
)

from app.services.fertilizer_service import (
    recommend_fertilizer,
)

from app.services.model_service import (
    model_service,
)


# =================================================
# APP
# =================================================

app = FastAPI(
    title="AI Agriculture API",
    version="1.0.0",
    description=(
        "AI driven crop classification, "
        "yield prediction and fertilizer "
        "guidance system."
    ),
)


# =================================================
# CORS
# =================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =================================================
# STARTUP
# =================================================

@app.on_event("startup")
def startup_event():

    init_db()

    print(
        "Loading ML models..."
    )

    model_service.load_models()

    print(
        "ML models are ready."
    )


# =================================================
# REQUEST MODELS
# =================================================

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# =================================================
# ROOT
# =================================================

@app.get("/")
def root():

    return {
        "success": True,
        "message": "AI Agriculture API is running.",
        "docs": "/docs",
    }


# =================================================
# HEALTH
# =================================================

@app.get("/health")
def health():

    return {
        "success": True,
        "status": "healthy",
    }


# =================================================
# AUTH
# =================================================

@app.post("/auth/signup")
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db),
):

    try:

        user = create_user(
            db=db,
            name=request.name,
            email=request.email,
            password=request.password,
        )

        return {
            "success": True,
            "message": "Account created successfully.",
            "user": user,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Signup failed: "
                + str(error)
            ),
        )


@app.post("/auth/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):

    try:

        user = authenticate_user(
            db=db,
            email=request.email,
            password=request.password,
        )

        if not user:

            raise HTTPException(
                status_code=401,
                detail="Invalid email or password.",
            )

        return {
            "success": True,
            "message": "Login successful.",
            "user": user,
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Login failed: "
                + str(error)
            ),
        )


# =================================================
# LOCATION SEARCH
# =================================================

@app.get("/location/search")
async def location_search(
    place: str,
):

    try:

        results = await search_location(
            place
        )

        return {
            "success": True,
            "results": results,
        }

    except httpx.HTTPError as error:

        raise HTTPException(
            status_code=502,
            detail=(
                "Location service failed: "
                + str(error)
            ),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Location search failed: "
                + str(error)
            ),
        )


# =================================================
# LOCATION BY COORDINATES
# =================================================

@app.get("/location/coordinates")
async def location_coordinates(
    latitude: float,
    longitude: float,
):

    try:

        location = await reverse_geocode(
            latitude,
            longitude,
        )

        return {
            "success": True,
            "location": location,
        }

    except httpx.HTTPError as error:

        raise HTTPException(
            status_code=502,
            detail=(
                "Location service failed: "
                + str(error)
            ),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Location lookup failed: "
                + str(error)
            ),
        )


# =================================================
# SOIL
# =================================================

@app.get("/soil")
async def soil_information(
    latitude: float,
    longitude: float,
):

    try:

        result = await get_soil_data(
            latitude,
            longitude,
        )

        return {
            "success": True,
            "soil": result,
        }

    except httpx.HTTPError as error:

        raise HTTPException(
            status_code=502,
            detail=(
                "Soil service failed: "
                + str(error)
            ),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Soil lookup failed: "
                + str(error)
            ),
        )


# =================================================
# WEATHER
# =================================================

@app.get("/weather")
async def weather_information(
    latitude: float,
    longitude: float,
):

    try:

        weather = await get_weather(
            latitude,
            longitude,
        )

        return {
            "success": True,
            "weather": weather,
        }

    except httpx.HTTPError as error:

        raise HTTPException(
            status_code=502,
            detail=(
                "Weather service failed: "
                + str(error)
            ),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Weather lookup failed: "
                + str(error)
            ),
        )


# =================================================
# FARM DATA  (fast parallel version)
# =================================================

@app.get("/farm-data")
async def farm_data(
    latitude: float,
    longitude: float,
):

    try:

        start_time = time.perf_counter()

        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        location_task = reverse_geocode(
            latitude,
            longitude,
        )

        # -------------------------------------------------
        # WEATHER + RAINFALL RUN IN PARALLEL
        # -------------------------------------------------

        weather_task = get_weather(
            latitude,
            longitude,
        )

        climate_task = get_annual_rainfall(
            latitude,
            longitude,
        )

        location, weather, climate = (
            await asyncio.gather(
                location_task,
                weather_task,
                climate_task,
            )
        )

        elapsed = (
            time.perf_counter()
            - start_time
        )

        print(
            f"/farm-data completed "
            f"in {elapsed:.3f}s"
        )

        return {
            "success": True,

            "location": location,

            "weather": {
                "temperature": weather.get(
                    "temperature"
                ),
                "humidity": weather.get(
                    "humidity"
                ),
                "precipitation": weather.get(
                    "precipitation"
                ),
                "rain": weather.get(
                    "rain"
                ),
                "wind_speed": weather.get(
                    "wind_speed"
                ),
                "forecast_24h_precipitation": (
                    weather.get(
                        "forecast_24h_precipitation"
                    )
                ),
                "forecast_24h_rain": (
                    weather.get(
                        "forecast_24h_rain"
                    )
                ),
                "soil_moisture": (
                    weather.get(
                        "soil_moisture"
                    )
                ),
                "soil_temperature": (
                    weather.get(
                        "soil_temperature"
                    )
                ),
                "timezone": weather.get(
                    "timezone"
                ),
            },

            "climate": climate,

            "performance": {
                "response_time_seconds": round(
                    elapsed,
                    3,
                )
            },
        }

    except httpx.HTTPError as error:

        raise HTTPException(
            status_code=502,
            detail=(
                "Automatic farm data service "
                "failed: "
                + str(error)
            ),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Farm data request failed: "
                + str(error)
            ),
        )


# =================================================
# CROP PREDICTION
# =================================================

@app.get("/predict/crop")
async def crop_prediction(
    latitude: float,
    longitude: float,
):

    try:

        location = await reverse_geocode(
            latitude,
            longitude,
        )

        state = location.get(
            "state"
        )

        if not state:

            raise HTTPException(
                status_code=502,
                detail=(
                    "State could not be detected "
                    "from the selected location."
                ),
            )

        weather, climate = await asyncio.gather(

            get_weather(
                latitude,
                longitude,
            ),

            get_annual_rainfall(
                latitude,
                longitude,
            ),
        )

        if not climate.get(
            "available"
        ):

            return {
                "success": False,
                "message": (
                    "Automatic annual rainfall "
                    "data is currently unavailable."
                ),
                "location": location,
                "weather": weather,
                "climate": climate,
            }

        annual_rainfall = climate.get(
            "annual_rainfall"
        )

        result = await asyncio.to_thread(
            predict_crop,
            state=state,
            annual_rainfall=annual_rainfall,
        )

        return {
            "success": result.get(
                "success",
                False,
            ),
            "prediction": result,
            "location": location,
            "weather": {
                "temperature": weather.get(
                    "temperature"
                ),
                "humidity": weather.get(
                    "humidity"
                ),
                "rain": weather.get(
                    "rain"
                ),
                "forecast_24h_rain": weather.get(
                    "forecast_24h_rain"
                ),
                "soil_moisture": weather.get(
                    "soil_moisture"
                ),
                "soil_temperature": weather.get(
                    "soil_temperature"
                ),
            },
            "climate": climate,
        }

    except HTTPException:
        raise

    except httpx.HTTPError as error:

        raise HTTPException(
            status_code=502,
            detail=(
                "Automatic weather/climate "
                "service failed: "
                + str(error)
            ),
        )

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Crop prediction failed: "
                + str(error)
            ),
        )


# =================================================
# YIELD PREDICTION
# =================================================

@app.get("/predict/yield")
async def yield_prediction(
    latitude: float,
    longitude: float,
    crop: str | None = None,
):

    try:

        location = await reverse_geocode(
            latitude,
            longitude,
        )

        state = location.get(
            "state"
        )

        if not state:

            raise HTTPException(
                status_code=502,
                detail=(
                    "State could not be detected "
                    "from the selected location."
                ),
            )

        climate = await get_annual_rainfall(
            latitude,
            longitude,
        )

        if not climate.get(
            "available"
        ):

            return {
                "success": False,
                "message": (
                    "Automatic annual rainfall "
                    "data is currently unavailable."
                ),
                "location": location,
                "climate": climate,
            }

        annual_rainfall = climate.get(
            "annual_rainfall"
        )

        if not crop:

            crop_result = await asyncio.to_thread(
                predict_crop,
                state=state,
                annual_rainfall=annual_rainfall,
            )

            if not crop_result.get(
                "success"
            ):

                return {
                    "success": False,
                    "message": (
                        "Crop prediction failed "
                        "before yield prediction."
                    ),
                    "crop_prediction": crop_result,
                    "location": location,
                    "climate": climate,
                }

            crop = crop_result.get(
                "crop"
            )

        result = await asyncio.to_thread(
            predict_yield,
            crop=crop,
            state=state,
            annual_rainfall=annual_rainfall,
        )

        return {
            "success": result.get(
                "success",
                False,
            ),
            "prediction": result,
            "location": location,
            "climate": climate,
        }

    except HTTPException:
        raise

    except httpx.HTTPError as error:

        raise HTTPException(
            status_code=502,
            detail=(
                "Automatic climate/location "
                "service failed: "
                + str(error)
            ),
        )

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Yield prediction failed: "
                + str(error)
            ),
        )


# =================================================
# FERTILIZER RECOMMENDATION
# =================================================

@app.get("/predict/fertilizer")
async def fertilizer_prediction(
    latitude: float,
    longitude: float,
    crop: str | None = None,
):

    try:

        location = await reverse_geocode(
            latitude,
            longitude,
        )

        state = location.get(
            "state"
        )

        if not state:

            raise HTTPException(
                status_code=502,
                detail=(
                    "State could not be detected "
                    "from the selected location."
                ),
            )

        climate = await get_annual_rainfall(
            latitude,
            longitude,
        )

        if not crop:

            if not climate.get(
                "available"
            ):

                return {
                    "success": False,
                    "message": (
                        "Crop cannot be automatically "
                        "determined because annual "
                        "rainfall data is unavailable."
                    ),
                }

            crop_result = await asyncio.to_thread(
                predict_crop,
                state=state,
                annual_rainfall=climate.get(
                    "annual_rainfall"
                ),
            )

            if not crop_result.get(
                "success"
            ):

                return {
                    "success": False,
                    "message": (
                        "Crop prediction failed "
                        "before fertilizer guidance."
                    ),
                    "crop_prediction": crop_result,
                    "location": location,
                }

            crop = crop_result.get(
                "crop"
            )

        result = await asyncio.to_thread(
            recommend_fertilizer,
            crop=crop,
            state=state,
        )

        return {
            "success": result.get(
                "success",
                False,
            ),
            "recommendation": result,
            "location": location,
            "climate": climate,
        }

    except HTTPException:
        raise

    except httpx.HTTPError as error:

        raise HTTPException(
            status_code=502,
            detail=(
                "Automatic location/climate "
                "service failed: "
                + str(error)
            ),
        )

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Fertilizer recommendation "
                "failed: "
                + str(error)
            ),
        )


# =================================================
# SAVE PREDICTION HISTORY
# =================================================

@app.post("/history")
async def save_prediction_history(
    user_id: int,
    latitude: float,
    longitude: float,
    predicted_crop: str | None = None,
    predicted_yield: float | None = None,
    fertilizer_recommendation: str | None = None,
    db: Session = Depends(get_db),
):

    try:

        location, weather, climate = await asyncio.gather(

            reverse_geocode(
                latitude,
                longitude,
            ),

            get_weather(
                latitude,
                longitude,
            ),

            get_annual_rainfall(
                latitude,
                longitude,
            ),
        )

        crop = predicted_crop

        season = None
        prediction_year = None

        if crop:

            crop_result = await asyncio.to_thread(
                predict_crop,
                state=location.get(
                    "state"
                ),
                annual_rainfall=climate.get(
                    "annual_rainfall"
                ),
            )

            if crop_result.get(
                "success"
            ):

                season = crop_result.get(
                    "season"
                )

                prediction_year = crop_result.get(
                    "year"
                )

        result = db.execute(
            text(
                """
                INSERT INTO prediction_history (

                    user_id,

                    location,

                    state,

                    country,

                    latitude,

                    longitude,

                    predicted_crop,

                    predicted_yield,

                    yield_unit,

                    fertilizer_recommendation,

                    annual_rainfall,

                    temperature,

                    humidity,

                    rain,

                    soil_moisture,

                    soil_temperature,

                    season,

                    prediction_year

                )

                VALUES (

                    :user_id,

                    :location,

                    :state,

                    :country,

                    :latitude,

                    :longitude,

                    :predicted_crop,

                    :predicted_yield,

                    :yield_unit,

                    :fertilizer_recommendation,

                    :annual_rainfall,

                    :temperature,

                    :humidity,

                    :rain,

                    :soil_moisture,

                    :soil_temperature,

                    :season,

                    :prediction_year

                )

                RETURNING id
                """
            ),
            {
                "user_id": user_id,

                "location": location.get(
                    "name"
                ),

                "state": location.get(
                    "state"
                ),

                "country": location.get(
                    "country"
                ),

                "latitude": latitude,

                "longitude": longitude,

                "predicted_crop": predicted_crop,

                "predicted_yield": predicted_yield,

                "yield_unit": (
                    "dataset yield units"
                    if predicted_yield is not None
                    else None
                ),

                "fertilizer_recommendation":
                    fertilizer_recommendation,

                "annual_rainfall":
                    climate.get(
                        "annual_rainfall"
                    ),

                "temperature":
                    weather.get(
                        "temperature"
                    ),

                "humidity":
                    weather.get(
                        "humidity"
                    ),

                "rain":
                    weather.get(
                        "rain"
                    ),

                "soil_moisture":
                    weather.get(
                        "soil_moisture"
                    ),

                "soil_temperature":
                    weather.get(
                        "soil_temperature"
                    ),

                "season": season,

                "prediction_year":
                    prediction_year,
            },
        )

        history_id = result.scalar_one()

        db.commit()

        return {
            "success": True,
            "message": (
                "Prediction history saved."
            ),
            "history_id": history_id,
        }

    except httpx.HTTPError as error:

        db.rollback()

        raise HTTPException(
            status_code=502,
            detail=(
                "Automatic location/weather "
                "service failed: "
                + str(error)
            ),
        )

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not save prediction "
                "history: "
                + str(error)
            ),
        )


# =================================================
# GET PREDICTION HISTORY
# =================================================

@app.get("/history")
def get_prediction_history(
    user_id: int,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):

    try:

        result = db.execute(
            text(
                """
                SELECT

                    id,

                    location,

                    state,

                    country,

                    latitude,

                    longitude,

                    predicted_crop,

                    predicted_yield,

                    yield_unit,

                    fertilizer_recommendation,

                    annual_rainfall,

                    temperature,

                    humidity,

                    rain,

                    soil_moisture,

                    soil_temperature,

                    season,

                    prediction_year,

                    created_at

                FROM prediction_history

                WHERE user_id = :user_id

                ORDER BY created_at DESC

                LIMIT :limit
                """
            ),
            {
                "user_id": user_id,
                "limit": limit,
            },
        )

        rows = result.mappings().all()

        history = [
            dict(row)
            for row in rows
        ]

        return {
            "success": True,
            "count": len(history),
            "history": history,
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not retrieve history: "
                + str(error)
            ),
        )