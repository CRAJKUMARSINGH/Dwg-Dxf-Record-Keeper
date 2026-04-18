import { useState } from "react";
import { Link } from "wouter";
import { 
  useListAnalysisRecords, 
  getListAnalysisRecordsQueryKey,
  useUpdateAnalysisRecord,
  useDeleteAnalysisRecord
} from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { useToast } from "@/hooks/use-toast";
import { Activity, MoreVertical, Trash2, Filter, Star, Search } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function Records() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [filterType, setFilterType] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const { data: records, isLoading } = useListAnalysisRecords({}, {
    query: {
      queryKey: getListAnalysisRecordsQueryKey({})
    }
  });

  const updateRecord = useUpdateAnalysisRecord();
  const deleteRecord = useDeleteAnalysisRecord();

  function handleDelete(id: number) {
    if (confirm("Are you sure you want to delete this analysis record?")) {
      deleteRecord.mutate({ id }, {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: getListAnalysisRecordsQueryKey({}) });
          toast({
            title: "Record deleted",
            description: "The analysis record has been removed."
          });
        }
      });
    }
  }

  function toggleFavorite(id: number, currentStatus: boolean) {
    updateRecord.mutate({ id, data: { isFavorite: !currentStatus } }, {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getListAnalysisRecordsQueryKey({}) });
      }
    });
  }

  const filteredRecords = records?.filter(record => {
    if (filterType && filterType !== "all" && record.variationType !== filterType) return false;
    if (searchQuery && !record.title.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  // Get unique variation types for the filter
  const variationTypes = Array.from(new Set(records?.map(r => r.variationType) || []));

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Analysis Records</h2>
          <p className="text-muted-foreground">Extracted design variations and memorized patterns.</p>
        </div>
        
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search records..." 
              className="pl-8" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Select value={filterType || "all"} onValueChange={(val) => setFilterType(val === "all" ? null : val)}>
            <SelectTrigger className="w-[180px]">
              <Filter className="w-4 h-4 mr-2" />
              <SelectValue placeholder="Filter type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Variations</SelectItem>
              {variationTypes.map(type => (
                <SelectItem key={type} value={type}>{type}</SelectItem>
              ))}
            </SelectContent>
          </Select>
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
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredRecords?.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center border rounded-lg bg-card/50 border-dashed">
          <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
            <Activity className="h-6 w-6 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium">No records found</h3>
          <p className="text-sm text-muted-foreground max-w-sm mt-1 mb-4">
            {records?.length === 0 
              ? "You haven't created any analysis records yet. Extract parameters from your files to create records."
              : "No records match your current filters."}
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {filteredRecords?.map(record => (
            <Card key={record.id} className="flex flex-col hover-elevate transition-colors border-border/50 hover:border-border group">
              <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
                <div className="flex items-start gap-3 w-full pr-2">
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className={`h-8 w-8 shrink-0 -ml-2 -mt-1 ${record.isFavorite ? 'text-yellow-500 hover:text-yellow-600' : 'text-muted-foreground/50 hover:text-yellow-500'}`}
                    onClick={() => toggleFavorite(record.id, record.isFavorite)}
                  >
                    <Star className={`h-5 w-5 ${record.isFavorite ? 'fill-current' : ''}`} />
                  </Button>
                  <div className="space-y-1 flex-1">
                    <CardTitle className="leading-tight text-base">
                      <Link href={`/records/${record.id}`} className="hover:underline">
                        {record.title}
                      </Link>
                    </CardTitle>
                    <CardDescription className="flex items-center text-xs">
                      <Badge variant="outline" className="font-normal">{record.variationType}</Badge>
                    </CardDescription>
                  </div>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-8 w-8 -mr-2 -mt-2 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                      <MoreVertical className="h-4 w-4" />
                      <span className="sr-only">Open menu</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem asChild>
                      <Link href={`/records/${record.id}`}>View Details</Link>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-destructive" onClick={() => handleDelete(record.id)}>
                      <Trash2 className="mr-2 h-4 w-4" /> Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </CardHeader>
              <CardContent className="flex-1 pt-4">
                <p className="text-sm text-muted-foreground line-clamp-3">
                  {record.description || "No description provided."}
                </p>
              </CardContent>
              <CardFooter className="border-t bg-muted/50 px-6 py-3 flex justify-between items-center text-xs text-muted-foreground mt-auto">
                <div className="flex items-center gap-3">
                  <span>{format(new Date(record.createdAt), 'MMM d, yyyy')}</span>
                  {record.projectId && (
                    <>
                      <span>•</span>
                      <Link href={`/projects/${record.projectId}`} className="hover:underline">Project #{record.projectId}</Link>
                    </>
                  )}
                </div>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
