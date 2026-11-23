from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import sys
import threading
import webbrowser
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

# Ensure relative paths in storage.py (products.json, orders.json) always resolve
# inside the Products/ directory regardless of where the user runs this script.
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
os.chdir(BASE_DIR)

import common  # noqa: E402
import delivery  # noqa: E402
import inventory  # noqa: E402
import order  # noqa: E402
import storage  # noqa: E402

HOST = "127.0.0.1"
PORT = 8000

DATA_LOCK = threading.Lock()
INITIAL_PRODUCTS_SNAPSHOT: list[dict[str, Any]] = []
INITIAL_ORDERS_SNAPSHOT: list[dict[str, Any]] = []


def capture_initial_snapshot() -> None:
    """Capture the starting JSON datasets."""
    global INITIAL_PRODUCTS_SNAPSHOT, INITIAL_ORDERS_SNAPSHOT
    with DATA_LOCK:
        INITIAL_PRODUCTS_SNAPSHOT = copy.deepcopy(storage.load_products())
        INITIAL_ORDERS_SNAPSHOT = copy.deepcopy(storage.load_orders())


def assign_delivery_non_interactive(
    order_id: str,
    delivery_method: str,
    driver_id: str | None = None,
) -> dict[str, Any]:
    orders, target_order = delivery.find_order(order_id)

    if target_order["status"] != common.STATUS_PACKED:
        raise ValueError("Delivery can only be assigned to a Packed order.")

    valid_methods = {
        common.DELIVERY_METHOD_COURIER,
        common.DELIVERY_METHOD_SELF_PICKUP,
    }
    if delivery_method not in valid_methods:
        raise ValueError(
            f"Invalid delivery method. Choose {common.DELIVERY_METHOD_COURIER} "
            f"or {common.DELIVERY_METHOD_SELF_PICKUP}."
        )

    if delivery_method == common.DELIVERY_METHOD_COURIER:
        if not driver_id or driver_id not in delivery.DRIVERS:
            raise ValueError("Please select a valid driver for Courier delivery.")
        assigned_driver_id: str | None = driver_id
        assigned_driver_name: str | None = delivery.DRIVERS[driver_id]
    else:
        assigned_driver_id = None
        assigned_driver_name = None

    target_order["delivery"] = {
        "delivery_method": delivery_method,
        "driver_id": assigned_driver_id,
        "driver_name": assigned_driver_name,
        "delivery_status": common.DELIVERY_STATUS_ASSIGNED,
    }
    target_order["status"] = common.STATUS_READY_FOR_DELIVERY
    target_order.setdefault("status_history", []).append(
        common.new_status_history_entry(
            common.STATUS_READY_FOR_DELIVERY,
            datetime.now().isoformat(timespec="seconds"),
        )
    )
    storage.save_orders(orders)
    return target_order


