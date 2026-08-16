import { useMemo, useState } from "react";
import { useOrders } from "../../hooks/useOrders";
import { useBranches } from "../../hooks/useBranches";
import { useDebounce } from "../../hooks/useDebounce";
import OrdersFilters from "../../components/orders/OrdersFilters";
import OrdersTable from "../../components/orders/OrdersTable";
import OrderDetailDrawer from "../../components/orders/OrderDetailDrawer";
import Pagination from "../../components/common/Pagination";
import LoadingState from "../../components/common/LoadingState";
import ErrorState from "../../components/common/ErrorState";

const PAGE_SIZE = 20;

export default function Orders() {
  const [filters, setFilters] = useState({
    branch: null,
    start_date: null,
    end_date: null,
    status: null,
    order_type: null,
    search: null,
  });
  const [page, setPage] = useState(1);
  const [selectedOrderId, setSelectedOrderId] = useState(null);

  const debouncedSearch = useDebounce(filters.search, 400);

  const params = useMemo(
    () => ({ ...filters, search: debouncedSearch, page, page_size: PAGE_SIZE }),
    [filters, debouncedSearch, page]
  );

  const { orders, count, loading, error, reload } = useOrders(params);
  const { branches } = useBranches();

  function handleFilterChange(patch) {
    setFilters((prev) => ({ ...prev, ...patch }));
    setPage(1);
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Orders</h1>
        <p className="text-sm text-slate-500">Browse and search all restaurant orders</p>
      </div>

      <OrdersFilters branches={branches} filters={filters} onChange={handleFilterChange} />

      <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
        {loading && <LoadingState message="Loading orders..." />}
        {!loading && error && <ErrorState message={error} onRetry={reload} />}
        {!loading && !error && (
          <>
            <OrdersTable orders={orders} onSelect={setSelectedOrderId} />
            <Pagination page={page} pageSize={PAGE_SIZE} count={count} onPageChange={setPage} />
          </>
        )}
      </div>

      <OrderDetailDrawer orderId={selectedOrderId} onClose={() => setSelectedOrderId(null)} />
    </div>
  );
}
