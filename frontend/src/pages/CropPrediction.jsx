import React, {
  useEffect,
  useState,
} from "react";

import {
  Link,
} from "react-router-dom";

import Header from "../components/Header";
import Loading from "../components/Loading";

import {
  CROP_KEY,
  LOCATION_KEY,
  getStoredCrop,
} from "../constants";

import {
  getCropPrediction,
  getErrorMessage,
  getFarmData,
} from "../services/api";

export default function CropPrediction() {
  const [location, setLocation] =
    useState(null);

  const [selectedCrop, setSelectedCrop] =
    useState(
      getStoredCrop()
    );

  const [farmData, setFarmData] =
    useState(null);

  const [result, setResult] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    async function load() {
      try {
        const saved =
          localStorage.getItem(
            LOCATION_KEY
          );

        if (!saved) {
          setError(
            "Please select a location from the Dashboard first."
          );

          setLoading(false);
          return;
        }

        const savedLocation =
          JSON.parse(saved);

        setLocation(
          savedLocation
        );

        const latitude =
          Number(
            savedLocation.latitude
          );

        const longitude =
          Number(
            savedLocation.longitude
          );

        const farm =
          await getFarmData(
            latitude,
            longitude
          );

        setFarmData(farm);

        const crop =
          await getCropPrediction(
            latitude,
            longitude,
            selectedCrop
          );

        setResult(crop);
      } catch (err) {
        setError(
          getErrorMessage(
            err,
            "Could not load crop prediction."
          )
        );
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [selectedCrop]);

  if (loading) {
    return (
      <div className="app-shell">
        <Header />

        <main className="page-container">
          <Loading message="Loading crop classification..." />
        </main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Header />

      <main className="page-container">
        <section className="page-hero">
          <p className="eyebrow">
            MACHINE LEARNING
          </p>

          <h1>
            Crop Classification
          </h1>

          <p>
            AI-based classification using
            location, season and annual
            rainfall information.
          </p>
        </section>

        {error && (
          <div className="error-box">
            {error}

            <Link
              to="/dashboard"
              className="inline-link"
            >
              Go to Dashboard
            </Link>
          </div>
        )}

        {result && (
          <>
            <section className="prediction-highlight">
              <div className="prediction-main">
                <p className="eyebrow">
                  MODEL RESULT
                </p>

                <h2>
                  {result.crop ||
                    selectedCrop}
                </h2>

                <p>
                  The current model classified
                  the selected location as this
                  crop.
                </p>
              </div>

              <div className="prediction-badge">
                🌱
              </div>
            </section>

            <section className="result-grid">
              <div className="detail-card">
                <span>
                  📍 State
                </span>

                <strong>
                  {result.state ||
                    location?.state ||
                    "Detected automatically"}
                </strong>
              </div>

              <div className="detail-card">
                <span>
                  🌦️ Season
                </span>

                <strong>
                  {result.season ||
                    "Automatic"}
                </strong>
              </div>

              <div className="detail-card">
                <span>
                  📅 Prediction year
                </span>

                <strong>
                  {result.year ||
                    new Date().getFullYear()}
                </strong>
              </div>

              <div className="detail-card">
                <span>
                  🌧️ Annual rainfall
                </span>

                <strong>
                  {result.annual_rainfall !==
                  null
                    ? `${result.annual_rainfall} mm`
                    : farmData?.annual_rainfall !==
                      null
                    ? `${farmData.annual_rainfall} mm`
                    : "Not available"}
                </strong>
              </div>

              <div className="detail-card">
                <span>
                  🤖 Model
                </span>

                <strong>
                  {result.model}
                </strong>
              </div>

              <div className="detail-card">
                <span>
                  🌾 Selected crop
                </span>

                <strong>
                  {selectedCrop}
                </strong>
              </div>
            </section>

            {Object.keys(
              result.probabilities || {}
            ).length > 0 && (
              <section className="content-card">
                <div className="section-heading">
                  <span className="section-icon">
                    📊
                  </span>

                  <div>
                    <h2>
                      Model probabilities
                    </h2>

                    <p>
                      Probability values returned
                      by the classification model.
                    </p>
                  </div>
                </div>

                <div className="probability-list">
                  {Object.entries(
                    result.probabilities
                  ).map(
                    ([
                      crop,
                      probability,
                    ]) => (
                      <div
                        className="probability-row"
                        key={crop}
                      >
                        <div className="probability-header">
                          <strong>
                            {crop}
                          </strong>

                          <span>
                            {probability}%
                          </span>
                        </div>

                        <div className="progress-track">
                          <div
                            className="progress-fill"
                            style={{
                              width: `${Math.min(
                                100,
                                Number(
                                  probability
                                ) || 0
                              )}%`,
                            }}
                          />
                        </div>
                      </div>
                    )
                  )}
                </div>
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
}