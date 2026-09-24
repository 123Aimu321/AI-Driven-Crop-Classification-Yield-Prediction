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
  getStoredUser,
} from "../constants";

import {
  getErrorMessage,
  getHistory,
} from "../services/api";

export default function History() {
  const user =
    getStoredUser();

  const [history, setHistory] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    async function loadHistory() {
      if (!user?.id) {
        setError(
          "User session not found."
        );

        setLoading(false);
        return;
      }

      try {
        const records =
          await getHistory(
            user.id,
            50
          );

        setHistory(records);
      } catch (err) {
        setError(
          getErrorMessage(
            err,
            "Could not load prediction history."
          )
        );
      } finally {
        setLoading(false);
      }
    }

    loadHistory();
  }, [user?.id]);

  function formatDate(
    value
  ) {
    if (!value) {
      return "Date unavailable";
    }

    const date =
      new Date(value);

    if (
      Number.isNaN(
        date.getTime()
      )
    ) {
      return String(value);
    }

    return date.toLocaleString();
  }

  if (loading) {
    return (
      <div className="app-shell">
        <Header />

        <main className="page-container">
          <Loading message="Loading prediction history..." />
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
            SAVED PREDICTIONS
          </p>

          <h1>
            Prediction History
          </h1>

          <p>
            Review your previous crop,
            yield and fertilizer analyses.
          </p>
        </section>

        {error && (
          <div className="error-box">
            {error}
          </div>
        )}

        {!error &&
          history.length === 0 && (
            <section className="empty-state">
              <div>
                🕘
              </div>

              <h2>
                No predictions yet
              </h2>

              <p>
                Run an AI analysis from the
                Dashboard and your result
                will appear here.
              </p>

              <Link
                to="/dashboard"
                className="primary-button"
              >
                Go to Dashboard
              </Link>
            </section>
          )}

        <div className="history-list">
          {history.map(
            (item, index) => (
              <article
                className="history-card"
                key={
                  item.id ||
                  `${item.created_at}-${index}`
                }
              >
                <div className="history-header">
                  <div>
                    <div className="history-location">
                      📍{" "}
                      {item.location}
                    </div>

                    <div className="history-date">
                      {formatDate(
                        item.created_at
                      )}
                    </div>
                  </div>

                  <div className="history-crop">
                    🌱{" "}
                    {item.predicted_crop ||
                      "Crop not recorded"}
                  </div>
                </div>

                <div className="history-grid">
                  <div>
                    <span>
                      State
                    </span>

                    <strong>
                      {item.state ||
                        "Not recorded"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Yield
                    </span>

                    <strong>
                      {item.predicted_yield !==
                      null
                        ? `${item.predicted_yield} ${
                            item.yield_unit ||
                            ""
                          }`
                        : "Not recorded"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Rainfall
                    </span>

                    <strong>
                      {item.annual_rainfall !==
                      null
                        ? `${item.annual_rainfall} mm`
                        : "Not recorded"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Temperature
                    </span>

                    <strong>
                      {item.temperature !==
                      null
                        ? `${item.temperature} °C`
                        : "Not recorded"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Humidity
                    </span>

                    <strong>
                      {item.humidity !==
                      null
                        ? `${item.humidity} %`
                        : "Not recorded"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Rain
                    </span>

                    <strong>
                      {item.rain !==
                      null
                        ? `${item.rain} mm`
                        : "Not recorded"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Soil moisture
                    </span>

                    <strong>
                      {item.soil_moisture !==
                      null
                        ? item.soil_moisture
                        : "Not recorded"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Soil temperature
                    </span>

                    <strong>
                      {item.soil_temperature !==
                      null
                        ? `${item.soil_temperature} °C`
                        : "Not recorded"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Season
                    </span>

                    <strong>
                      {item.season ||
                        "Not recorded"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Prediction year
                    </span>

                    <strong>
                      {item.prediction_year ||
                        "Not recorded"}
                    </strong>
                  </div>

                  <div className="history-fertilizer">
                    <span>
                      Fertilizer focus
                    </span>

                    <strong>
                      {item.fertilizer_recommendation ||
                        "Not recorded"}
                    </strong>
                  </div>
                </div>
              </article>
            )
          )}
        </div>
      </main>
    </div>
  );
}