import React from "react";

export default function ResultCard({
  icon,
  title,
  value,
  label,
  className = "",
}) {
  return (
    <div
      className={`result-card ${className}`}
    >
      <div className="result-icon">
        {icon}
      </div>

      <div className="result-content">
        <span className="result-label">
          {label}
        </span>

        <strong className="result-value">
          {value}
        </strong>

        {title && (
          <span className="result-title">
            {title}
          </span>
        )}
      </div>
    </div>
  );
}