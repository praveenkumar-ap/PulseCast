import type { UserRole } from "@/types/domain";

export type NavItem = {
  id: string;
  label: string;
  path: string;
  description?: string;
  rolesVisible: UserRole[];
  orderByRole?: Partial<Record<UserRole, number>>;
};

export const NAV_ITEMS: NavItem[] = [
  {
    id: "forecasts",
    label: "Forecasts",
    path: "/forecasts",
    description: "Outlooks and projections across signals.",
    rolesVisible: ["PLANNER", "APPROVER", "DATA_SCIENTIST"],
    orderByRole: { PLANNER: 1, APPROVER: 3, DATA_SCIENTIST: 2 },
  },
  {
    id: "scenarios",
    label: "Scenarios",
    path: "/scenarios",
    description: "What-if experiments and approvals.",
    rolesVisible: ["PLANNER", "APPROVER"],
    orderByRole: { PLANNER: 2, APPROVER: 1 },
  },
  {
    id: "optimizer",
    label: "Optimizer",
    path: "/optimizer",
    description: "Inventory policy recommendations.",
    rolesVisible: ["PLANNER"],
    orderByRole: { PLANNER: 3 },
  },
  {
    id: "alerts",
    label: "Alerts",
    path: "/alerts",
    description: "Signals that need your attention.",
    rolesVisible: ["PLANNER", "APPROVER", "DATA_SCIENTIST"],
    orderByRole: { PLANNER: 4, APPROVER: 4, DATA_SCIENTIST: 4 },
  },
  {
    id: "indicators",
    label: "Indicators",
    path: "/indicators",
    description: "Signal catalog and freshness.",
    rolesVisible: ["PLANNER", "DATA_SCIENTIST"],
    orderByRole: { PLANNER: 5, DATA_SCIENTIST: 1 },
  },
  {
    id: "monitor",
    label: "Monitor",
    path: "/monitor",
    description: "Data and forecast health.",
    rolesVisible: ["PLANNER", "DATA_SCIENTIST"],
    orderByRole: { PLANNER: 6, DATA_SCIENTIST: 3 },
  },
  {
    id: "value",
    label: "Value & ROI",
    path: "/value",
    description: "Business impact summaries.",
    rolesVisible: ["PLANNER", "APPROVER"],
    orderByRole: { PLANNER: 7, APPROVER: 2 },
  },
  {
    id: "roi",
    label: "ROI Tracker",
    path: "/roi",
    description: "Impact notes and reviews.",
    rolesVisible: ["PLANNER", "APPROVER"],
    orderByRole: { PLANNER: 8, APPROVER: 5 },
  },
];

export function getNavItemsForRole(role: UserRole): NavItem[] {
  return NAV_ITEMS.filter((item) => item.rolesVisible.includes(role)).sort((a, b) => {
    const aOrder = a.orderByRole?.[role] ?? Number.MAX_SAFE_INTEGER;
    const bOrder = b.orderByRole?.[role] ?? Number.MAX_SAFE_INTEGER;
    if (aOrder === bOrder) return a.label.localeCompare(b.label);
    return aOrder - bOrder;
  });
}
