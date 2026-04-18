import { useState } from "react";
import { useRoute, Link } from "wouter";
import { 
  useGetFileRecord, getGetFileRecordQueryKey,
  useGetSimilarFiles, getGetSimilarFilesQueryKey,
  useListAnalysisRecords, getListAnalysisRecordsQueryKey,
  useUpdateFileRecord,
  useCreateAnalysisRecord
} from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { 
  ArrowLeft, FileText, Activity, FileCode2, Plus, ArrowRight, Save
} from "lucide-react";

const analysisRecordSchema = z.object({
  title: z.string().min(1, "Title is required"),
  variationType: z.string().min(1, "Variation type is required"),
  description: z.string().optional(),
  parameters: z.string().optional(),
  notes: z.string().optional(),
  isFavorite: z.boolean().default(false)
});

export default function FileDetail() {
  const [, params] = useRoute("/files/:id");
  const id = parseInt(params?.id || "0");
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [createRecordOpen, setCreateRecordOpen] = useState(false);

  const { data: file, isLoading: fileLoading } = useGetFileRecord(id, {
    query: {
      enabled: !!id,
      queryKey: getGetFileRecordQueryKey(id)
    }
  });

  const { data: similarFiles, isLoading: similarFilesLoading } = useGetSimilarFiles(id, {
    query: {
      enabled: !!id,
      queryKey: getGetSimilarFilesQueryKey(id)
    }
  });

  const { data: records, isLoading: recordsLoading } = useListAnalysisRecords({ fileId: id }, {
    query: {
      enabled: !!id,
      queryKey: getListAnalysisRecordsQueryKey({ fileId: id })
    }
  });

  const createRecord = useCreateAnalysisRecord();

  const form = useForm<z.infer<typeof analysisRecordSchema>>({
    resolver: zodResolver(analysisRecordSchema),
    defaultValues: {
      title: "",
      variationType: "",
      description: "",
      parameters: "",
      notes: "",
      isFavorite: false
    }
  });

  function onCreateRecord(values: z.infer<typeof analysisRecordSchema>) {
    createRecord.mutate({ 
      data: { 
        ...values, 
        fileId: id,
        projectId: file?.projectId
      } 
    }, {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getListAnalysisRecordsQueryKey({ fileId: id }) });
        setCreateRecordOpen(false);
        form.reset();
        toast({
          title: "Record created",
          description: "Analysis record has been successfully saved."
        });
      },
      onError: () => {
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to create record. Please try again."
        });
      }
    });
  }

  if (fileLoading) {
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

  if (!file) return <div>File not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" asChild>
            <Link href="/files">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg border bg-muted shrink-0">
              {file.fileType.toLowerCase() === 'dxf' ? (
                <FileCode2 className="h-6 w-6 text-blue-500" />
              ) : (
                <FileText className="h-6 w-6 text-red-500" />
              )}
            </div>
            <div>
              <h2 className="text-2xl font-bold tracking-tight">{file.fileName}</h2>
              <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                <Badge variant={file.analysisStatus === 'completed' ? "default" : file.analysisStatus === 'failed' ? "destructive" : "secondary"}>
                  {file.analysisStatus}
                </Badge>
                <span>•</span>
                <span>{file.fileSizeKb ? `${(file.fileSizeKb / 1024).toFixed(2)} MB` : 'Unknown size'}</span>
                {file.projectId && (
                  <>
                    <span>•</span>
                    <Link href={`/projects/${file.projectId}`} className="hover:underline">Project #{file.projectId}</Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
        
        <Dialog open={createRecordOpen} onOpenChange={setCreateRecordOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Record
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create Analysis Record</DialogTitle>
              <DialogDescription>
                Extract a variation or design pattern from this file to memorize.
              </DialogDescription>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onCreateRecord)} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="title"
                    render={({ field }) => (
                      <FormItem className="col-span-2 sm:col-span-1">
                        <FormLabel>Title</FormLabel>
                        <FormControl>
                          <Input placeholder="e.g. Deck reinforcement pattern" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="variationType"
                    render={({ field }) => (
                      <FormItem className="col-span-2 sm:col-span-1">
                        <FormLabel>Variation Type</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select type" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="material_substitution">Material Substitution</SelectItem>
                            <SelectItem value="span_adjustment">Span Adjustment</SelectItem>
                            <SelectItem value="load_capacity">Load Capacity</SelectItem>
                            <SelectItem value="geometric_change">Geometric Change</SelectItem>
                            <SelectItem value="other">Other</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="description"
                    render={({ field }) => (
                      <FormItem className="col-span-2">
                        <FormLabel>Description</FormLabel>
                        <FormControl>
                          <Textarea placeholder="Describe this design variation..." {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="parameters"
                    render={({ field }) => (
                      <FormItem className="col-span-2">
                        <FormLabel>Extracted Parameters (JSON or text)</FormLabel>
                        <FormControl>
                          <Textarea className="font-mono text-xs" placeholder='{"rebar_density": 1.5, "concrete_grade": "C40"}' {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <DialogFooter>
                  <Button type="submit" disabled={createRecord.isPending}>
                    {createRecord.isPending ? "Saving..." : "Save Record"}
                  </Button>
                </DialogFooter>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Extracted Parameters</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-6">
                <div>
                  <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Bridge Type</h4>
                  <p className="text-sm font-medium">{file.bridgeType || "—"}</p>
                </div>
                <div>
                  <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Span Length</h4>
                  <p className="text-sm font-medium">{file.spanLength ? `${file.spanLength} m` : "—"}</p>
                </div>
                <div>
                  <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Dimensions</h4>
                  <p className="text-sm font-medium">
                    {file.width && file.height ? `${file.width}m × ${file.height}m` : "—"}
                  </p>
                </div>
                <div>
                  <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Material</h4>
                  <p className="text-sm font-medium">{file.material || "—"}</p>
                </div>
                <div>
                  <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Load Capacity</h4>
                  <p className="text-sm font-medium">{file.loadCapacity ? `${file.loadCapacity} kN` : "—"}</p>
                </div>
                <div>
                  <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Design Code</h4>
                  <p className="text-sm font-medium">{file.designCode || "—"}</p>
                </div>
              </div>
              
              {file.extractedData && (
                <div className="mt-6 pt-6 border-t">
                  <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">Raw Extracted Data</h4>
                  <pre className="text-xs bg-muted p-4 rounded-lg overflow-x-auto">
                    {file.extractedData}
                  </pre>
                </div>
              )}
            </CardContent>
          </Card>

          <Tabs defaultValue="records">
            <TabsList>
              <TabsTrigger value="records">Analysis Records</TabsTrigger>
            </TabsList>
            <TabsContent value="records" className="mt-4">
              <Card>
                <CardContent className="pt-6">
                  {recordsLoading ? (
                    <div className="space-y-4">
                      <Skeleton className="h-16 w-full" />
                      <Skeleton className="h-16 w-full" />
                    </div>
                  ) : records?.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      No analysis records found for this file.
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {records?.map(record => (
                        <div key={record.id} className="flex items-center justify-between p-4 border rounded-lg">
                          <div>
                            <Link href={`/records/${record.id}`} className="font-medium hover:underline block mb-1">
                              {record.title}
                            </Link>
                            <Badge variant="outline" className="text-xs">{record.variationType}</Badge>
                          </div>
                          <Button variant="ghost" size="icon" asChild>
                            <Link href={`/records/${record.id}`}>
                              <ArrowRight className="h-4 w-4" />
                            </Link>
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Similar Files</CardTitle>
              <CardDescription>Based on extracted parameters</CardDescription>
            </CardHeader>
            <CardContent>
              {similarFilesLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map(i => <Skeleton key={i} className="h-12 w-full" />)}
                </div>
              ) : similarFiles?.length === 0 ? (
                <div className="text-sm text-muted-foreground text-center py-4">
                  No similar files found.
                </div>
              ) : (
                <div className="space-y-3">
                  {similarFiles?.map(similar => (
                    <div key={similar.id} className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded bg-muted shrink-0">
                        {similar.fileType.toLowerCase() === 'dxf' ? (
                          <FileCode2 className="h-4 w-4 text-blue-500" />
                        ) : (
                          <FileText className="h-4 w-4 text-red-500" />
                        )}
                      </div>
                      <div className="overflow-hidden flex-1">
                        <Link href={`/files/${similar.id}`} className="text-sm font-medium hover:underline truncate block">
                          {similar.fileName}
                        </Link>
                        <p className="text-xs text-muted-foreground truncate">{similar.bridgeType}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
