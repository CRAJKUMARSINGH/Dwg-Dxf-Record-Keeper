import { useGetStatsSummary, useListVariations, getGetStatsSummaryQueryKey, getListVariationsQueryKey } from "@workspace/api-client-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, FolderTree, Activity, Copy, FileCode2, FileSearch, Layers } from "lucide-react";
import { Link } from "wouter";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";

export default function Home() {
  const { data: stats, isLoading: statsLoading } = useGetStatsSummary({
    query: {
      queryKey: getGetStatsSummaryQueryKey()
    }
  });

  const { data: variationsRaw, isLoading: variationsLoading } = useListVariations({
    query: {
      queryKey: getListVariationsQueryKey()
    }
  });
  const variations = Array.isArray(variationsRaw) ? variationsRaw : [];

  if (statsLoading || variationsLoading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-4" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-16" />
              </CardContent>
            </Card>
          ))}
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
          <Card className="col-span-4">
            <CardHeader>
              <Skeleton className="h-6 w-32 mb-2" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-[300px] w-full" />
            </CardContent>
          </Card>
          <Card className="col-span-3">
            <CardHeader>
              <Skeleton className="h-6 w-32 mb-2" />
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[1, 2, 3, 4].map((i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">
          DXF studio, projects, drawing library, and analysis records in one workspace.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="md:col-span-2 border-primary/25 bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent shadow-sm">
          <CardHeader className="pb-3">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div className="space-y-1">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                    <Layers className="h-4 w-4" />
                  </span>
                  DXF drawing studio
                </CardTitle>
                <CardDescription className="text-sm leading-relaxed max-w-xl">
                  Nine-sheet RCC slab bridge generator: IRC-oriented GAD, plan, sections, pier and abutment, rebar BBS, wing walls,
                  bed protection — with scan-to-parameters when your API is running.
                </CardDescription>
              </div>
              <Button asChild className="shrink-0">
                <Link href="/generator">Open DXF studio</Link>
              </Button>
            </div>
          </CardHeader>
        </Card>
        <Card className="shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Record keeper</CardTitle>
            <CardDescription>Organise drawings and analyses alongside generation.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            <Button variant="outline" size="sm" className="justify-start" asChild>
              <Link href="/projects">
                <FolderTree className="h-4 w-4 mr-2 shrink-0" />
                Projects
              </Link>
            </Button>
            <Button variant="outline" size="sm" className="justify-start" asChild>
              <Link href="/files">
                <FileText className="h-4 w-4 mr-2 shrink-0" />
                File library
              </Link>
            </Button>
            <Button variant="outline" size="sm" className="justify-start" asChild>
              <Link href="/records">
                <Activity className="h-4 w-4 mr-2 shrink-0" />
                Analysis records
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
            <FolderTree className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalProjects}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Files Processed</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalFiles}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Analysis Records</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalRecords}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Comparisons</CardTitle>
            <Copy className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalComparisons}</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Files by Type</CardTitle>
          </CardHeader>
          <CardContent className="pl-2">
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.filesByType}>
                  <XAxis dataKey="label" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                  <Tooltip cursor={{fill: 'var(--muted)'}} contentStyle={{backgroundColor: 'hsl(var(--popover))', border: '1px solid hsl(var(--border))', borderRadius: 'var(--radius)'}} />
                  <Bar dataKey="count" fill="currentColor" radius={[4, 4, 0, 0]} className="fill-primary" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Recent Files</CardTitle>
            <CardDescription>
              Recently added or updated design files.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.recentFiles?.map((file) => (
                <div key={file.id} className="flex items-center">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg border bg-muted">
                    {file.fileType.toLowerCase() === 'dxf' ? (
                      <FileCode2 className="h-4 w-4 text-blue-500" />
                    ) : (
                      <FileText className="h-4 w-4 text-red-500" />
                    )}
                  </div>
                  <div className="ml-4 space-y-1 flex-1 overflow-hidden">
                    <Link href={`/files/${file.id}`} className="text-sm font-medium leading-none hover:underline truncate block">
                      {file.fileName}
                    </Link>
                    <p className="text-xs text-muted-foreground truncate">
                      {file.bridgeType || 'Unknown type'}
                    </p>
                  </div>
                  <Badge variant="outline">{file.analysisStatus}</Badge>
                </div>
              ))}
              {(!stats.recentFiles || stats.recentFiles.length === 0) && (
                <div className="text-sm text-muted-foreground text-center py-4">
                  No files uploaded yet.
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Variation Patterns</CardTitle>
          <CardDescription>Common design variations across projects</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {variations?.map((pattern) => (
              <div key={pattern.variationType} className="rounded-lg border p-4 hover-elevate">
                <div className="flex items-center justify-between mb-2">
                  <div className="font-semibold">{pattern.variationType}</div>
                  <Badge variant="secondary">{pattern.count}</Badge>
                </div>
                <div className="space-y-2 mt-4">
                  {pattern.examples?.slice(0, 3).map(example => (
                    <Link key={example.id} href={`/records/${example.id}`} className="flex items-center text-sm text-muted-foreground hover:text-foreground">
                      <FileSearch className="mr-2 h-3 w-3" />
                      <span className="truncate">{example.title}</span>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
