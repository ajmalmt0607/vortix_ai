import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

function cleanParams(params = {}) {
  const out = {};
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      out[key] = value;
    }
  });
  return out;
}

export async function fetchDashboard(params = {}) {
  const { data } = await api.get("/dashboard/", { params: cleanParams(params) });
  return data;
}

export async function fetchOrders(params = {}) {
  const { data } = await api.get("/orders/", { params: cleanParams(params) });
  return data;
}

export async function fetchOrderDetail(id) {
  const { data } = await api.get(`/orders/${id}/`);
  return data;
}

export async function sendAIMessage(message) {
  const { data } = await api.post("/ai/chat/", { message });
  return data;
}

export default api;