def build_state_payload() -> dict[str, Any]:
    """Return full application state for the frontend."""
    return {
        "products": inventory.list_products(),
        "orders": order.list_orders(),
        "drivers": delivery.DRIVERS,
        "delivery_methods": [
            common.DELIVERY_METHOD_COURIER,
            common.DELIVERY_METHOD_SELF_PICKUP,
        ],
        "order_statuses": list(common.ORDER_STATUSES),
        "delivery_statuses": list(common.DELIVERY_STATUSES),
    }


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>E-Shop Logistics Management System — Group 65</title>
  <style>
    :root {
      --bg: #f4f6f9;
      --surface: #ffffff;
      --surface-alt: #f8fafc;
      --border: #e2e8f0;
      --text: #0f172a;
      --muted: #64748b;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --primary-soft: #eff6ff;
      --success: #15803d;
      --success-bg: #dcfce7;
      --warn: #b45309;
      --warn-bg: #fef3c7;
      --danger: #b91c1c;
      --danger-bg: #fee2e2;
      --info: #0369a1;
      --info-bg: #e0f2fe;
      --radius: 10px;
      --shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }

    header {
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 16px 24px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      position: sticky;
      top: 0;
      z-index: 10;
    }

    .brand h1 {
      margin: 0;
      font-size: 1.2rem;
      font-weight: 700;
    }

    .brand p {
      margin: 2px 0 0;
      font-size: 0.85rem;
      color: var(--muted);
    }

    .header-actions {
      display: flex;
      gap: 8px;
      align-items: center;
    }

    main {
      max-width: 1160px;
      margin: 24px auto;
      padding: 0 20px 48px;
    }

    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 14px;
      margin-bottom: 22px;
    }

    .kpi-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 16px 18px;
      box-shadow: var(--shadow);
    }

    .kpi-label {
      font-size: 0.8rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .kpi-value {
      font-size: 1.65rem;
      font-weight: 700;
      margin-top: 4px;
    }

    .kpi-sub {
      font-size: 0.82rem;
      color: var(--muted);
      margin-top: 2px;
    }

    .tabs {
      display: flex;
      gap: 8px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 20px;
      flex-wrap: wrap;
    }

    .tab-btn {
      background: transparent;
      border: none;
      border-bottom: 2px solid transparent;
      padding: 10px 16px;
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--muted);
      cursor: pointer;
    }

    .tab-btn.active {
      color: var(--primary);
      border-bottom-color: var(--primary);
    }

    .panel { display: none; }
    .panel.active { display: block; }

    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 18px;
      box-shadow: var(--shadow);
      margin-bottom: 16px;
    }

    .card-header {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      margin-bottom: 14px;
    }

    .card-header h2 {
      margin: 0;
      font-size: 1.05rem;
    }

    .form-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 10px;
      align-items: end;
    }

    label {
      display: block;
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--muted);
      margin-bottom: 4px;
    }

    input, select {
      width: 100%;
      padding: 8px 10px;
      border: 1px solid var(--border);
      border-radius: 7px;
      font-size: 0.92rem;
      background: var(--surface);
      color: var(--text);
    }

    button {
      padding: 8px 14px;
      border-radius: 7px;
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--text);
      font-size: 0.88rem;
      font-weight: 600;
      cursor: pointer;
    }

    button:hover { background: var(--surface-alt); }
    button:disabled { opacity: 0.5; cursor: not-allowed; }

    .btn-primary {
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
    }
    .btn-primary:hover { background: var(--primary-hover); }

    .btn-success {
      background: var(--success);
      color: #ffffff;
      border-color: var(--success);
    }
    .btn-success:hover { filter: brightness(0.92); }

    .btn-danger {
      background: var(--surface);
      color: var(--danger);
      border-color: #fecaca;
    }
    .btn-danger:hover { background: var(--danger-bg); }

    .btn-sm { padding: 5px 9px; font-size: 0.8rem; }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
    }

    th, td {
      text-align: left;
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
    }

    th {
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
      background: var(--surface-alt);
    }

    .num { text-align: right; font-variant-numeric: tabular-nums; }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.86rem; }

    .badge {
      display: inline-block;
      padding: 3px 9px;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 600;
      white-space: nowrap;
    }

    .badge-pending, .badge-unassigned { background: var(--warn-bg); color: var(--warn); }
    .badge-packed, .badge-assigned { background: var(--info-bg); color: var(--info); }
    .badge-ready, .badge-transit { background: var(--primary-soft); color: var(--primary); }
    .badge-delivered { background: var(--success-bg); color: var(--success); }
    .badge-cancelled { background: var(--danger-bg); color: var(--danger); }

    .order-card {
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 16px;
      margin-bottom: 14px;
      background: var(--surface);
    }

    .order-top {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: flex-start;
      gap: 10px;
      margin-bottom: 10px;
    }

    .order-meta {
      font-size: 0.86rem;
      color: var(--muted);
    }

    .action-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin-top: 12px;
    }

    .inline-controls {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }

    .inline-controls select { width: auto; min-width: 150px; }

    .timeline {
      margin: 12px 0 0;
      padding-left: 18px;
      border-left: 2px solid var(--border);
    }

    .timeline-item {
      position: relative;
      padding: 0 0 10px 10px;
      font-size: 0.86rem;
    }

    .timeline-item::before {
      content: "";
      position: absolute;
      left: -24px;
      top: 5px;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--primary);
      border: 2px solid var(--surface);
    }

    .timeline-time {
      color: var(--muted);
      font-size: 0.8rem;
      margin-left: 6px;
    }

    .toast {
      position: fixed;
      bottom: 20px;
      right: 20px;
      max-width: 420px;
      padding: 12px 16px;
      border-radius: 8px;
      color: #ffffff;
      font-size: 0.9rem;
      font-weight: 500;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.2);
      display: none;
      z-index: 100;
    }

    .toast.show { display: block; }
    .toast.ok { background: #15803d; }
    .toast.err { background: #b91c1c; }

    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.45);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 50;
      padding: 16px;
    }

    .modal-backdrop.open { display: flex; }

    .modal {
      background: var(--surface);
      border-radius: var(--radius);
      padding: 20px;
      width: 100%;
      max-width: 420px;
      box-shadow: 0 12px 32px rgba(15, 23, 42, 0.22);
    }

    .modal h3 { margin: 0 0 14px; }
    .modal-field { margin-bottom: 12px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <h1>E-Shop Logistics Management System</h1>
      <p>COMP 8500SEF · Group 65 </p>
    </div>
    <div class="header-actions">
      <button onclick="loadState(true)">Refresh</button>
      <button class="btn-danger" onclick="resetDemo()">Reset Demo Data</button>
    </div>
  </header>

  <main>
    <section class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Inventory SKUs</div>
        <div class="kpi-value" id="kpi-products">0</div>
        <div class="kpi-sub" id="kpi-units">0 total units in stock</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Pending Orders</div>
        <div class="kpi-value" id="kpi-pending">0</div>
        <div class="kpi-sub">Awaiting packing</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Active Deliveries</div>
        <div class="kpi-value" id="kpi-active">0</div>
        <div class="kpi-sub">Packed, Ready, or Out for Delivery</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Delivered Orders</div>
        <div class="kpi-value" id="kpi-delivered">0</div>
        <div class="kpi-sub">Completed end-to-end</div>
      </div>
    </section>

    <nav class="tabs">
      <button class="tab-btn active" data-tab="inventory" onclick="switchTab('inventory')">1. Product &amp; Inventory</button>
      <button class="tab-btn" data-tab="orders" onclick="switchTab('orders')">2. Orders &amp; Fulfillment</button>
      <button class="tab-btn" data-tab="delivery" onclick="switchTab('delivery')">3. Delivery &amp; Tracking</button>
    </nav>

    <!-- Tab 1: Inventory -->
    <section id="tab-inventory" class="panel active">
      <div class="card">
        <div class="card-header"><h2>Add New Product</h2></div>
        <form id="add-product-form" class="form-row" onsubmit="handleAddProduct(event)">
          <div>
            <label for="new-name">Product Name</label>
            <input id="new-name" required placeholder="e.g., Wireless Mouse" />
          </div>
          <div>
            <label for="new-price">Price (HK$)</label>
            <input id="new-price" required placeholder="e.g., 120.00" />
          </div>
          <div>
            <label for="new-stock">Starting Stock</label>
            <input id="new-stock" type="number" min="0" step="1" required placeholder="e.g., 25" />
          </div>
          <div>
            <button type="submit" class="btn-primary" style="width:100%;">Add Product</button>
          </div>
        </form>
      </div>

      <div class="card">
        <div class="card-header">
          <h2>Inventory List</h2>
          <input id="product-search" placeholder="Filter by ID or name..." style="max-width:260px;" oninput="renderInventory()" />
        </div>
        <div style="overflow-x:auto;">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Product Name</th>
                <th class="num">Price (HK$)</th>
                <th class="num">Stock</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="inventory-tbody"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- Tab 2: Orders -->
    <section id="tab-orders" class="panel">
      <div class="card">
        <div class="card-header">
          <h2>Customer Orders &amp; Fulfillment</h2>
          <select id="order-status-filter" style="max-width:220px;" onchange="renderOrders()">
            <option value="ALL">All Statuses</option>
          </select>
        </div>
        <div id="orders-container"></div>
      </div>
    </section>

    <!-- Tab 3: Delivery & Tracking -->
    <section id="tab-delivery" class="panel">
      <div class="card">
        <div class="card-header">
          <h2>Delivery Assignment &amp; Order Tracking</h2>
          <span style="font-size:0.85rem;color:var(--muted);">Packed orders can be assigned to Courier or Self Pickup</span>
        </div>
        <div id="delivery-container"></div>
      </div>
    </section>
  </main>

  <!-- Edit Product Modal -->
  <div id="edit-modal" class="modal-backdrop">
    <div class="modal">
      <h3 id="edit-modal-title">Edit Product</h3>
      <form onsubmit="handleEditProduct(event)">
        <input type="hidden" id="edit-id" />
        <div class="modal-field">
          <label for="edit-name">Product Name</label>
          <input id="edit-name" required />
        </div>
        <div class="modal-field">
          <label for="edit-price">Price (HK$)</label>
          <input id="edit-price" required />
        </div>
        <div class="modal-actions">
          <button type="button" onclick="closeEditModal()">Cancel</button>
          <button type="submit" class="btn-primary">Save Changes</button>
        </div>
      </form>
    </div>
  </div>

  <div id="toast" class="toast"></div>

  <script>
    let appState = { products: [], orders: [], drivers: {}, delivery_methods: [], order_statuses: [] };

    function escapeHtml(val) {
      return String(val ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function showToast(message, isError = false) {
      const el = document.getElementById("toast");
      el.textContent = message;
      el.className = "toast show " + (isError ? "err" : "ok");
      clearTimeout(el._timer);
      el._timer = setTimeout(() => { el.className = "toast"; }, 3500);
    }

    function badgeClass(status) {
      const s = (status || "").toLowerCase();
      if (s === "pending" || s === "unassigned") return "badge badge-pending";
      if (s === "packed" || s === "assigned") return "badge badge-packed";
      if (s.includes("ready") || s.includes("out") || s.includes("transit")) return "badge badge-ready";
      if (s === "delivered") return "badge badge-delivered";
      if (s === "cancelled") return "badge badge-cancelled";
      return "badge";
    }

    function formatTime(iso) {
      if (!iso) return "";
      return iso.replace("T", " ").slice(0, 19);
    }

    function switchTab(name) {
      document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.tab === name);
      });
      document.querySelectorAll(".panel").forEach(panel => {
        panel.classList.toggle("active", panel.id === "tab-" + name);
      });
    }

    async function apiRequest(url, options = {}) {
      const res = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        ...options,
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Request failed");
      }
      return data;
    }

    async function loadState(notify = false) {
      try {
        appState = await apiRequest("/api/state");
        populateStatusFilter();
        renderAll();
        if (notify) showToast("Refreshed from products.json and orders.json");
      } catch (err) {
        showToast(err.message, true);
      }
    }

    function populateStatusFilter() {
      const sel = document.getElementById("order-status-filter");
      const current = sel.value || "ALL";
      sel.innerHTML = '<option value="ALL">All Statuses</option>' +
        appState.order_statuses.map(s => `<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`).join("");
      sel.value = current;
    }

    function renderAll() {
      renderKpis();
      renderInventory();
      renderOrders();
      renderDelivery();
    }

    function renderKpis() {
      const products = appState.products || [];
      const orders = appState.orders || [];
      const totalUnits = products.reduce((sum, p) => sum + Number(p.stock_quantity || 0), 0);
      const pending = orders.filter(o => o.status === "Pending").length;
      const active = orders.filter(o => ["Packed", "Ready for Delivery", "Out for Delivery"].includes(o.status)).length;
      const delivered = orders.filter(o => o.status === "Delivered").length;

      document.getElementById("kpi-products").textContent = products.length;
      document.getElementById("kpi-units").textContent = `${totalUnits} total units in stock`;
      document.getElementById("kpi-pending").textContent = pending;
      document.getElementById("kpi-active").textContent = active;
      document.getElementById("kpi-delivered").textContent = delivered;
    }

    function renderInventory() {
      const query = (document.getElementById("product-search").value || "").trim().toLowerCase();
      const rows = (appState.products || []).filter(p =>
        !query ||
        p.product_id.toLowerCase().includes(query) ||
        p.product_name.toLowerCase().includes(query)
      );

      const tbody = document.getElementById("inventory-tbody");
      if (!rows.length) {
        tbody.innerHTML = '<tr><td colspan="5" style="color:var(--muted);">No matching products.</td></tr>';
        return;
      }

      tbody.innerHTML = rows.map(p => `
        <tr>
          <td class="mono">${escapeHtml(p.product_id)}</td>
          <td>${escapeHtml(p.product_name)}</td>
          <td class="num">${escapeHtml(p.price)}</td>
          <td class="num"><strong>${escapeHtml(p.stock_quantity)}</strong></td>
          <td>
            <button class="btn-sm" onclick="adjustStock('${escapeHtml(p.product_id)}', -1)">-1</button>
            <button class="btn-sm" onclick="adjustStock('${escapeHtml(p.product_id)}', 1)">+1</button>
            <button class="btn-sm" onclick="adjustStock('${escapeHtml(p.product_id)}', 10)">+10</button>
            <button class="btn-sm" onclick="openEditModal('${escapeHtml(p.product_id)}')">Edit</button>
          </td>
        </tr>
      `).join("");
    }

    function renderOrders() {
      const filter = document.getElementById("order-status-filter").value;
      const orders = (appState.orders || []).filter(o => filter === "ALL" || o.status === filter);
      const container = document.getElementById("orders-container");

      if (!orders.length) {
        container.innerHTML = '<p style="color:var(--muted);">No orders match this filter.</p>';
        return;
      }

      container.innerHTML = orders.map(o => {
        const itemsHtml = (o.items || []).map(it => `
          <tr>
            <td class="mono">${escapeHtml(it.product_id)}</td>
            <td>${escapeHtml(it.product_name)}</td>
            <td class="num">${escapeHtml(it.price)}</td>
            <td class="num">${escapeHtml(it.quantity)}</td>
            <td class="num">${escapeHtml(it.line_total)}</td>
          </tr>
        `).join("");

        const canAct = o.status === "Pending";
        return `
          <div class="order-card">
            <div class="order-top">
              <div>
                <strong>Order #${escapeHtml(o.order_id)}</strong> — ${escapeHtml(o.customer_name)}
                <div class="order-meta">${escapeHtml(o.delivery_address)} · Created ${escapeHtml(formatTime(o.created_at))}</div>
              </div>
              <div>
                <span class="${badgeClass(o.status)}">${escapeHtml(o.status)}</span>
                <strong style="margin-left:10px;">HK$${escapeHtml(o.total)}</strong>
              </div>
            </div>
            <div style="overflow-x:auto;">
              <table>
                <thead>
                  <tr>
                    <th>Product ID</th>
                    <th>Item</th>
                    <th class="num">Unit Price</th>
                    <th class="num">Qty</th>
                    <th class="num">Line Total</th>
                  </tr>
                </thead>
                <tbody>${itemsHtml}</tbody>
              </table>
            </div>
            <div class="action-bar">
              ${canAct ? `
                <button class="btn-primary" onclick="packOrder('${escapeHtml(o.order_id)}')">Pack Order (Auto-Deduct Stock)</button>
                <button class="btn-danger" onclick="cancelOrder('${escapeHtml(o.order_id)}')">Cancel Order</button>
              ` : `
                <button onclick="switchTab('delivery')">Manage Delivery &amp; Tracking</button>
              `}
            </div>
          </div>
        `;
      }).join("");
    }

    function renderDelivery() {
      const orders = appState.orders || [];
      const container = document.getElementById("delivery-container");
      const driverOptions = Object.entries(appState.drivers || {})
        .map(([id, name]) => `<option value="${escapeHtml(id)}">${escapeHtml(id)} — ${escapeHtml(name)}</option>`)
        .join("");

      if (!orders.length) {
        container.innerHTML = '<p style="color:var(--muted);">No orders found.</p>';
        return;
      }

      container.innerHTML = orders.map(o => {
        const d = o.delivery || {};
        const historyHtml = (o.status_history || []).map(h => `
          <div class="timeline-item">
            <strong>${escapeHtml(h.status)}</strong>
            <span class="timeline-time">${escapeHtml(formatTime(h.at))}</span>
          </div>
        `).join("");

        let controlsHtml = "";
        if (o.status === "Packed") {
          controlsHtml = `
            <div class="inline-controls">
              <select id="method-${escapeHtml(o.order_id)}" onchange="toggleDriverSelect('${escapeHtml(o.order_id)}')">
                ${(appState.delivery_methods || []).map(m => `<option value="${escapeHtml(m)}">${escapeHtml(m)}</option>`).join("")}
              </select>
              <select id="driver-${escapeHtml(o.order_id)}">${driverOptions}</select>
              <button class="btn-primary" onclick="assignDelivery('${escapeHtml(o.order_id)}')">Assign Delivery</button>
            </div>
          `;
        } else if (d.delivery_status === "Assigned") {
          controlsHtml = `<button class="btn-primary" onclick="startDelivery('${escapeHtml(o.order_id)}')">Start Delivery (Out for Delivery)</button>`;
        } else if (d.delivery_status === "In Transit") {
          controlsHtml = `<button class="btn-success" onclick="completeDelivery('${escapeHtml(o.order_id)}')">Mark as Delivered</button>`;
        }

        const driverLabel = d.driver_id ? `${d.driver_id} (${d.driver_name})` : "N/A";
        return `
          <div class="order-card">
            <div class="order-top">
              <div>
                <strong>Order #${escapeHtml(o.order_id)}</strong> — ${escapeHtml(o.customer_name)}
                <div class="order-meta">
                  Method: <strong>${escapeHtml(d.delivery_method || "Unset")}</strong> ·
                  Driver: <strong>${escapeHtml(driverLabel)}</strong>
                </div>
              </div>
              <div style="display:flex;gap:6px;flex-wrap:wrap;">
                <span class="${badgeClass(o.status)}">Order: ${escapeHtml(o.status)}</span>
                <span class="${badgeClass(d.delivery_status)}">Delivery: ${escapeHtml(d.delivery_status || "Unassigned")}</span>
              </div>
            </div>
            ${controlsHtml ? `<div class="action-bar">${controlsHtml}</div>` : ""}
            <div class="timeline">${historyHtml}</div>
          </div>
        `;
      }).join("");
    }

    function toggleDriverSelect(orderId) {
      const method = document.getElementById("method-" + orderId).value;
      const driverSel = document.getElementById("driver-" + orderId);
      driverSel.disabled = method !== "Courier";
    }

    async function handleAddProduct(event) {
      event.preventDefault();
      try {
        const name = document.getElementById("new-name").value;
        const price = document.getElementById("new-price").value;
        const starting_stock = Number(document.getElementById("new-stock").value);
        const res = await apiRequest("/api/products", {
          method: "POST",
          body: JSON.stringify({ name, price, starting_stock }),
        });
        document.getElementById("add-product-form").reset();
        await loadState();
        showToast(`Added ${res.product.product_id} — ${res.product.product_name}`);
      } catch (err) {
        showToast(err.message, true);
      }
    }

    function openEditModal(productId) {
      const product = appState.products.find(p => p.product_id === productId);
      if (!product) return;
      document.getElementById("edit-id").value = product.product_id;
      document.getElementById("edit-modal-title").textContent = `Edit ${product.product_id}`;
      document.getElementById("edit-name").value = product.product_name;
      document.getElementById("edit-price").value = product.price;
      document.getElementById("edit-modal").classList.add("open");
    }

    function closeEditModal() {
      document.getElementById("edit-modal").classList.remove("open");
    }

    async function handleEditProduct(event) {
      event.preventDefault();
      try {
        const id = document.getElementById("edit-id").value;
        const name = document.getElementById("edit-name").value;
        const price = document.getElementById("edit-price").value;
        await apiRequest(`/api/products/${encodeURIComponent(id)}`, {
          method: "PUT",
          body: JSON.stringify({ name, price }),
        });
        closeEditModal();
        await loadState();
        showToast(`Updated product ${id}`);
      } catch (err) {
        showToast(err.message, true);
      }
    }

    async function adjustStock(productId, change) {
      try {
        const res = await apiRequest(`/api/products/${encodeURIComponent(productId)}/stock`, {
          method: "POST",
          body: JSON.stringify({ change }),
        });
        await loadState();
        showToast(`${productId} stock updated to ${res.product.stock_quantity}`);
      } catch (err) {
        showToast(err.message, true);
      }
    }

    async function packOrder(orderId) {
      try {
        await apiRequest(`/api/orders/${encodeURIComponent(orderId)}/pack`, { method: "POST" });
        await loadState();
        showToast(`Order #${orderId} packed and inventory stock deducted`);
      } catch (err) {
        showToast(err.message, true);
      }
    }

    async function cancelOrder(orderId) {
      try {
        await apiRequest(`/api/orders/${encodeURIComponent(orderId)}/cancel`, { method: "POST" });
        await loadState();
        showToast(`Order #${orderId} cancelled`);
      } catch (err) {
        showToast(err.message, true);
      }
    }

    async function assignDelivery(orderId) {
      try {
        const delivery_method = document.getElementById("method-" + orderId).value;
        const driver_id = delivery_method === "Courier"
          ? document.getElementById("driver-" + orderId).value
          : null;
        await apiRequest(`/api/orders/${encodeURIComponent(orderId)}/delivery/assign`, {
          method: "POST",
          body: JSON.stringify({ delivery_method, driver_id }),
        });
        await loadState();
        showToast(`Delivery assigned for Order #${orderId}`);
      } catch (err) {
        showToast(err.message, true);
      }
    }

    async function startDelivery(orderId) {
      try {
        await apiRequest(`/api/orders/${encodeURIComponent(orderId)}/delivery/start`, { method: "POST" });
        await loadState();
        showToast(`Order #${orderId} is now Out for Delivery`);
      } catch (err) {
        showToast(err.message, true);
      }
    }

    async function completeDelivery(orderId) {
      try {
        await apiRequest(`/api/orders/${encodeURIComponent(orderId)}/delivery/complete`, { method: "POST" });
        await loadState();
        showToast(`Order #${orderId} marked as Delivered`);
      } catch (err) {
        showToast(err.message, true);
      }
    }

    async function resetDemo() {
      try {
        await apiRequest("/api/reset", { method: "POST" });
        await loadState();
        showToast("Demo data restored to initial snapshot");
      } catch (err) {
        showToast(err.message, true);
      }
    }

    loadState();
  </script>
