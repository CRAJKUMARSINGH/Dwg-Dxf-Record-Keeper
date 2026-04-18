import { useEffect } from "react";
import { Switch, Route, Router as WouterRouter, useLocation } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppLayout } from "@/components/layout";
import NotFound from "@/pages/not-found";

import Home from "@/pages/home";
import Projects from "@/pages/projects/index";
import ProjectDetail from "@/pages/projects/detail";
import Files from "@/pages/files/index";
import FileDetail from "@/pages/files/detail";
import Records from "@/pages/records/index";
import RecordDetail from "@/pages/records/detail";
import Comparisons from "@/pages/comparisons/index";
import ComparisonDetail from "@/pages/comparisons/detail";
import BridgeGenerator from "@/pages/generator";

const queryClient = new QueryClient();

function StudioRedirect() {
  const [, setLocation] = useLocation();
  useEffect(() => {
    setLocation("/generator");
  }, [setLocation]);
  return null;
}

function Router() {
  return (
    <AppLayout>
      <Switch>
        <Route path="/" component={Home} />
        
        <Route path="/projects" component={Projects} />
        <Route path="/projects/:id" component={ProjectDetail} />
        
        <Route path="/files" component={Files} />
        <Route path="/files/:id" component={FileDetail} />
        
        <Route path="/records" component={Records} />
        <Route path="/records/:id" component={RecordDetail} />
        
        <Route path="/comparisons" component={Comparisons} />
        <Route path="/comparisons/:id" component={ComparisonDetail} />
        
        <Route path="/generator" component={BridgeGenerator} />
        <Route path="/studio" component={StudioRedirect} />

        <Route component={NotFound} />
      </Switch>
    </AppLayout>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
          <Router />
        </WouterRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
