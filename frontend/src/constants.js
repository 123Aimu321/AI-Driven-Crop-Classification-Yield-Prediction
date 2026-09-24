export const AUTH_KEY = "crop_ai_user";

export const LOCATION_KEY =
  "crop_ai_location";

export const CROP_KEY =
  "crop_ai_selected_crop";

export const CROP_OPTIONS = [
  "Wheat",
  "Rice",
  "Ragi",
];

export function getStoredUser() {
  try {
    const raw =
      localStorage.getItem(AUTH_KEY);

    if (!raw) {
      return null;
    }

    const user = JSON.parse(raw);

    if (!user || !user.id) {
      return null;
    }

    return user;
  } catch {
    return null;
  }
}

export function getStoredLocation() {
  try {
    const raw =
      localStorage.getItem(
        LOCATION_KEY
      );

    if (!raw) {
      return null;
    }

    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function getStoredCrop() {
  const crop =
    localStorage.getItem(CROP_KEY);

  if (
    crop &&
    CROP_OPTIONS.includes(crop)
  ) {
    return crop;
  }

  return "Rice";
}

export function normalizeCrop(value) {
  if (typeof value === "string") {
    return value;
  }

  if (value?.crop) {
    return value.crop;
  }

  if (value?.predicted_crop) {
    return value.predicted_crop;
  }

  if (value?.prediction?.crop) {
    return value.prediction.crop;
  }

  return "";
}

export function isValidCoordinates(
  latitude,
  longitude
) {
  const lat = Number(latitude);
  const lon = Number(longitude);

  return (
    Number.isFinite(lat) &&
    Number.isFinite(lon) &&
    lat >= -90 &&
    lat <= 90 &&
    lon >= -180 &&
    lon <= 180
  );
}

export function formatNumber(
  value,
  digits = 2
) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "Not available";
  }

  return number.toFixed(digits);
}

export function displayValue(
  value,
  fallback = "Not available"
) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return fallback;
  }

  return String(value);
}