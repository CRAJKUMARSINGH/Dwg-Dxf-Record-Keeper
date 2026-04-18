import { useState } from "react";
import { Link } from "wouter";
import { 
  useListComparisons, getListComparisonsQueryKey,
  useCreateComparison, useDeleteComparison,
  useListFiles, getListFilesQueryKey,
  useListProjects, getListProjectsQueryKey
} from "@workspace/api-client-react";
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
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { Copy, MoreVertical, Plus, Trash2, GitCompare, FileCode2, FileText } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const comparisonSchema = z.object({
  title: z.string().min(1, "Title is required"),
  projectId: z.coerce.number().optional().nullable(),
  fileIds: z.string().min(1, "File IDs required (comma separated)"),
  notes: z.string().optional()
});

export default function Comparisons() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [createOpen, setCreateOpen] = useState(false);

  const { data: comparisons, isLoading } = useListComparisons({}, {
    query: {
      queryKey: getListComparisonsQueryKey({})
    }
  });

  const { data: projects } = useListProjects({
    query: {
      queryKey: getListProjectsQueryKey()
    }
  });

  const createComparison = useCreateComparison();
  const deleteComparison = useDeleteComparison();

  const form = useForm<z.infer<typeof comparisonSchema>>({
    resolver: zodResolver(comparisonSchema),
    defaultValues: {
      title: "",
      projectId: null,
      fileIds: "",
      notes: ""
    }
  });

  function onSubmit(values: z.infer<typeof comparisonSchema>) {
    createComparison.mutate({ 
      data: { 
        ...values,
        projectId: values.projectId || undefined,
        differencesSummary: "Analysis pending...",
        similaritiesSummary: "Analysis pending..."
      } 
    }, {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getListComparisonsQueryKey({}) });
        setCreateOpen(false);
        form.reset();
        toast({
          title: "Comparison created",
          description: "The comparison has been successfully initiated."
        });
      },
      onError: () => {
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to create comparison. Please try again."
        });
      }
    });
  }

  function handleDelete(id: number) {
    if (confirm("Are you sure you want to delete this comparison?")) {
      deleteComparison.mutate({ id }, {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: getListComparisonsQueryKey({}) });
          toast({
            title: "Comparison deleted",
            description: "The comparison has been removed."
          });
        }
      });
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Comparisons</h2>
          <p className="text-muted-foreground">Compare design files to identify differences and patterns.</p>
        </div>
        
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Comparison
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create Comparison</DialogTitle>
              <DialogDescription>
                Select two or more files to compare their extracted parameters.
              </DialogDescription>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="title"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Title</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. Deck Plan v1 vs v2" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="projectId"
                  render={({ field }) => (
                    <FormItem>
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
                  name="fileIds"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>File IDs (comma separated)</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. 1, 2" {...field} />
                      </FormControl>
                      <CardDescription>Enter the IDs of the files you want to compare</CardDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="notes"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Notes</FormLabel>
                      <FormControl>
                        <Textarea placeholder="Context for this comparison..." {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <DialogFooter>
                  <Button type="submit" disabled={createComparison.isPending}>
                    {createComparison.isPending ? "Creating..." : "Create Comparison"}
                  </Button>
                </DialogFooter>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4].map(i => (
            <Card key={i} className="flex flex-col">
              <CardHeader>
                <Skeleton className="h-6 w-2/3" />
                <Skeleton className="h-4 w-1/3" />
              </CardHeader>
              <CardContent className="flex-1">
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : comparisons?.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center border rounded-lg bg-card/50 border-dashed">
          <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
            <Copy className="h-6 w-6 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium">No comparisons found</h3>
          <p className="text-sm text-muted-foreground max-w-sm mt-1 mb-4">
            Start comparing design files to track changes and find patterns.
          </p>
          <Button onClick={() => setCreateOpen(true)}>Create Comparison</Button>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {comparisons?.map(comparison => (
            <Card key={comparison.id} className="flex flex-col hover-elevate transition-colors border-border/50 hover:border-border">
              <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
                <div className="space-y-1 pr-4">
                  <CardTitle className="leading-tight">
                    <Link href={`/comparisons/${comparison.id}`} className="hover:underline flex items-center gap-2">
                      <GitCompare className="h-4 w-4" />
                      {comparison.title}
                    </Link>
                  </CardTitle>
                  <CardDescription className="flex items-center text-xs">
                    Files: {comparison.fileIds}
                  </CardDescription>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-8 w-8 -mr-2 -mt-2">
                      <MoreVertical className="h-4 w-4" />
                      <span className="sr-only">Open menu</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem asChild>
                      <Link href={`/comparisons/${comparison.id}`}>View Details</Link>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-destructive" onClick={() => handleDelete(comparison.id)}>
                      <Trash2 className="mr-2 h-4 w-4" /> Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </CardHeader>
              <CardContent className="flex-1 pt-4">
                <div className="space-y-3 text-sm text-muted-foreground">
                  {comparison.differencesSummary && (
                    <div className="line-clamp-2">
                      <span className="font-medium text-foreground">Diff: </span>
                      {comparison.differencesSummary}
                    </div>
                  )}
                  {comparison.similaritiesSummary && (
                    <div className="line-clamp-2">
                      <span className="font-medium text-foreground">Sim: </span>
                      {comparison.similaritiesSummary}
                    </div>
                  )}
                </div>
              </CardContent>
              <CardFooter className="border-t bg-muted/50 px-6 py-3 flex justify-between items-center text-xs text-muted-foreground mt-auto">
                <div className="flex items-center gap-3">
                  <span>Created {format(new Date(comparison.createdAt), 'MMM d, yyyy')}</span>
                </div>
                {comparison.projectId && (
                   <Link href={`/projects/${comparison.projectId}`} className="hover:underline">Project #{comparison.projectId}</Link>
                )}
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
