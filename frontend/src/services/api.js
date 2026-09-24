// frontend/src/services/api.js
import axios from "axios";

const API_BASE_URL =
  "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,

  // Fast failure instead of waiting 45 seconds.
  timeout: 15000,

  headers: {
    "Content-Type": "application/json",
  },
});

export default api;

/* =====================================================
   REQUEST CANCELLATION
===================================================== */

export function createCancelToken() {
  return new AbortController();
}

/* =====================================================
   GENERAL HELPERS
===================================================== */

export function firstDefined(...values) {
  for (const value of values) {
    if (
      value !== undefined &&
      value !== null &&
      value !== ""
    ) {
      return value;
    }
  }

  return null;
}

export function toNumber(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return null;
  }

  const number = Number(value);

  return Number.isFinite(number)
    ? number
    : null;
}

export function toText(
  value,
  fallback = ""
) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return fallback;
  }

  if (typeof value === "string") {
    return value;
  }

  if (
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }

  return fallback;
}

export function getErrorMessage(
  error,
  fallback = "Something went wrong."
) {
  // Cancelled requests are not real errors.
  if (
    axios.isCancel?.(error) ||
    error?.name === "CanceledError" ||
    error?.code === "ERR_CANCELED"
  ) {
    return "Request cancelled.";
  }

  // Timeouts deserve a friendly message.
  if (
    error?.code === "ECONNABORTED" ||
    /timeout/i.test(error?.message || "")
  ) {
    return (
      "The request timed out. " +
      "The backend took too long to respond."
    );
  }

  const data =
    error?.response?.data;

  if (
    typeof data?.detail === "string"
  ) {
    return data.detail;
  }

  if (
    Array.isArray(data?.detail)
  ) {
    return data.detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

        return (
          item?.msg ||
          item?.message ||
          "Invalid request."
        );
      })
      .join(", ");
  }

  if (typeof data === "string") {
    return data;
  }

  if (
    error?.message ===
    "Network Error"
  ) {
    return (
      "Cannot connect to the backend. " +
      "Make sure FastAPI is running on port 8000."
    );
  }

  return (
    error?.message ||
    fallback
  );
}

/* =====================================================
   AUTH
===================================================== */

export async function signup(
  name,
  email,
  password
) {
  const response =
    await api.post(
      "/auth/signup",
      {
        name,
        email,
        password,
      }
    );

  return response.data;
}

export async function login(
  email,
  password
) {
  const response =
    await api.post(
      "/auth/login",
      {
        email,
        password,
      }
    );

  return response.data;
}

/* =====================================================
   LOCATION
===================================================== */

export function normalizeLocation(
  item
) {
  if (
    !item ||
    typeof item !== "object"
  ) {
    return null;
  }

  const latitude =
    toNumber(
      firstDefined(
        item.latitude,
        item.lat,
        item.location?.latitude,
        item.location?.lat
      )
    );

  const longitude =
    toNumber(
      firstDefined(
        item.longitude,
        item.lon,
        item.lng,
        item.location?.longitude,
        item.location?.lon,
        item.location?.lng
      )
    );

  if (
    latitude === null ||
    longitude === null
  ) {
    return null;
  }

  return {
    name: toText(
      firstDefined(
        item.name,
        item.city,
        item.location?.name
      ),
      "Selected Location"
    ),

    state: toText(
      firstDefined(
        item.state,
        item.region,
        item.location?.state
      ),
      ""
    ),

    country: toText(
      firstDefined(
        item.country,
        item.country_name,
        item.location?.country
      ),
      ""
    ),

    country_code: toText(
      firstDefined(
        item.country_code,
        item.countryCode
      ),
      ""
    ),

    latitude,

    longitude,

    display_name: toText(
      firstDefined(
        item.display_name,
        item.displayName,
        item.name,
        item.city
      ),
      "Selected Location"
    ),
  };
}

