import { useCallback, useEffect, useState } from "react";
import { fetchDashboard } from "../services/api";

// There's no dedicated GET /api/v1/branches/ endpoint yet, so the branch list
// for filter dropdowns is derived from the dashboard's branch_performance
// (present whenever no branch filter is applied). Cached at module scope so
// it's fetched at most once per session, regardless of which page loads first.
let cache = null;

function mapBranches(branchPerformance) {
  return (branchPerformance || []).map((b) => ({ id: b.branch_id, name: b.branch_name }));
}

export function useBranches() {
  const [branches, setBranches] = useState(cache || []);

  useEffect(() => {
    if (cache) return;
    let active = true;
    fetchDashboard({})
      .then((data) => {
        const list = mapBranches(data.branch_performance);
        cache = list;
        if (active) setBranches(list);
      })
      .catch(() => {
        // Silent: the branch filter just stays empty; page-level errors are
        // already surfaced elsewhere on the page.
      });
    return () => {
      active = false;
    };
  }, []);

  const registerFromDashboard = useCallback((branchPerformance) => {
    if (cache) return;
    const list = mapBranches(branchPerformance);
    if (list.length) {
      cache = list;
      setBranches(list);
    }
  }, []);

  return { branches, registerFromDashboard };
}
