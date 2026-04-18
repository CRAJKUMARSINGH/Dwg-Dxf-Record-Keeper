import { useState } from "react";
import { useRoute, Link } from "wouter";
import { 
  useGetAnalysisRecord, 
  getGetAnalysisRecordQueryKey,
  useUpdateAnalysisRecord,
  useGetFileRecord,
  getGetFileRecordQueryKey,
  useGetProject,
  getGetProjectQueryKey
} from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, Activity, Star, Calendar, FileText, FolderTree } from "lucide-react";

export default function RecordDetail() {
  const [, params] = useRoute("/records/:id");
  const id = parseInt(params?.id || "0");
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: record, isLoading: recordLoading } = useGetAnalysisRecord(id, {
    query: {
      enabled: !!id,
      queryKey: getGetAnalysisRecordQueryKey(id)
    }
  });

  const { data: file, isLoading: fileLoading } = useGetFileRecord(record?.fileId || 0, {
    query: {
      enabled: !!record?.fileId,
      queryKey: getGetFileRecordQueryKey(record?.fileId || 0)
    }
  });

  const { data: project, isLoading: projectLoading } = useGetProject(record?.projectId || 0, {
    query: {
      enabled: !!record?.projectId,
      queryKey: getGetProjectQueryKey(record?.projectId || 0)
    }
  });

  const updateRecord = useUpdateAnalysisRecord();

  function toggleFavorite() {
    if (!record) return;
    updateRecord.mutate({ id, data: { isFavorite: !record.isFavorite } }, {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getGetAnalysisRecordQueryKey(id) });
        toast({
          title: record.isFavorite ? "Removed from favorites" : "Added to favorites",
          description: "Record status updated."
        });
      }
    });
  }

  if (recordLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10 rounded-md" />
          <div>
            <Skeleton className="h-8 w-64 mb-2" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>
        <Skeleton className="h-[300px] w-full rounded-lg" />
      </div>
    );
  }

  if (!record) return <div>Analysis record not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" asChild>
            <Link href="/records">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg border bg-muted shrink-0">
              <Activity className="h-6 w-6 text-primary" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-2xl font-bold tracking-tight">{record.title}</h2>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className={`h-8 w-8 ${record.isFavorite ? 'text-yellow-500 hover:text-yellow-600' : 'text-muted-foreground/50 hover:text-yellow-500'}`}
                  onClick={toggleFavorite}
                >
                  <Star className={`h-5 w-5 ${record.isFavorite ? 'fill-current' : ''}`} />
                </Button>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                <Badge variant="outline">{record.variationType}</Badge>
                <span>•</span>
                <span>Created {format(new Date(record.createdAt), 'MMM d, yyyy')}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Description</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm whitespace-pre-wrap">{record.description || "No description provided."}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Parameters</CardTitle>
              <CardDescription>Extracted key-value pairs or raw text</CardDescription>
            </CardHeader>
            <CardContent>
              {record.parameters ? (
                <pre className="text-xs bg-muted p-4 rounded-lg overflow-x-auto font-mono whitespace-pre-wrap border border-border">
                  {record.parameters}
                </pre>
              ) : (
                <div className="text-center py-4 text-muted-foreground text-sm border border-dashed rounded-lg">
                  No parameters defined for this record.
                </div>
              )}
            </CardContent>
          </Card>

          {record.notes && (
            <Card>
              <CardHeader>
                <CardTitle>Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm whitespace-pre-wrap">{record.notes}</p>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Context</CardTitle>
              <CardDescription>Associated entities</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {record.fileId && (
                <div className="space-y-2">
                  <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-1">
                    <FileText className="h-3 w-3" /> Source File
                  </h4>
                  {fileLoading ? (
                    <Skeleton className="h-10 w-full" />
                  ) : file ? (
                    <Link href={`/files/${file.id}`} className="flex items-center gap-2 p-2 border rounded-md hover:bg-muted/50 transition-colors">
                      <FileText className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-medium truncate">{file.fileName}</span>
                    </Link>
                  ) : (
                    <div className="text-sm text-muted-foreground">File not found</div>
                  )}
                </div>
              )}

              {record.projectId && (
                <div className="space-y-2">
                  <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-1 mt-4">
                    <FolderTree className="h-3 w-3" /> Project
                  </h4>
                  {projectLoading ? (
                    <Skeleton className="h-10 w-full" />
                  ) : project ? (
                    <Link href={`/projects/${project.id}`} className="flex items-center gap-2 p-2 border rounded-md hover:bg-muted/50 transition-colors">
                      <FolderTree className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-medium truncate">{project.name}</span>
                    </Link>
                  ) : (
                    <div className="text-sm text-muted-foreground">Project not found</div>
                  )}
                </div>
              )}
              
              {!record.fileId && !record.projectId && (
                <div className="text-sm text-muted-foreground text-center py-2">
                  This record is standalone and not linked to any files or projects.
                </div>
              )}
            </CardContent>
          </Card>
          
          {record.referenceFiles && (
             <Card>
             <CardHeader>
               <CardTitle>Reference Files</CardTitle>
             </CardHeader>
             <CardContent>
               <p className="text-sm">{record.referenceFiles}</p>
             </CardContent>
           </Card>
          )}
        </div>
      </div>
    </div>
  );
}