export async function searchLocations(
  place
) {
  const response =
    await api.get(
      "/location/search",
      {
        params: {
          place,
        },
      }
    );

  const data =
    response.data;

  let items = [];

  if (Array.isArray(data)) {
    items = data;
  } else if (
    Array.isArray(data?.results)
  ) {
    items = data.results;
  } else if (
    Array.isArray(data?.locations)
  ) {
    items = data.locations;
  } else if (
    Array.isArray(data?.data)
  ) {
    items = data.data;
  } else if (
    data &&
    typeof data === "object"
  ) {
    items = [data];
  }

  return items
    .map(normalizeLocation)
    .filter(Boolean);
}

/* =====================================================
   FARM DATA
===================================================== */

export function normalizeFarmData(
  data
) {
  const weather =
    data?.weather ||
    data?.current_weather ||
    data?.current ||
    {};

  const soil =
    data?.soil ||
    data?.soil_data ||
    {};

  const climate =
    data?.climate ||
    data?.historical ||
    {};

  const location =
    data?.location ||
    {};

  return {
    temperature:
      toNumber(
        firstDefined(
          data?.temperature,
          weather?.temperature,
          weather?.temp,
          weather?.current?.temperature
        )
      ),

    humidity:
      toNumber(
        firstDefined(
          data?.humidity,
          weather?.humidity,
          weather?.relative_humidity,
          weather?.current?.humidity
        )
      ),

    rain:
      toNumber(
        firstDefined(
          data?.rain,
          data?.rainfall,
          weather?.rain,
          weather?.precipitation,
          weather?.precipitation_sum
        )
      ),

    precipitation:
      toNumber(
        firstDefined(
          data?.precipitation,
          weather?.precipitation,
          weather?.precipitation_sum
        )
      ),

    wind_speed:
      toNumber(
        firstDefined(
          data?.wind_speed,
          weather?.wind_speed,
          weather?.windSpeed
        )
      ),

    forecast_24h_rain:
      toNumber(
        firstDefined(
          data?.forecast_24h_rain,
          weather?.forecast_24h_rain,
          weather?.rain_24h
        )
      ),

    forecast_24h_precipitation:
      toNumber(
        firstDefined(
          data?.forecast_24h_precipitation,
          weather?.forecast_24h_precipitation
        )
      ),

    soil_moisture:
      toNumber(
        firstDefined(
          data?.soil_moisture,
          soil?.soil_moisture,
          soil?.moisture,
          weather?.soil_moisture
        )
      ),

    soil_temperature:
      toNumber(
        firstDefined(
          data?.soil_temperature,
          soil?.soil_temperature,
          soil?.temperature,
          weather?.soil_temperature
        )
      ),

    timezone: toText(
      firstDefined(
        data?.timezone,
        weather?.timezone
      ),
      ""
    ),

    annual_rainfall:
      toNumber(
        firstDefined(
          data?.annual_rainfall,
          climate?.annual_rainfall,
          climate?.annualRainfall,
          data?.rainfall?.annual_rainfall,
          data?.rainfall?.annual
        )
      ),

    rainfall_year:
      firstDefined(
        data?.rainfall_year,
        climate?.year,
        data?.year
      ),

    // New block exposed by the fast /farm-data endpoint.
    performance:
      data?.performance || null,

    location,

    raw: data,
  };
}

export async function getFarmData(
  latitude,
  longitude,
  signal
) {
  const response =
    await api.get(
      "/farm-data",
      {
        params: {
          latitude,
          longitude,
        },
        signal,
      }
    );

  return normalizeFarmData(
    response.data
  );
}

/* =====================================================
   CROP PREDICTION
===================================================== */

