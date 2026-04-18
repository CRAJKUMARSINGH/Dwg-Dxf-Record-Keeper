import { useState } from "react";
import { useRoute, Link } from "wouter";
import { 
  useGetProject, getGetProjectQueryKey,
  useListFiles, getListFilesQueryKey,
  useListAnalysisRecords, getListAnalysisRecordsQueryKey,
  useUpdateProject,
  useCreateFileRecord
} from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { 
  ArrowLeft, Building2, MapPin, Calendar, FileText, Activity, 
  Settings, CheckCircle2, Circle, Clock, FileCode2, Plus
} from "lucide-react";

const fileRecordSchema = z.object({
  fileName: z.string().min(1, "File name is required"),
  fileType: z.enum(["dxf", "pdf"]),
  bridgeType: z.string().optional(),
  spanLength: z.coerce.number().optional(),
  width: z.coerce.number().optional(),
  height: z.coerce.number().optional(),
  material: z.string().optional(),
  loadCapacity: z.coerce.number().optional(),
  designCode: z.string().optional(),
});

export default function ProjectDetail() {
  const [, params] = useRoute("/projects/:id");
  const id = parseInt(params?.id || "0");
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [uploadOpen, setUploadOpen] = useState(false);

  const { data: project, isLoading: projectLoading } = useGetProject(id, {
    query: {
      enabled: !!id,
      queryKey: getGetProjectQueryKey(id)
    }
  });

  const { data: files, isLoading: filesLoading } = useListFiles({ projectId: id }, {
    query: {
      enabled: !!id,
      queryKey: getListFilesQueryKey({ projectId: id })
    }
  });

  const { data: records, isLoading: recordsLoading } = useListAnalysisRecords({ projectId: id }, {
    query: {
      enabled: !!id,
      queryKey: getListAnalysisRecordsQueryKey({ projectId: id })
    }
  });

  const createFileRecord = useCreateFileRecord();

  const form = useForm<z.infer<typeof fileRecordSchema>>({
    resolver: zodResolver(fileRecordSchema),
    defaultValues: {
      fileName: "",
      fileType: "pdf",
      bridgeType: "",
    }
  });

  function onUploadSubmit(values: z.infer<typeof fileRecordSchema>) {
    createFileRecord.mutate({ 
      data: { 
        ...values, 
        projectId: id,
        analysisStatus: "pending",
        fileSizeKb: Math.floor(Math.random() * 5000) + 100 // dummy size
      } 
    }, {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getListFilesQueryKey({ projectId: id }) });
        queryClient.invalidateQueries({ queryKey: getGetProjectQueryKey(id) });
        setUploadOpen(false);
        form.reset();
        toast({
          title: "File added",
          description: "The design file has been added to the project."
        });
      },
      onError: () => {
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to add file. Please try again."
        });
      }
    });
  }

  if (projectLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10 rounded-md" />
          <div>
            <Skeleton className="h-8 w-64 mb-2" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>
        <Skeleton className="h-[200px] w-full rounded-lg" />
      </div>
    );
  }

  if (!project) return <div>Project not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" asChild>
            <Link href="/projects">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h2 className="text-2xl font-bold tracking-tight">{project.name}</h2>
            <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
              <Badge variant={project.status === 'completed' ? "default" : project.status === 'active' ? "secondary" : "outline"}>
                {project.status.replace("_", " ")}
              </Badge>
              <span>•</span>
              <span>Created {format(new Date(project.createdAt), 'MMM d, yyyy')}</span>
            </div>
          </div>
        </div>
        
        <Dialog open={uploadOpen} onOpenChange={setUploadOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Upload File
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Upload Design File</DialogTitle>
              <DialogDescription>
                Add a new DXF or PDF drawing to this project and extract initial parameters.
              </DialogDescription>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onUploadSubmit)} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="fileName"
                    render={({ field }) => (
                      <FormItem className="col-span-2 sm:col-span-1">
                        <FormLabel>File Name</FormLabel>
                        <FormControl>
                          <Input placeholder="e.g. deck_plan_v2.dxf" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="fileType"
                    render={({ field }) => (
                      <FormItem className="col-span-2 sm:col-span-1">
                        <FormLabel>File Type</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select type" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="dxf">DXF (AutoCAD)</SelectItem>
                            <SelectItem value="pdf">PDF</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="bridgeType"
                    render={({ field }) => (
                      <FormItem className="col-span-2 sm:col-span-1">
                        <FormLabel>Bridge Type</FormLabel>
                        <FormControl>
                          <Input placeholder="e.g. Suspension" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="material"
                    render={({ field }) => (
                      <FormItem className="col-span-2 sm:col-span-1">
                        <FormLabel>Primary Material</FormLabel>
                        <FormControl>
                          <Input placeholder="e.g. Steel, Concrete" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="spanLength"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Span Length (m)</FormLabel>
                        <FormControl>
                          <Input type="number" placeholder="0.0" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="width"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Width (m)</FormLabel>
                        <FormControl>
                          <Input type="number" placeholder="0.0" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <DialogFooter>
                  <Button type="submit" disabled={createFileRecord.isPending}>
                    {createFileRecord.isPending ? "Uploading..." : "Upload File"}
                  </Button>
                </DialogFooter>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-4 md:col-span-2">
              <div>
                <h3 className="text-sm font-medium text-muted-foreground mb-1">Description</h3>
                <p className="text-sm">{project.description || "No description provided."}</p>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-4 border-t">
                <div>
                  <h3 className="text-xs font-medium text-muted-foreground mb-1 flex items-center gap-1"><Building2 className="h-3 w-3"/> Type</h3>
                  <p className="text-sm font-medium">{project.bridgeType || "—"}</p>
                </div>
                <div>
                  <h3 className="text-xs font-medium text-muted-foreground mb-1 flex items-center gap-1"><MapPin className="h-3 w-3"/> Location</h3>
                  <p className="text-sm font-medium">{project.location || "—"}</p>
                </div>
                <div>
                  <h3 className="text-xs font-medium text-muted-foreground mb-1 flex items-center gap-1"><Calendar className="h-3 w-3"/> Last Updated</h3>
                  <p className="text-sm font-medium">{format(new Date(project.updatedAt), 'MMM d, yyyy')}</p>
                </div>
              </div>
            </div>
            <div className="flex flex-col justify-center space-y-4 md:border-l md:pl-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Files</span>
                </div>
                <span className="text-2xl font-bold">{project.fileCount}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Records</span>
                </div>
                <span className="text-2xl font-bold">{project.recordCount}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="files" className="w-full">
        <TabsList>
          <TabsTrigger value="files">Files ({project.fileCount})</TabsTrigger>
          <TabsTrigger value="records">Analysis Records ({project.recordCount})</TabsTrigger>
        </TabsList>
        <TabsContent value="files" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Project Files</CardTitle>
              <CardDescription>All DXF and PDF files uploaded to this project.</CardDescription>
            </CardHeader>
            <CardContent>
              {filesLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map(i => <Skeleton key={i} className="h-16 w-full" />)}
                </div>
              ) : files?.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground border-2 border-dashed rounded-lg">
                  No files uploaded yet.
                </div>
              ) : (
                <div className="space-y-4">
                  {files?.map(file => (
                    <div key={file.id} className="flex items-center justify-between p-4 border rounded-lg hover-elevate bg-card">
                      <div className="flex items-center gap-4">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg border bg-muted shrink-0">
                          {file.fileType.toLowerCase() === 'dxf' ? (
                            <FileCode2 className="h-5 w-5 text-blue-500" />
                          ) : (
                            <FileText className="h-5 w-5 text-red-500" />
                          )}
                        </div>
                        <div>
                          <Link href={`/files/${file.id}`} className="font-medium hover:underline text-base leading-none block mb-1">
                            {file.fileName}
                          </Link>
                          <div className="flex items-center gap-3 text-xs text-muted-foreground">
                            <span>{file.fileSizeKb ? `${(file.fileSizeKb / 1024).toFixed(2)} MB` : 'Unknown size'}</span>
                            <span>•</span>
                            <span>{format(new Date(file.createdAt), 'MMM d, yyyy')}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <Badge variant={file.analysisStatus === 'completed' ? 'default' : file.analysisStatus === 'failed' ? 'destructive' : 'secondary'}>
                          {file.analysisStatus}
                        </Badge>
                        <Button variant="ghost" size="sm" asChild>
                          <Link href={`/files/${file.id}`}>View</Link>
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="records" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Analysis Records</CardTitle>
              <CardDescription>Extracted variations and patterns from project files.</CardDescription>
            </CardHeader>
            <CardContent>
              {recordsLoading ? (
                <div className="space-y-4">
                  {[1, 2].map(i => <Skeleton key={i} className="h-20 w-full" />)}
                </div>
              ) : records?.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground border-2 border-dashed rounded-lg">
                  No analysis records found.
                </div>
              ) : (
                <div className="space-y-4">
                  {records?.map(record => (
                    <div key={record.id} className="flex flex-col p-4 border rounded-lg hover-elevate bg-card">
                      <div className="flex items-center justify-between mb-2">
                        <Link href={`/records/${record.id}`} className="font-medium hover:underline">
                          {record.title}
                        </Link>
                        <Badge variant="outline">{record.variationType}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">{record.description}</p>
                      <div className="flex items-center justify-between mt-4 text-xs text-muted-foreground">
                        <span>Created {format(new Date(record.createdAt), 'MMM d, yyyy')}</span>
                        <Button variant="link" size="sm" className="h-auto p-0" asChild>
                          <Link href={`/records/${record.id}`}>View Record</Link>
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
