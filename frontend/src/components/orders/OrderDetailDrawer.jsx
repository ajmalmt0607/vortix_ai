import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { fetchOrderDetail } from "../../services/api";
import { formatMoney, formatDateTime } from "../../utils/format";
import { getErrorMessage } from "../../utils/errors";
import Badge from "../common/Badge";
import LoadingState from "../common/LoadingState";
import ErrorState from "../common/ErrorState";

const STATUS_VARIANT = {
  COMPLETED: "success",
  CONFIRMED: "info",
  PENDING: "warning",
  CANCELLED: "danger",
};

const TYPE_LABELS = { DINE_IN: "Dine-in", TAKEAWAY: "Takeaway", DELIVERY: "Delivery" };

function titleCase(value) {
  return value.charAt(0) + value.slice(1).toLowerCase();
}

export default function OrderDetailDrawer({ orderId, onClose }) {
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!orderId) return;
    setLoading(true);
    setError(null);
    setOrder(null);
    fetchOrderDetail(orderId)
      .then(setOrder)
      .catch((err) => setError(getErrorMessage(err, "Unable to load this order.")))
      .finally(() => setLoading(false));
  }, [orderId]);

  if (!orderId) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-slate-900/30" onClick={onClose} />
      <div className="relative flex h-[100dvh] w-full max-w-md flex-col bg-white shadow-2xl sm:h-full">
        <div className="flex flex-shrink-0 items-center justify-between border-b border-slate-100 px-5 pb-4 pt-[calc(env(safe-area-inset-top)+1rem)] sm:pt-4">
          <h2 className="text-sm font-semibold text-slate-900">Order Details</h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 pb-[calc(env(safe-area-inset-bottom)+1.5rem)] pt-5">
          {loading && <LoadingState message="Loading order..." />}
          {!loading && error && <ErrorState message={error} />}
          {!loading && !error && order && (
            <>
              <div>
                <p className="text-lg font-semibold text-slate-900">#{order.order_number}</p>
                <p className="mt-1 text-sm text-slate-500">{order.branch?.name}</p>
                <p className="text-xs text-slate-400">{formatDateTime(order.ordered_at)}</p>
                <div className="mt-3 flex items-center gap-2">
                  <Badge variant={STATUS_VARIANT[order.status] || "neutral"}>{titleCase(order.status)}</Badge>
                  <Badge variant="neutral">{TYPE_LABELS[order.order_type] || order.order_type}</Badge>
                </div>
                {order.customer && (
                  <p className="mt-2 text-xs text-slate-500">
                    Customer: <span className="font-medium text-slate-700">{order.customer.name}</span>
                    {order.customer.phone ? ` · ${order.customer.phone}` : ""}
                  </p>
                )}
              </div>

              <div className="mt-5 divide-y divide-slate-100 border-y border-slate-100">
                {order.items.map((item) => (
                  <div key={item.id} className="flex items-center justify-between py-3 text-sm">
                    <div>
                      <p className="font-medium text-slate-700">
                        {item.product?.name} × {item.quantity}
                      </p>
                      <p className="text-xs text-slate-400">{formatMoney(item.unit_price)} each</p>
                    </div>
                    <p className="font-medium text-slate-700">{formatMoney(item.total)}</p>
                  </div>
                ))}
              </div>

              <div className="mt-4 space-y-1.5 text-sm">
                <div className="flex justify-between text-slate-500">
                  <span>Subtotal</span>
                  <span>{formatMoney(order.subtotal)}</span>
                </div>
                <div className="flex justify-between text-slate-500">
                  <span>Discount</span>
                  <span>-{formatMoney(order.discount)}</span>
                </div>
                <div className="flex justify-between text-slate-500">
                  <span>Tax</span>
                  <span>{formatMoney(order.tax)}</span>
                </div>
                <div className="flex justify-between border-t border-slate-100 pt-2 text-base font-semibold text-slate-900">
                  <span>Total</span>
                  <span>{formatMoney(order.total)}</span>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