export function normalizeCropResult(
  data
) {
  const result =
    data?.result ||
    data?.prediction ||
    data?.data ||
    data;

  const crop =
    firstDefined(
      result?.crop,
      result?.predicted_crop,
      result?.predictedCrop,
      data?.crop,
      data?.predicted_crop
    );

  const probabilities =
    result?.probabilities ||
    data?.probabilities ||
    {};

  return {
    success:
      data?.success !== false,

    crop: toText(
      crop,
      ""
    ),

    state: toText(
      firstDefined(
        result?.state,
        data?.state
      ),
      ""
    ),

    season: toText(
      firstDefined(
        result?.season,
        data?.season
      ),
      ""
    ),

    year:
      toNumber(
        firstDefined(
          result?.year,
          data?.year
        )
      ),

    annual_rainfall:
      toNumber(
        firstDefined(
          result?.annual_rainfall,
          data?.annual_rainfall
        )
      ),

    model: toText(
      firstDefined(
        result?.model,
        data?.model
      ),
      "Random Forest"
    ),

    probabilities:
      probabilities &&
      typeof probabilities === "object"
        ? probabilities
        : {},

    raw: data,
  };
}

export async function getCropPrediction(
  latitude,
  longitude,
  crop,
  signal
) {
  const params = {
    latitude,
    longitude,
  };

  if (crop) {
    params.crop =
      String(crop);
  }

  const response =
    await api.get(
      "/predict/crop",
      {
        params,
        signal,
      }
    );

  return normalizeCropResult(
    response.data
  );
}

/* =====================================================
   YIELD PREDICTION
===================================================== */

export function normalizeYieldResult(
  data
) {
  const result =
    data?.result ||
    data?.prediction ||
    data?.data ||
    data;

  const predictedYield =
    firstDefined(
      result?.predicted_yield,
      result?.predictedYield,
      result?.yield,
      data?.predicted_yield,
      data?.predictedYield
    );

  return {
    success:
      data?.success !== false,

    crop: toText(
      firstDefined(
        result?.crop,
        data?.crop
      ),
      ""
    ),

    state: toText(
      firstDefined(
        result?.state,
        data?.state
      ),
      ""
    ),

    season: toText(
      firstDefined(
        result?.season,
        data?.season
      ),
      ""
    ),

    year:
      toNumber(
        firstDefined(
          result?.year,
          data?.year
        )
      ),

    annual_rainfall:
      toNumber(
        firstDefined(
          result?.annual_rainfall,
          data?.annual_rainfall
        )
      ),

    predicted_yield:
      toNumber(
        predictedYield
      ),

    unit: toText(
      firstDefined(
        result?.unit,
        data?.unit
      ),
      "dataset yield units"
    ),

    model: toText(
      firstDefined(
        result?.model,
        data?.model
      ),
      "Random Forest"
    ),

    raw: data,
  };
}

export async function getYieldPrediction(
  latitude,
  longitude,
  crop,
  signal
) {
  const response =
    await api.get(
      "/predict/yield",
      {
        params: {
          latitude,
          longitude,
          crop: String(crop),
        },
        signal,
      }
    );

  return normalizeYieldResult(
    response.data
  );
}

/* =====================================================
   FERTILIZER
===================================================== */

export function normalizeFertilizerResult(
  data
) {
  const result =
    data?.result ||
    data?.recommendation ||
    data?.data ||
    data;

  let fertilizerFocus =
    firstDefined(
      result?.fertilizer_focus,
      data?.fertilizer_focus
    );

  if (!Array.isArray(
    fertilizerFocus
  )) {
    fertilizerFocus = [];
  }

  return {
    success:
      data?.success !== false,

    crop: toText(
      firstDefined(
        result?.crop,
        data?.crop
      ),
      ""
    ),

    state: toText(
      firstDefined(
        result?.state,
        data?.state
      ),
      ""
    ),

    primary_nutrient_focus:
      toText(
        firstDefined(
          result?.primary_nutrient_focus,
          result?.primary_nutrient,
          data?.primary_nutrient_focus,
          data?.primary_nutrient
        ),
        ""
      ),

    fertilizer_focus:
      fertilizerFocus
        .map((item) => {
          if (
            typeof item === "string"
          ) {
            return item;
          }

          return (
            item?.name ||
            item?.fertilizer ||
            ""
          );
        })
        .filter(Boolean),

    guidance: toText(
      firstDefined(
        result?.guidance,
        data?.guidance
      ),
      ""
    ),

    recommendation_type:
      toText(
        firstDefined(
          result?.recommendation_type,
          data?.recommendation_type
        ),
        "Crop-level guidance"
      ),

    notice: toText(
      firstDefined(
        result?.notice,
        data?.notice
      ),
      ""
    ),

    raw: data,
  };
}

