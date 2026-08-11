"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Briefcase,
  Building2,
  BarChart3,
  User as UserIcon,
  Users,
  Menu,
  X,
  LogOut,
  ChevronDown,
} from "lucide-react";
import { Avatar } from "@/components/ui";
import type { User } from "@/lib/types";

/**
 * Dashboard chrome: sidebar nav, mobile drawer and the user menu.
 *
 * Split out of the layout because these need `useState`/`usePathname`; the layout
 * itself stays a Server Component so it can await the user without shipping the
 * fetch to the browser.
 *
 * `user` arrives as a prop from that server fetch. The SvelteKit version instead
 * read from `authStore` and mirrored the user into localStorage, re-syncing it in
 * `onMount` — all of which existed only because the layout had no server-rendered
 * user. That store is gone (MIGRATION.md § Auth).
 */

const baseNavItems = [
  { href: "/dashboard/", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/dashboard/jobs/", icon: Briefcase, label: "Jobs" },
  { href: "/dashboard/analytics/", icon: BarChart3, label: "Analytics" },
  { href: "/dashboard/account/", icon: UserIcon, label: "Account" },
];

const companyNavItem = {
  href: "/dashboard/company/",
  icon: Building2,
  label: "Company",
};
const teamNavItem = { href: "/dashboard/team/", icon: Users, label: "Team" };

export interface SidebarProps {
  user: User;
  /** Server Action that clears the session cookies and redirects to /login/. */
  logoutAction: () => Promise<void>;
}

export function Sidebar({ user, logoutAction }: SidebarProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const pathname = usePathname();

  // Company and Team are only meaningful for recruiters attached to a company.
  const navItems = user.company
    ? [
        baseNavItems[0], // Dashboard
        baseNavItems[1], // Jobs
        companyNavItem,
        teamNavItem,
        baseNavItems[2], // Analytics
        baseNavItems[3], // Account
      ]
    : baseNavItems;

  const isActive = (href: string) =>
    href === "/dashboard/" ? pathname === "/dashboard/" : pathname.startsWith(href);

  return (
    <>
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-0 left-0 right-0 bg-white border-b border-border z-40 px-4 py-3">
        <button
          type="button"
          onClick={() => setSidebarOpen((open) => !open)}
          className="p-2 rounded-lg text-muted hover:bg-surface transition-colors"
          aria-label="Toggle menu"
          aria-expanded={sidebarOpen}
        >
          {sidebarOpen ? (
            <X className="w-6 h-6" />
          ) : (
            <Menu className="w-6 h-6" />
          )}
        </button>
      </div>

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 bottom-0 w-64 bg-white border-r border-border z-30 transform transition-transform duration-200 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        <div className="h-full flex flex-col">
          {/* Logo */}
          <div className="h-16 flex items-center px-6 border-b border-border">
            <Link href="/dashboard/" className="text-xl font-bold text-primary">
              PeelJobs
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto py-4">
            <ul className="space-y-1 px-3">
              {navItems.map((item) => {
                const active = isActive(item.href);
                const Icon = item.icon;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      aria-current={active ? "page" : undefined}
                      className={`flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-colors ${
                        active
                          ? "bg-primary/10 text-primary"
                          : "text-muted hover:bg-surface hover:text-black"
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* User section */}
          <div className="border-t border-border p-4">
            <div className="relative">
              {/* Explicit type: a <button> with no type attribute reports
                  type="submit". Harmless while it sits outside a form, but it
                  would start submitting one the moment it didn't. */}
              <button
                type="button"
                onClick={() => setUserMenuOpen((open) => !open)}
                className="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-surface transition-colors"
                aria-expanded={userMenuOpen}
              >
                <Avatar
                  name={`${user.first_name || "U"} ${user.last_name || ""}`}
                  size="md"
                />
                <div className="flex-1 min-w-0 text-left">
                  <p className="text-sm font-medium text-black truncate">
                    {user.first_name || "User"} {user.last_name || ""}
                  </p>
                  <p className="text-xs text-muted truncate">
                    {user.company?.name || "Independent Recruiter"}
                  </p>
                </div>
                <ChevronDown
                  className={`w-4 h-4 text-muted flex-shrink-0 transition-transform duration-200 ${
                    userMenuOpen ? "rotate-180" : ""
                  }`}
                />
              </button>

              {/* Dropdown menu */}
              {userMenuOpen && (
                <div className="absolute bottom-full left-0 right-0 mb-2 bg-white rounded-lg shadow-lg border border-border py-1">
                  <Link
                    href="/dashboard/account/"
                    className="flex items-center gap-2 px-4 py-2 text-sm text-muted hover:bg-surface hover:text-black transition-colors"
                  >
                    <UserIcon className="w-4 h-4" />
                    Account Settings
                  </Link>
                  <form action={logoutAction}>
                    <button
                      type="submit"
                      className="w-full flex items-center gap-2 px-4 py-2 text-sm text-error hover:bg-error-light transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      Logout
                    </button>
                  </form>
                </div>
              )}
            </div>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <button
          type="button"
          aria-label="Close menu"
          className="fixed inset-0 bg-black/50 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </>
  );
}

export default Sidebar;
