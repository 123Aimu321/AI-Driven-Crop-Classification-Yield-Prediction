import React from "react";

export default function Loading({
  message = "Loading..."
}) {
  return (
    <div className="loading-state">
      <div className="loading-spinner" />

      <p>{message}</p>
    </div>
  );
}