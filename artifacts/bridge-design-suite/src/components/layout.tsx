import { Link, useLocation } from "wouter";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
} from "@/components/ui/sidebar";
import { Activity, Copy, FileText, Home, FolderTree } from "lucide-react";

export function AppLayout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-background font-sans text-foreground selection:bg-primary selection:text-primary-foreground">
        <Sidebar className="border-r border-border">
          <SidebarContent>
            <div className="flex h-14 items-center px-4 font-mono font-bold text-lg tracking-tight border-b border-border text-primary">
              BRIDGE<span className="text-muted-foreground ml-1 font-normal">SUITE</span>
            </div>
            <SidebarGroup>
              <SidebarGroupLabel className="text-xs font-mono text-muted-foreground uppercase tracking-wider mt-4 mb-2 px-2">
                Workspace
              </SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem>
                    <SidebarMenuButton asChild isActive={location === "/"}>
                      <Link href="/">
                        <Home className="h-4 w-4" />
                        <span>Dashboard</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton asChild isActive={location.startsWith("/projects")}>
                      <Link href="/projects">
                        <FolderTree className="h-4 w-4" />
                        <span>Projects</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton asChild isActive={location.startsWith("/files")}>
                      <Link href="/files">
                        <FileText className="h-4 w-4" />
                        <span>File Library</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton asChild isActive={location.startsWith("/records")}>
                      <Link href="/records">
                        <Activity className="h-4 w-4" />
                        <span>Analysis Records</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton asChild isActive={location.startsWith("/comparisons")}>
                      <Link href="/comparisons">
                        <Copy className="h-4 w-4" />
                        <span>Comparisons</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
        </Sidebar>
        <main className="flex-1 flex flex-col min-h-screen min-w-0">
          <div className="flex-1 p-6 lg:p-8">
            <div className="mx-auto max-w-6xl">
              {children}
            </div>
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
}