export async function getFertilizerRecommendation(
  latitude,
  longitude,
  crop,
  signal
) {
  const response =
    await api.get(
      "/predict/fertilizer",
      {
        params: {
          latitude,
          longitude,
          crop: String(crop),
        },
        signal,
      }
    );

  return normalizeFertilizerResult(
    response.data
  );
}

/* =====================================================
   HISTORY
===================================================== */

export async function saveHistory(
  userId,
  latitude,
  longitude,
  values
) {
  const predictedCrop =
    typeof values?.predicted_crop ===
    "string"
      ? values.predicted_crop
      : "";

  const predictedYield =
    toNumber(
      values?.predicted_yield
    );

  /*
    IMPORTANT:
    FastAPI expects this as STRING.
    Never send the complete fertilizer object.
  */

  const fertilizerRecommendation =
    typeof values
      ?.fertilizer_recommendation ===
    "string"
      ? values.fertilizer_recommendation
      : "";

  const params = {
    user_id: Number(userId),

    latitude: Number(latitude),

    longitude: Number(longitude),
  };

  if (predictedCrop) {
    params.predicted_crop =
      predictedCrop;
  }

  if (
    predictedYield !== null
  ) {
    params.predicted_yield =
      predictedYield;
  }

  if (
    fertilizerRecommendation
  ) {
    params.fertilizer_recommendation =
      fertilizerRecommendation;
  }

  const response =
    await api.post(
      "/history",
      null,
      {
        params,
      }
    );

  return response.data;
}

export function normalizeHistoryRecord(
  item
) {
  return {
    id: item?.id,

    location: toText(
      item?.location,
      "Unknown location"
    ),

    state: toText(
      item?.state,
      ""
    ),

    country: toText(
      item?.country,
      ""
    ),

    latitude:
      toNumber(
        item?.latitude
      ),

    longitude:
      toNumber(
        item?.longitude
      ),

    predicted_crop:
      toText(
        item?.predicted_crop,
        ""
      ),

    predicted_yield:
      toNumber(
        item?.predicted_yield
      ),

    yield_unit:
      toText(
        item?.yield_unit,
        "dataset yield units"
      ),

    fertilizer_recommendation:
      toText(
        item?.fertilizer_recommendation,
        ""
      ),

    annual_rainfall:
      toNumber(
        item?.annual_rainfall
      ),

    temperature:
      toNumber(
        item?.temperature
      ),

    humidity:
      toNumber(
        item?.humidity
      ),

    rain:
      toNumber(
        item?.rain
      ),

    soil_moisture:
      toNumber(
        item?.soil_moisture
      ),

    soil_temperature:
      toNumber(
        item?.soil_temperature
      ),

    season:
      toText(
        item?.season,
        ""
      ),

    prediction_year:
      toNumber(
        item?.prediction_year
      ),

    created_at:
      item?.created_at || null,
  };
}

export async function getHistory(
  userId,
  limit = 50
) {
  const response =
    await api.get(
      "/history",
      {
        params: {
          user_id: Number(userId),
          limit,
        },
      }
    );

  const data =
    response.data;

  let records = [];

  if (Array.isArray(data)) {
    records = data;
  } else if (
    Array.isArray(data?.history)
  ) {
    records =
      data.history;
  } else if (
    Array.isArray(data?.results)
  ) {
    records =
      data.results;
  } else if (
    Array.isArray(data?.data)
  ) {
    records =
      data.data;
  }

  return records.map(
    normalizeHistoryRecord
  );
}