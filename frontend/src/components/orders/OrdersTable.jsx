import { formatMoney, formatDateTime } from "../../utils/format";
import Badge from "../common/Badge";
import EmptyState from "../common/EmptyState";

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

export default function OrdersTable({ orders, onSelect }) {
  if (!orders || orders.length === 0) {
    return <EmptyState title="No orders found" message="Try adjusting your filters." />;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs text-slate-400">
            <th className="px-5 py-2.5 font-medium">Order</th>
            <th className="px-5 py-2.5 font-medium">Branch</th>
            <th className="px-5 py-2.5 font-medium">Customer</th>
            <th className="px-5 py-2.5 font-medium">Type</th>
            <th className="px-5 py-2.5 text-right font-medium">Total</th>
            <th className="px-5 py-2.5 font-medium">Status</th>
            <th className="px-5 py-2.5 font-medium">Date</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((order) => (
            <tr
              key={order.id}
              onClick={() => onSelect(order.id)}
              className="cursor-pointer border-t border-slate-50 hover:bg-slate-50"
            >
              <td className="px-5 py-3 font-medium text-slate-800">{order.order_number}</td>
              <td className="px-5 py-3 text-slate-600">{order.branch?.name || "—"}</td>
              <td className="px-5 py-3 text-slate-600">{order.customer?.name || "Walk-in"}</td>
              <td className="px-5 py-3 text-slate-600">{TYPE_LABELS[order.order_type] || order.order_type}</td>
              <td className="px-5 py-3 text-right font-medium text-slate-800">{formatMoney(order.total)}</td>
              <td className="px-5 py-3">
                <Badge variant={STATUS_VARIANT[order.status] || "neutral"}>{titleCase(order.status)}</Badge>
              </td>
              <td className="whitespace-nowrap px-5 py-3 text-slate-500">{formatDateTime(order.ordered_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
