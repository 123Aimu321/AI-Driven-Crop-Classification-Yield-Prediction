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
  LOCATION_KEY,
  getStoredCrop,
} from "../constants";

import {
  getErrorMessage,
  getYieldPrediction,
} from "../services/api";

export default function YieldPrediction() {
  const [location, setLocation] =
    useState(null);

  const [crop, setCrop] =
    useState(
      getStoredCrop()
    );

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

          return;
        }

        const savedLocation =
          JSON.parse(saved);

        setLocation(
          savedLocation
        );

        const response =
          await getYieldPrediction(
            Number(
              savedLocation.latitude
            ),
            Number(
              savedLocation.longitude
            ),
            crop
          );

        setResult(response);
      } catch (err) {
        setError(
          getErrorMessage(
            err,
            "Could not load yield prediction."
          )
        );
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [crop]);

  if (loading) {
    return (
      <div className="app-shell">
        <Header />

        <main className="page-container">
          <Loading message="Calculating yield estimate..." />
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
            Yield Prediction
          </h1>

          <p>
            Estimated crop yield based on
            the trained Random Forest model.
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
            <section className="yield-hero-card">
              <div>
                <p className="eyebrow">
                  PREDICTED YIELD
                </p>

                <div className="yield-number">
                  {result.predicted_yield !==
                  null
                    ? result.predicted_yield
                    : "—"}
                </div>

                <p>
                  {result.unit}
                </p>
              </div>

              <div className="yield-crop">
                🌾

                <strong>
                  {result.crop ||
                    crop}
                </strong>
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
                    "Not available"}
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
                  📅 Year
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
                    : "Not available"}
                </strong>
              </div>

              <div className="detail-card">
                <span>
                  🌱 Crop
                </span>

                <strong>
                  {result.crop ||
                    crop}
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
            </section>

            <section className="content-card information-card">
              <div className="section-heading">
                <span className="section-icon">
                  ℹ️
                </span>

                <div>
                  <h2>
                    About this estimate
                  </h2>

                  <p>
                    This is a machine-learning
                    estimate based on the data
                    available to the model.
                  </p>
                </div>
              </div>

              <div className="notice-box">
                Predicted yield is an estimate
                and actual production can vary
                because of soil conditions,
                irrigation, weather, farming
                practices, variety and other
                factors.
              </div>

              <p className="small-note">
                Unit:
                {" "}
                {result.unit}.
                The project currently reports
                the dataset's yield units and
                does not assume a real-world unit
                that has not been established.
              </p>
            </section>
          </>
        )}
      </main>
    </div>
  );
}