import { useCallback, useEffect, useState } from "react";
import { fetchOrders } from "../services/api";
import { getErrorMessage } from "../utils/errors";

export function useOrders(params) {
  const [result, setResult] = useState({ count: 0, results: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const paramsKey = JSON.stringify(params);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchOrders(params)
      .then(setResult)
      .catch((err) => setError(getErrorMessage(err, "Unable to load orders. Please try again.")))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paramsKey]);

  useEffect(() => {
    load();
  }, [load]);

  return { orders: result.results, count: result.count, loading, error, reload: load };
}
