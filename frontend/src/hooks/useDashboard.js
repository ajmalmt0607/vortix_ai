import { useCallback, useEffect, useState } from "react";
import { fetchDashboard } from "../services/api";
import { getErrorMessage } from "../utils/errors";

export function useDashboard(params) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const paramsKey = JSON.stringify(params);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchDashboard(params)
      .then(setData)
      .catch((err) => setError(getErrorMessage(err, "Unable to load restaurant data. Please try again.")))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paramsKey]);

  useEffect(() => {
    load();
  }, [load]);

  return { data, loading, error, reload: load };
}
