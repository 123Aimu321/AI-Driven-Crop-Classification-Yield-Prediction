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
  getFertilizerRecommendation,
} from "../services/api";

const MANUAL_FERTILIZER_GUIDANCE = {
  Wheat: {
    title:
      "Wheat fertilizer reference",

    nutrients: [
      {
        name: "Nitrogen",
        role:
          "Supports vegetative growth and leaf development.",
        examples:
          "Urea or other nitrogen-containing fertilizers",
      },

      {
        name: "Phosphorus",
        role:
          "Supports root development and early crop establishment.",
        examples:
          "DAP or SSP",
      },

      {
        name: "Potassium",
        role:
          "Supports overall crop strength and nutrient balance.",
        examples:
          "MOP or another potassium source",
      },
    ],

    practice:
      "Nitrogen is commonly managed in split applications during crop growth. The actual schedule depends on soil test results, variety, season and irrigation conditions.",
  },

  Rice: {
    title:
      "Rice fertilizer reference",

    nutrients: [
      {
        name: "Nitrogen",
        role:
          "Important for vegetative growth and crop development.",
        examples:
          "Urea or another nitrogen-containing fertilizer",
      },

      {
        name: "Phosphorus",
        role:
          "Supports root development and crop establishment.",
        examples:
          "DAP or SSP",
      },

      {
        name: "Potassium",
        role:
          "Supports crop strength and nutrient balance.",
        examples:
          "MOP or another potassium source",
      },
    ],

    practice:
      "Nitrogen is commonly split across crop-growth stages. Phosphorus and potassium management depends on soil status and the production system.",
  },

  Ragi: {
    title:
      "Ragi fertilizer reference",

    nutrients: [
      {
        name: "Nitrogen",
        role:
          "Supports vegetative growth and biomass development.",
        examples:
          "Urea or another nitrogen-containing fertilizer",
      },

      {
        name: "Phosphorus",
        role:
          "Important for root development and establishment.",
        examples:
          "DAP or SSP",
      },

      {
        name: "Potassium",
        role:
          "Supports overall crop development and nutrient balance.",
        examples:
          "MOP or another potassium source",
      },
    ],

    practice:
      "Balanced N, P and K management is generally used. The exact nutrient requirement should be adjusted according to soil testing and local crop recommendations.",
  },
};

export default function Fertilizer() {
  const [location, setLocation] =
    useState(null);

  const [selectedCrop] =
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
          await getFertilizerRecommendation(
            Number(
              savedLocation.latitude
            ),
            Number(
              savedLocation.longitude
            ),
            selectedCrop
          );

        setResult(response);
      } catch (err) {
        setError(
          getErrorMessage(
            err,
            "Could not load fertilizer guidance."
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
          <Loading message="Loading fertilizer guidance..." />
        </main>
      </div>
    );
  }

  const crop =
    result?.crop ||
    selectedCrop;

  const manual =
    MANUAL_FERTILIZER_GUIDANCE[
      crop
    ] ||
    MANUAL_FERTILIZER_GUIDANCE[
      selectedCrop
    ];

  return (
    <div className="app-shell">
      <Header />

      <main className="page-container">
        <section className="page-hero">
          <p className="eyebrow">
            CROP NUTRIENT GUIDANCE
          </p>

          <h1>
            Fertilizer Guidance
          </h1>

          <p>
            General nutrient guidance for
            the selected crop, combined with
            the system's crop-level recommendation.
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
            <section className="fertilizer-summary">
              <div className="fertilizer-summary-icon">
                🧪
              </div>

              <div>
                <p className="eyebrow">
                  CURRENT CROP
                </p>

                <h2>
                  {crop}
                </h2>

                <p>
                  Location:{" "}
                  {result.state ||
                    location?.state ||
                    "Detected automatically"}
                </p>
              </div>

              <div className="primary-nutrient">
                <span>
                  Primary nutrient focus
                </span>

                <strong>
                  {result.primary_nutrient_focus ||
                    "Balanced NPK management"}
                </strong>
              </div>
            </section>

            <section className="content-card">
              <div className="section-heading">
                <span className="section-icon">
                  🌱
                </span>

                <div>
                  <h2>
                    AI fertilizer guidance
                  </h2>

                  <p>
                    Crop-level guidance returned
                    by the backend.
                  </p>
                </div>
              </div>

              <div className="guidance-grid">
                <div className="guidance-box">
                  <span>
                    Primary nutrient
                  </span>

                  <strong>
                    {result.primary_nutrient_focus ||
                      "Balanced NPK management"}
                  </strong>
                </div>

                <div className="guidance-box">
                  <span>
                    Recommendation type
                  </span>

                  <strong>
                    {result.recommendation_type ||
                      "Crop-level guidance"}
                  </strong>
                </div>
              </div>

              <div className="guidance-text">
                <h3>
                  Guidance
                </h3>

                <p>
                  {result.guidance ||
                    "Balanced nutrient management is recommended based on crop requirements."}
                </p>
              </div>

              <div className="fertilizer-focus-list">
                <h3>
                  Fertilizer categories
                </h3>

                {result.fertilizer_focus?.length >
                0 ? (
                  result.fertilizer_focus.map(
                    (item, index) => (
                      <div
                        className="fertilizer-item"
                        key={`${item}-${index}`}
                      >
                        <span>
                          ✓
                        </span>

                        <strong>
                          {item}
                        </strong>
                      </div>
                    )
                  )
                ) : (
                  <p>
                    Balanced nitrogen,
                    phosphorus and potassium
                    management.
                  </p>
                )}
              </div>
            </section>

            <section className="content-card">
              <div className="section-heading">
                <span className="section-icon">
                  📚
                </span>

                <div>
                  <h2>
                    Manual fertilizer reference
                  </h2>

                  <p>
                    General information to
                    understand the role of
                    common fertilizer nutrients.
                  </p>
                </div>
              </div>

              <div className="nutrient-grid">
                {manual?.nutrients?.map(
                  (nutrient) => (
                    <article
                      className="nutrient-card"
                      key={nutrient.name}
                    >
                      <div className="nutrient-icon">
                        {nutrient.name ===
                        "Nitrogen"
                          ? "N"
                          : nutrient.name ===
                            "Phosphorus"
                          ? "P"
                          : "K"}
                      </div>

                      <h3>
                        {nutrient.name}
                      </h3>

                      <p>
                        {nutrient.role}
                      </p>

                      <small>
                        Common examples:
                        {" "}
                        {nutrient.examples}
                      </small>
                    </article>
                  )
                )}
              </div>

              <div className="practice-box">
                <strong>
                  General practice
                </strong>

                <p>
                  {manual?.practice}
                </p>
              </div>
            </section>

            <section className="important-notice">
              <div className="notice-icon">
                ⚠
              </div>

              <div>
                <strong>
                  Fertilizer dosage notice
                </strong>

                <p>
                  Exact fertilizer dosage is
                  not calculated because
                  automatic soil N, P, K and
                  pH measurements are not
                  available. Use a soil test
                  and local agronomic advice
                  before applying fertilizer.
                </p>
              </div>
            </section>

            {result.notice && (
              <section className="content-card">
                <div className="section-heading">
                  <span className="section-icon">
                    ℹ️
                  </span>

                  <div>
                    <h2>
                      System notice
                    </h2>

                    <p>
                      Additional information
                      from the recommendation
                      service.
                    </p>
                  </div>
                </div>

                <p className="notice-text">
                  {result.notice}
                </p>
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
}