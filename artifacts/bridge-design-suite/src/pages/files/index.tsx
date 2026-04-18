import { useState } from "react";
import { Link } from "wouter";
import { useListFiles, useCreateFileRecord, useDeleteFileRecord, getListFilesQueryKey, useListProjects, getListProjectsQueryKey } from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { useToast } from "@/hooks/use-toast";
import { FileText, MoreVertical, Plus, Trash2, FileCode2, Filter } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const fileRecordSchema = z.object({
  projectId: z.coerce.number().optional().nullable(),
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

export default function Files() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [createOpen, setCreateOpen] = useState(false);
  const [filterType, setFilterType] = useState<string | null>(null);

  const { data: files, isLoading } = useListFiles(
    filterType ? { fileType: filterType } : {}, 
    {
      query: {
        queryKey: getListFilesQueryKey(filterType ? { fileType: filterType } : {})
      }
    }
  );

  const { data: projects } = useListProjects({
    query: {
      queryKey: getListProjectsQueryKey()
    }
  });

  const createFileRecord = useCreateFileRecord();
  const deleteFileRecord = useDeleteFileRecord();

  const form = useForm<z.infer<typeof fileRecordSchema>>({
    resolver: zodResolver(fileRecordSchema),
    defaultValues: {
      projectId: null,
      fileName: "",
      fileType: "pdf",
      bridgeType: "",
    }
  });

  function onSubmit(values: z.infer<typeof fileRecordSchema>) {
    createFileRecord.mutate({ 
      data: { 
        ...values,
        projectId: values.projectId || undefined,
        analysisStatus: "pending",
        fileSizeKb: Math.floor(Math.random() * 5000) + 100 
      } 
    }, {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getListFilesQueryKey() });
        setCreateOpen(false);
        form.reset();
        toast({
          title: "File record created",
          description: "The file record has been successfully added to the library."
        });
      },
      onError: () => {
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to create file record. Please try again."
        });
      }
    });
  }

  function handleDelete(id: number) {
    if (confirm("Are you sure you want to delete this file record?")) {
      deleteFileRecord.mutate({ id }, {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: getListFilesQueryKey() });
          toast({
            title: "File deleted",
            description: "The file record has been removed."
          });
        }
      });
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">File Library</h2>
          <p className="text-muted-foreground">Manage all your DXF and PDF design files.</p>
        </div>
        
        <div className="flex items-center gap-2">
          <Select value={filterType || "all"} onValueChange={(val) => setFilterType(val === "all" ? null : val)}>
            <SelectTrigger className="w-[180px]">
              <Filter className="w-4 h-4 mr-2" />
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="dxf">DXF (AutoCAD)</SelectItem>
              <SelectItem value="pdf">PDF</SelectItem>
            </SelectContent>
          </Select>

          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
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
                  Add a new design file to the central library.
                </DialogDescription>
              </DialogHeader>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="projectId"
                      render={({ field }) => (
                        <FormItem className="col-span-2">
                          <FormLabel>Project (Optional)</FormLabel>
                          <Select 
                            onValueChange={(val) => field.onChange(val === "none" ? null : parseInt(val))} 
                            value={field.value ? field.value.toString() : "none"}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select project" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="none">No Project</SelectItem>
                              {projects?.map(p => (
                                <SelectItem key={p.id} value={p.id.toString()}>{p.name}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
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
                            <Input placeholder="e.g. Steel" {...field} />
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
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <Card key={i} className="flex flex-col">
              <CardHeader>
                <Skeleton className="h-6 w-2/3" />
                <Skeleton className="h-4 w-1/3" />
              </CardHeader>
              <CardContent className="flex-1">
                <Skeleton className="h-10 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : files?.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center border rounded-lg bg-card/50 border-dashed">
          <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
            <FileText className="h-6 w-6 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium">No files found</h3>
          <p className="text-sm text-muted-foreground max-w-sm mt-1 mb-4">
            Get started by uploading your first design file.
          </p>
          <Button onClick={() => setCreateOpen(true)}>Upload File</Button>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {files?.map(file => (
            <Card key={file.id} className="flex flex-col hover-elevate transition-colors border-border/50 hover:border-border">
              <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
                <div className="flex items-center gap-3 w-full pr-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg border bg-muted shrink-0">
                    {file.fileType.toLowerCase() === 'dxf' ? (
                      <FileCode2 className="h-5 w-5 text-blue-500" />
                    ) : (
                      <FileText className="h-5 w-5 text-red-500" />
                    )}
                  </div>
                  <div className="space-y-1 overflow-hidden flex-1">
                    <CardTitle className="leading-tight truncate text-base">
                      <Link href={`/files/${file.id}`} className="hover:underline">
                        {file.fileName}
                      </Link>
                    </CardTitle>
                    <CardDescription className="flex items-center text-xs gap-2 truncate">
                      <span>{file.fileSizeKb ? `${(file.fileSizeKb / 1024).toFixed(2)} MB` : 'Unknown size'}</span>
                      {file.projectId && (
                        <>
                          <span>•</span>
                          <span>Project #{file.projectId}</span>
                        </>
                      )}
                    </CardDescription>
                  </div>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-8 w-8 -mr-2 -mt-2 shrink-0">
                      <MoreVertical className="h-4 w-4" />
                      <span className="sr-only">Open menu</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem asChild>
                      <Link href={`/files/${file.id}`}>View Details</Link>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-destructive" onClick={() => handleDelete(file.id)}>
                      <Trash2 className="mr-2 h-4 w-4" /> Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </CardHeader>
              <CardContent className="flex-1 pt-4">
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary">{file.fileType.toUpperCase()}</Badge>
                  <Badge variant={file.analysisStatus === 'completed' ? 'default' : file.analysisStatus === 'failed' ? 'destructive' : 'outline'}>
                    {file.analysisStatus}
                  </Badge>
                  {file.bridgeType && (
                    <Badge variant="outline" className="text-muted-foreground">{file.bridgeType}</Badge>
                  )}
                </div>
              </CardContent>
              <CardFooter className="border-t bg-muted/50 px-6 py-3 flex justify-between items-center text-xs text-muted-foreground mt-auto">
                <div className="flex items-center gap-3">
                  <span>Created {format(new Date(file.createdAt), 'MMM d, yyyy')}</span>
                </div>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
