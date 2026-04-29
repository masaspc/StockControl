export type Role = "admin" | "manager" | "operator" | "viewer";

export interface UserMe {
  id: number;
  ad_account: string;
  display_name: string;
  email: string | null;
  role: Role;
  site_id: number | null;
  last_login: string | null;
}

export interface Item {
  id: number;
  code: string;
  name: string;
  category: string | null;
  maker: string | null;
  model_no: string | null;
  manage_type: "serial" | "quantity";
  unit: string;
  order_point: number;
  order_unit: number;
  barcode: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Location {
  id: number;
  code: string;
  name: string;
  loc_type: "site" | "area" | "shelf" | "vehicle" | "person" | "customer";
  parent_id: number | null;
  site_id: number | null;
  manager_id: number | null;
  is_active: boolean;
  created_at: string;
}

export interface LocationTreeNode extends Location {
  children: LocationTreeNode[];
}

export interface StockDetail {
  id: number;
  item_id: number;
  location_id: number;
  quantity: number;
  updated_at: string;
  item_code: string | null;
  item_name: string | null;
  location_code: string | null;
  location_name: string | null;
  order_point: number | null;
  is_alert: boolean;
}

export interface StockSummary {
  total_items: number;
  total_locations: number;
  alert_items: number;
  serial_items_total: number;
  serial_items_in_stock: number;
  serial_items_checked_out: number;
}

export interface SerialItem {
  id: number;
  item_id: number;
  serial_no: string;
  mac_address: string | null;
  location_id: number | null;
  status: "in_stock" | "checked_out" | "disposed" | "lost";
  condition: "normal" | "damaged" | "repair_needed";
  received_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: number;
  tx_type: "in" | "out" | "return" | "transfer" | "adjust";
  item_id: number;
  serial_item_id: number | null;
  quantity: number;
  from_location_id: number | null;
  to_location_id: number | null;
  operator_id: number;
  note: string | null;
  work_order_no: string | null;
  created_at: string;
}

export interface Order {
  id: number;
  order_no: string;
  item_id: number;
  supplier_id: number | null;
  quantity: number;
  status: string;
  requested_by: number | null;
  approved_by: number | null;
  ordered_at: string | null;
  expected_at: string | null;
  note: string | null;
  created_at: string;
  updated_at: string;
}

export interface Supplier {
  id: number;
  name: string;
  contact: string | null;
  email: string | null;
  phone: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AlertItem {
  item_id: number;
  item_code: string;
  item_name: string;
  current_qty: number;
  order_point: number;
  unit: string;
}

export interface RecentTransaction {
  id: number;
  tx_type: string;
  item_name: string;
  quantity: number;
  operator_name: string | null;
  created_at: string;
}

export interface DashboardData {
  total_items: number;
  total_locations: number;
  total_serials: number;
  alert_count: number;
  pending_orders: number;
  today_in: number;
  today_out: number;
  alerts: AlertItem[];
  recent_transactions: RecentTransaction[];
}
