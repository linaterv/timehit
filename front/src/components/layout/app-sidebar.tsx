"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Clock,
  CheckSquare,
  FileText,
  Briefcase,
  Users,
  Building2,
  Shield,
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

const mainNavItems = [
  { title: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { title: "Timesheets", href: "/timesheets", icon: Clock },
  { title: "Approvals", href: "/approvals", icon: CheckSquare },
  { title: "Invoices", href: "/invoices", icon: FileText },
  { title: "Placements", href: "/placements", icon: Briefcase },
  { title: "Contractors", href: "/contractors", icon: Users },
  { title: "Clients", href: "/clients", icon: Building2 },
];

const adminNavItems = [
  { title: "Users", href: "/admin/users", icon: Shield },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <Sidebar data-testid="app-sidebar">
      <SidebarHeader className="border-b px-4 py-3">
        <Link
          href="/"
          className="flex items-center gap-2 font-bold text-lg"
          data-testid="sidebar-logo"
        >
          <Clock className="h-6 w-6" />
          <span>TimeHit</span>
        </Link>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainNavItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    isActive={pathname.startsWith(item.href)}
                    render={
                      <Link
                        href={item.href}
                        data-testid={`sidebar-nav-${item.title.toLowerCase()}`}
                      />
                    }
                    tooltip={item.title}
                  >
                    <item.icon />
                    <span>{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupLabel>Admin</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {adminNavItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    isActive={pathname.startsWith(item.href)}
                    render={
                      <Link
                        href={item.href}
                        data-testid={`sidebar-nav-admin-${item.title.toLowerCase()}`}
                      />
                    }
                    tooltip={item.title}
                  >
                    <item.icon />
                    <span>{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
