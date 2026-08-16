export function getErrorMessage(error, fallback = "Something went wrong. Please try again.") {
  if (error?.response?.data?.error) return error.response.data.error;
  if (error?.response?.data?.detail) return error.response.data.detail;
  if (error?.code === "ECONNABORTED") return "The request timed out. Please try again.";
  if (!error?.response) return "Unable to reach the server. Please check your connection.";
  return fallback;
}
