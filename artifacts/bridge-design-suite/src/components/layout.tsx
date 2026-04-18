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
import { Activity, Copy, FileText, Home, FolderTree, Layers } from "lucide-react";
import { cn } from "@/lib/utils";

export function AppLayout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();
  const isStudio = location.startsWith("/generator");

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-background font-sans text-foreground selection:bg-primary selection:text-primary-foreground">
        <Sidebar className="border-r border-border">
          <SidebarContent>
            <div className="flex flex-col gap-0.5 px-4 py-3 border-b border-border">
              <div className="font-mono font-bold text-lg tracking-tight text-primary leading-tight">
                BRIDGE<span className="text-muted-foreground ml-1 font-normal">DESIGN</span>
              </div>
              <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider leading-snug">
                Suite · records · DXF studio
              </div>
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
                  <SidebarMenuItem>
                    <SidebarMenuButton asChild isActive={location.startsWith("/generator")}>
                      <Link href="/generator">
                        <Layers className="h-4 w-4" />
                        <span>DXF studio</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
        </Sidebar>
        <main className="flex-1 flex flex-col min-h-screen min-w-0">
          <div className={cn("flex-1", isStudio ? "p-3 sm:p-4 lg:p-5" : "p-6 lg:p-8")}>
            <div
              className={cn(
                "mx-auto w-full",
                isStudio ? "max-w-[1920px]" : "max-w-6xl",
              )}
            >
              {children}
            </div>
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
}
