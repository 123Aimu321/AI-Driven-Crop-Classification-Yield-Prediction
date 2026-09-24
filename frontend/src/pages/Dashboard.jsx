import React, {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  Link,
} from "react-router-dom";

import Header from "../components/Header";
import Loading from "../components/Loading";
import ResultCard from "../components/ResultCard";

import {
  CROP_KEY,
  CROP_OPTIONS,
  LOCATION_KEY,
  getStoredUser,
  isValidCoordinates,
} from "../constants";

import {
  getCropPrediction,
  getErrorMessage,
  getFarmData,
  getFertilizerRecommendation,
  getYieldPrediction,
  saveHistory,
  searchLocations,
} from "../services/api";

export default function Dashboard() {
  const user =
    getStoredUser();

  const [search, setSearch] =
    useState("Bengaluru");

  const [locations, setLocations] =
    useState([]);

  const [selectedLocation, setSelectedLocation] =
    useState(null);

  const [selectedCrop, setSelectedCrop] =
    useState(
      localStorage.getItem(
        CROP_KEY
      ) || "Rice"
    );

  const [farmData, setFarmData] =
    useState(null);

  const [cropResult, setCropResult] =
    useState(null);

  const [yieldResult, setYieldResult] =
    useState(null);

  const [fertilizerResult, setFertilizerResult] =
    useState(null);

  const [searching, setSearching] =
    useState(false);

  const [analyzing, setAnalyzing] =
    useState(false);

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");

  const saveKey =
    useRef("");

  useEffect(() => {
    const saved =
      localStorage.getItem(
        LOCATION_KEY
      );

    if (saved) {
      try {
        const location =
          JSON.parse(saved);

        if (
          isValidCoordinates(
            location?.latitude,
            location?.longitude
          )
        ) {
          setSelectedLocation(
            location
          );
        }
      } catch {
        localStorage.removeItem(
          LOCATION_KEY
        );
      }
    }
  }, []);

  async function handleSearch(
    event
  ) {
    event?.preventDefault();

    setError("");
    setMessage("");

    if (!search.trim()) {
      setError(
        "Enter a location to search."
      );

      return;
    }

    try {
      setSearching(true);

      const results =
        await searchLocations(
          search.trim()
        );

      if (!results.length) {
        setError(
          "No location with valid coordinates was found."
        );

        setLocations([]);

        return;
      }

      setLocations(results);
    } catch (err) {
      setError(
        getErrorMessage(
          err,
          "Could not search for the location."
        )
      );
    } finally {
      setSearching(false);
    }
  }

  function chooseLocation(
    location
  ) {
    if (
      !isValidCoordinates(
        location.latitude,
        location.longitude
      )
    ) {
      setError(
        "The selected location does not have valid coordinates."
      );

      return;
    }

    setSelectedLocation(
      location
    );

    localStorage.setItem(
      LOCATION_KEY,
      JSON.stringify(location)
    );

    setLocations([]);

    setMessage(
      `${location.name} selected successfully.`
    );

    setError("");
  }

  async function runAnalysis() {
    if (!selectedLocation) {
      setError(
        "Please select a location first."
      );

      return;
    }

    if (
      !isValidCoordinates(
        selectedLocation.latitude,
        selectedLocation.longitude
      )
    ) {
      setError(
        "Selected location does not have valid coordinates."
      );

      return;
    }

    if (!CROP_OPTIONS.includes(
      selectedCrop
    )) {
      setError(
        "Please select Wheat, Rice or Ragi."
      );

      return;
    }

    if (!user?.id) {
      setError(
        "Your login session is invalid. Please log in again."
      );

      return;
    }

    try {
      setAnalyzing(true);
      setError("");
      setMessage("");

      const latitude =
        Number(
          selectedLocation.latitude
        );

      const longitude =
        Number(
          selectedLocation.longitude
        );

      /*
        STEP 1
        Automatic environment data.
      */
      const farm =
        await getFarmData(
          latitude,
          longitude
        );

      setFarmData(farm);

      /*
        STEP 2
        AI crop classification.
      */
      const crop =
        await getCropPrediction(
          latitude,
          longitude,
          selectedCrop
        );

      setCropResult(crop);

      const predictedCrop =
        crop?.crop ||
        selectedCrop;

      /*
        STEP 3
        Yield prediction uses the
        predicted crop.
      */
      const yieldData =
        await getYieldPrediction(
          latitude,
          longitude,
          predictedCrop
        );

      setYieldResult(
        yieldData
      );

      /*
        STEP 4
        Fertilizer guidance uses
        the predicted crop.
      */
      const fertilizer =
        await getFertilizerRecommendation(
          latitude,
          longitude,
          predictedCrop
        );

      setFertilizerResult(
        fertilizer
      );

      /*
        STEP 5
        Save only strings/numbers.
      */
      const historyKey =
        [
          user.id,
          latitude,
          longitude,
          predictedCrop,
          yieldData?.predicted_yield,
          fertilizer?.primary_nutrient_focus,
        ].join("|");

      if (
        saveKey.current !==
        historyKey
      ) {
        saveKey.current =
          historyKey;

        await saveHistory(
          user.id,
          latitude,
          longitude,
          {
            predicted_crop:
              predictedCrop,

            predicted_yield:
              yieldData?.predicted_yield,

            fertilizer_recommendation:
              fertilizer?.primary_nutrient_focus ||
              "",
          }
        );
      }

      setMessage(
        "Analysis completed and prediction saved to history."
      );
    } catch (err) {
      setError(
        getErrorMessage(
          err,
          "Could not complete the analysis."
        )
      );
    } finally {
      setAnalyzing(false);
    }
  }

  const displayCrop =
    cropResult?.crop ||
    selectedCrop;

  return (
    <div className="app-shell">
      <Header />

      <main className="page-container">
        <section className="dashboard-hero">
          <div>
            <p className="eyebrow">
              AI AGRICULTURE INTELLIGENCE
            </p>

            <h1>
              AI Driven Crop
              <span>
                Classification &
                Yield Prediction
              </span>
            </h1>

            <p className="hero-text">
              Select a location and crop.
              The system automatically
              collects environmental data,
              predicts the crop, estimates
              yield and provides fertilizer
              guidance.
            </p>
          </div>

          <div className="hero-orbit">
            <div className="orbit-center">
              🌱
            </div>

            <div className="orbit-item orbit-one">
              ☁️
            </div>

            <div className="orbit-item orbit-two">
              🌾
            </div>

            <div className="orbit-item orbit-three">
              💧
            </div>
          </div>
        </section>

        {error && (
          <div className="error-box page-message">
            {error}
          </div>
        )}

        {message && (
          <div className="success-box page-message">
            {message}
          </div>
        )}

        <section className="control-panel">
          <div className="section-heading">
            <span className="section-icon">
              📍
            </span>

            <div>
              <h2>
                Farm location
              </h2>

              <p>
                Search and select the
                location you want to analyze.
              </p>
            </div>
          </div>

          <form
            className="location-search"
            onSubmit={
              handleSearch
            }
          >
            <input
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value
                )
              }
              placeholder="Search Bengaluru, Shivamogga..."
            />

            <button
              className="secondary-button"
              disabled={searching}
            >
              {searching
                ? "Searching..."
                : "Search"}
            </button>
          </form>

          {locations.length > 0 && (
            <div className="location-results">
              {locations.map(
                (location, index) => (
                  <button
                    key={`${location.latitude}-${location.longitude}-${index}`}
                    className="location-result"
                    onClick={() =>
                      chooseLocation(
                        location
                      )
                    }
                  >
                    <span className="location-result-icon">
                      📍
                    </span>

                    <span>
                      <strong>
                        {location.name}
                      </strong>

                      <small>
                        {location.state
                          ? `${location.state}, `
                          : ""}
                        {location.country}
                      </small>
                    </span>
                  </button>
                )
              )}
            </div>
          )}

          {selectedLocation && (
            <div className="selected-location">
              <div>
                <span>
                  Selected location
                </span>

                <strong>
                  {selectedLocation.name}
                </strong>
              </div>

              <div>
                <span>
                  Coordinates
                </span>

                <strong>
                  {Number(
                    selectedLocation.latitude
                  ).toFixed(4)}
                  ,{" "}
                  {Number(
                    selectedLocation.longitude
                  ).toFixed(4)}
                </strong>
              </div>

              <div>
                <span>
                  State
                </span>

                <strong>
                  {selectedLocation.state ||
                    "Detected automatically"}
                </strong>
              </div>
            </div>
          )}
        </section>

        <section className="control-panel">
          <div className="section-heading">
            <span className="section-icon">
              🌾
            </span>

            <div>
              <h2>
                Crop selection
              </h2>

              <p>
                Choose one of the supported
                crops for the AI analysis.
              </p>
            </div>
          </div>

          <div className="crop-selector">
            {CROP_OPTIONS.map(
              (crop) => (
                <button
                  key={crop}
                  className={
                    selectedCrop === crop
                      ? "crop-option selected"
                      : "crop-option"
                  }
                  onClick={() => {
                    setSelectedCrop(
                      crop
                    );

                    localStorage.setItem(
                      CROP_KEY,
                      crop
                    );
                  }}
                >
                  <span>
                    {crop === "Wheat"
                      ? "🌾"
                      : crop === "Rice"
                      ? "🌱"
                      : "🌿"}
                  </span>

                  {crop}
                </button>
              )
            )}
          </div>

          <button
            className="primary-button analysis-button"
            onClick={
              runAnalysis
            }
            disabled={analyzing}
          >
            {analyzing
              ? "Running AI analysis..."
              : "Run AI Analysis"}
          </button>
        </section>

        {analyzing && (
          <Loading
            message="Collecting location, weather, climate and model predictions..."
          />
        )}

        {farmData && (
          <section className="section-block">
            <div className="section-heading">
              <span className="section-icon">
                🌤️
              </span>

              <div>
                <h2>
                  Automatic environment data
                </h2>

                <p>
                  Values collected from the
                  selected location.
                </p>
              </div>
            </div>

            <div className="result-grid">
              <ResultCard
                icon="🌡️"
                label="Temperature"
                value={
                  farmData.temperature !== null
                    ? `${farmData.temperature} °C`
                    : "Not available"
                }
              />

              <ResultCard
                icon="💧"
                label="Humidity"
                value={
                  farmData.humidity !== null
                    ? `${farmData.humidity} %`
                    : "Not available"
                }
              />

              <ResultCard
                icon="🌧️"
                label="Rain"
                value={
                  farmData.rain !== null
                    ? `${farmData.rain} mm`
                    : "Not available"
                }
              />

              <ResultCard
                icon="🌱"
                label="Soil moisture"
                value={
                  farmData.soil_moisture !== null
                    ? farmData.soil_moisture
                    : "Not available"
                }
              />

              <ResultCard
                icon="🌡️"
                label="Soil temperature"
                value={
                  farmData.soil_temperature !== null
                    ? `${farmData.soil_temperature} °C`
                    : "Not available"
                }
              />

              <ResultCard
                icon="🌦️"
                label="Annual rainfall"
                value={
                  farmData.annual_rainfall !== null
                    ? `${farmData.annual_rainfall} mm`
                    : "Not available"
                }
              />
            </div>
          </section>
        )}

        {cropResult && (
          <section className="prediction-highlight">
            <div className="prediction-main">
              <p className="eyebrow">
                AI CROP CLASSIFICATION
              </p>

              <h2>
                {displayCrop}
              </h2>

              <p>
                Predicted crop from the
                classification model.
              </p>
            </div>

            <div className="prediction-meta">
              <div>
                <span>
                  State
                </span>

                <strong>
                  {cropResult.state ||
                    selectedLocation?.state ||
                    "Not available"}
                </strong>
              </div>

              <div>
                <span>
                  Season
                </span>

                <strong>
                  {cropResult.season ||
                    "Automatic"}
                </strong>
              </div>

              <div>
                <span>
                  Year
                </span>

                <strong>
                  {cropResult.year ||
                    new Date().getFullYear()}
                </strong>
              </div>

              <div>
                <span>
                  Rainfall
                </span>

                <strong>
                  {cropResult.annual_rainfall !==
                  null
                    ? `${cropResult.annual_rainfall} mm`
                    : farmData?.annual_rainfall !==
                      null
                    ? `${farmData.annual_rainfall} mm`
                    : "Not available"}
                </strong>
              </div>
            </div>
          </section>
        )}

        <section className="quick-links">
          <Link to="/crop-prediction">
            <span>🌾</span>
            <strong>
              Crop prediction
            </strong>
            <small>
              View classification details
            </small>
          </Link>

          <Link to="/yield-prediction">
            <span>📈</span>
            <strong>
              Yield prediction
            </strong>
            <small>
              View estimated yield
            </small>
          </Link>

          <Link to="/fertilizer">
            <span>🧪</span>
            <strong>
              Fertilizer guidance
            </strong>
            <small>
              View crop nutrient guidance
            </small>
          </Link>

          <Link to="/history">
            <span>🕘</span>
            <strong>
              Prediction history
            </strong>
            <small>
              View saved analyses
            </small>
          </Link>
        </section>
      </main>
    </div>
  );
}