</body>
</html>
"""


class LogisticsHandler(BaseHTTPRequestHandler):
    """Local HTTP handler delegating all business logic to existing project modules."""

    def log_message(self, format: str, *args: Any) -> None:
        # Keep terminal output concise during demos.
        print(f"[web_app] {self.address_string()} - {format % args}")

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON request body.") from exc
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object.")
        return data

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        try:
            if path in ("/", "/index.html"):
                self._send_html(HTML_PAGE)
            elif path == "/api/state":
                with DATA_LOCK:
                    self._send_json(build_state_payload())
            else:
                self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:
        parts = [unquote(p) for p in urlparse(self.path).path.strip("/").split("/") if p]
        try:
            body = self._read_json_body()
            with DATA_LOCK:
                if parts == ["api", "products"]:
                    product = inventory.add_product(
                        body.get("name"),
                        body.get("price"),
                        body.get("starting_stock"),
                    )
                    self._send_json({"product": product}, HTTPStatus.CREATED)
                elif len(parts) == 4 and parts[:2] == ["api", "products"] and parts[3] == "stock":
                    product = inventory.change_stock(parts[2], body.get("change"))
                    self._send_json({"product": product})
                elif len(parts) == 4 and parts[:2] == ["api", "orders"] and parts[3] == "pack":
                    updated = order.pack_order(parts[2])
                    self._send_json({"order": updated})
                elif len(parts) == 4 and parts[:2] == ["api", "orders"] and parts[3] == "cancel":
                    updated = order.cancel_order(parts[2])
                    self._send_json({"order": updated})
                elif len(parts) == 5 and parts[:2] == ["api", "orders"] and parts[3:] == ["delivery", "assign"]:
                    updated = assign_delivery_non_interactive(
                        parts[2],
                        body.get("delivery_method", ""),
                        body.get("driver_id"),
                    )
                    self._send_json({"order": updated})
                elif len(parts) == 5 and parts[:2] == ["api", "orders"] and parts[3:] == ["delivery", "start"]:
                    with contextlib.redirect_stdout(io.StringIO()):
                        delivery.start_delivery(parts[2])
                    self._send_json({"order": order.view_order_details(parts[2])})
                elif len(parts) == 5 and parts[:2] == ["api", "orders"] and parts[3:] == ["delivery", "complete"]:
                    with contextlib.redirect_stdout(io.StringIO()):
                        delivery.complete_delivery(parts[2])
                    self._send_json({"order": order.view_order_details(parts[2])})
                elif parts == ["api", "reset"]:
                    storage.save_products(copy.deepcopy(INITIAL_PRODUCTS_SNAPSHOT))
                    storage.save_orders(copy.deepcopy(INITIAL_ORDERS_SNAPSHOT))
                    self._send_json({"status": "reset"})
                else:
                    self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_PUT(self) -> None:
        parts = [unquote(p) for p in urlparse(self.path).path.strip("/").split("/") if p]
        try:
            body = self._read_json_body()
            with DATA_LOCK:
                if len(parts) == 3 and parts[:2] == ["api", "products"]:
                    updated = inventory.update_product(
                        parts[2],
                        name=body.get("name"),
                        price=body.get("price"),
                    )
                    self._send_json({"product": updated})
                else:
                    self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)


def run_server(host: str = HOST, port: int = PORT, open_browser: bool = True) -> None:
    capture_initial_snapshot()
    server = ThreadingHTTPServer((host, port), LogisticsHandler)
    url = f"http://{host}:{port}"
    print(f"E-Shop Logistics Web Display running at {url}")
    print("Press Ctrl+C to stop.")
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down local web server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()