import { useRoute, Link } from "wouter";
import { 
  useGetComparison, 
  getGetComparisonQueryKey,
  useListFiles,
  getListFilesQueryKey
} from "@workspace/api-client-react";
import { format } from "date-fns";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft, GitCompare, FileText, Calendar, Info, FileCode2 } from "lucide-react";

export default function ComparisonDetail() {
  const [, params] = useRoute("/comparisons/:id");
  const id = parseInt(params?.id || "0");

  const { data: comparison, isLoading: comparisonLoading } = useGetComparison(id, {
    query: {
      enabled: !!id,
      queryKey: getGetComparisonQueryKey(id)
    }
  });

  const { data: allFiles, isLoading: filesLoading } = useListFiles({}, {
    query: {
      queryKey: getListFilesQueryKey({})
    }
  });

  if (comparisonLoading || filesLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10 rounded-md" />
          <div>
            <Skeleton className="h-8 w-64 mb-2" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          <Skeleton className="h-[300px] w-full rounded-lg" />
          <Skeleton className="h-[300px] w-full rounded-lg" />
        </div>
      </div>
    );
  }

  if (!comparison) return <div>Comparison not found</div>;

  const fileIds = comparison.fileIds.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id));
  const comparedFiles = allFiles?.filter(file => fileIds.includes(file.id)) || [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" asChild>
            <Link href="/comparisons">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg border bg-muted shrink-0">
              <GitCompare className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h2 className="text-2xl font-bold tracking-tight">{comparison.title}</h2>
              <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                <span>Created {format(new Date(comparison.createdAt), 'MMM d, yyyy')}</span>
                {comparison.projectId && (
                  <>
                    <span>•</span>
                    <Link href={`/projects/${comparison.projectId}`} className="hover:underline">Project #{comparison.projectId}</Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Differences</CardTitle>
            <CardDescription>Extracted divergent parameters between the files.</CardDescription>
          </CardHeader>
          <CardContent>
            {comparison.differencesSummary ? (
              <p className="text-sm whitespace-pre-wrap">{comparison.differencesSummary}</p>
            ) : (
              <div className="text-center py-4 text-muted-foreground text-sm border border-dashed rounded-lg">
                No differences summary available.
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Similarities</CardTitle>
            <CardDescription>Common parameters across the files.</CardDescription>
          </CardHeader>
          <CardContent>
            {comparison.similaritiesSummary ? (
              <p className="text-sm whitespace-pre-wrap">{comparison.similaritiesSummary}</p>
            ) : (
              <div className="text-center py-4 text-muted-foreground text-sm border border-dashed rounded-lg">
                No similarities summary available.
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {comparison.notes && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Info className="h-4 w-4" /> Context & Notes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm whitespace-pre-wrap">{comparison.notes}</p>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Files Compared ({comparedFiles.length})</CardTitle>
          <CardDescription>The specific source files included in this comparison.</CardDescription>
        </CardHeader>
        <CardContent>
          {comparedFiles.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground border-2 border-dashed rounded-lg">
              Files not found or deleted.
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {comparedFiles.map(file => (
                <div key={file.id} className="flex items-center p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg border bg-background shrink-0">
                    {file.fileType.toLowerCase() === 'dxf' ? (
                      <FileCode2 className="h-5 w-5 text-blue-500" />
                    ) : (
                      <FileText className="h-5 w-5 text-red-500" />
                    )}
                  </div>
                  <div className="ml-4 overflow-hidden flex-1">
                    <Link href={`/files/${file.id}`} className="font-medium hover:underline text-sm leading-none block mb-1 truncate">
                      {file.fileName}
                    </Link>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span>{file.bridgeType || 'Unknown type'}</span>
                      <span>•</span>
                      <span>{file.fileSizeKb ? `${(file.fileSizeKb / 1024).toFixed(2)} MB` : 'Unknown size'}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
