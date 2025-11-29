import { NAV_ITEMS, getNavItemsForRole, type NavItem } from "@/config/navigation";
import type { UserRole } from "@/types/domain";

export const navItems = NAV_ITEMS;

export { NAV_ITEMS, getNavItemsForRole, type NavItem };

export function navItemsForRole(role: UserRole) {
  return getNavItemsForRole(role);
}
