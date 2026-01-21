import { useState, useEffect } from "react";
import { AnimatePresence } from "motion/react";
import { Filter } from "lucide-react";
import { Sidebar } from "./components/Sidebar";
import { Dashboard } from "./components/Dashboard";
import { StoryDetailView } from "./components/StoryDetailView";
import { ControlPanel } from "./components/ControlPanel";
import { SourcesManagement } from "./components/SourcesManagement";
import { InsightsPanel } from "./components/InsightsPanel";
import { FilterPanel } from "./components/FilterPanel";
import { Story } from "./components/StoryCard";
import { Button } from "./components/ui/button";
import { fetchStories, fetchHotStories, healthCheck } from "../services/api";

export default function App() {
  const [theme, setTheme] = useState<"light" | "dark">("dark");
  const [activeView, setActiveView] = useState("dashboard");
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  const [isFilterPanelOpen, setIsFilterPanelOpen] = useState(false);
  const [stories, setStories] = useState<Story[]>([]);
  const [filteredStories, setFilteredStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [apiConnected, setApiConnected] = useState(false);
  const [filters, setFilters] = useState({
    platform: "all",
    velocity: "all",
    credibility: 0,
    showHot: false,  // Show hot/emerging stories
    kenyanOnly: false,  // Filter Kenyan stories only
  });

  // No mock data - only use real scraped data from API

  // Theme toggle
  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    document.documentElement.classList.toggle("dark", newTheme === "dark");
  };

  // Initialize theme
  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, []);

  // Fetch stories from API
  useEffect(() => {
    const loadStories = async () => {
      setLoading(true);
      try {
        // Check API health first
        const isHealthy = await healthCheck();
        setApiConnected(isHealthy);
        
        if (isHealthy) {
          // Fetch hot/emerging stories if enabled, otherwise regular stories
          if (filters.showHot) {
            const fetchedStories = await fetchHotStories(filters.kenyanOnly, 6);
            setStories(fetchedStories);
          } else {
            // Fetch real stories from API - ONLY real data, no fallback
            const params: any = { limit: 50, hours_back: 24 };
            if (filters.platform !== "all") {
              params.platform = filters.platform;
            }
            if (filters.kenyanOnly) {
              params.is_kenyan = true;
            }
            const fetchedStories = await fetchStories(params);
            setStories(fetchedStories);
          }
        } else {
          // API not available - show empty state, no mock data
          console.warn("API not available - please start the backend server");
          setStories([]);
        }
      } catch (error) {
        console.error("Error loading stories:", error);
        // No mock data fallback - show empty state
        setStories([]);
      } finally {
        setLoading(false);
      }
    };

    loadStories();
    
    // Refresh stories more frequently for hot stories (every 2 minutes)
    const refreshInterval = filters.showHot ? 2 * 60 * 1000 : 5 * 60 * 1000;
    const interval = setInterval(loadStories, refreshInterval);
    return () => clearInterval(interval);
  }, [filters.platform, filters.showHot, filters.kenyanOnly]);

  // Apply filters to stories
  useEffect(() => {
    let filtered = [...stories];

    // Platform filter
    if (filters.platform !== "all") {
      filtered = filtered.filter((s) => s.platform.toLowerCase() === filters.platform.toLowerCase());
    }

    // Velocity filter
    if (filters.velocity !== "all") {
      filtered = filtered.filter((s) => s.velocity === filters.velocity);
    }

    // Credibility filter
    filtered = filtered.filter((s) => s.credibility >= filters.credibility);

    setFilteredStories(filtered);
  }, [stories, filters]);

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <Sidebar
        activeView={activeView}
        onViewChange={setActiveView}
        theme={theme}
        onThemeToggle={toggleTheme}
      />

      {/* Main Content */}
      <main className="ml-64 min-h-screen flex">
        <div className="flex-1 p-8">
          {/* Filter Toggle Button (mobile) */}
          {activeView === "dashboard" && (
            <div className="lg:hidden mb-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsFilterPanelOpen(!isFilterPanelOpen)}
                className="gap-2"
              >
                <Filter className="w-4 h-4" />
                Filters
              </Button>
            </div>
          )}

          {/* Views */}
          {activeView === "dashboard" && (
            <Dashboard 
              stories={loading ? [] : filteredStories} 
              onStorySelect={setSelectedStory} 
            />
          )}
          {activeView === "control" && <ControlPanel />}
          {activeView === "sources" && <SourcesManagement />}
          {activeView === "insights" && <InsightsPanel />}
        </div>

        {/* Right Filter Panel */}
        {activeView === "dashboard" && (
          <div className="hidden lg:block w-80">
            <FilterPanel 
              isOpen={true} 
              onClose={() => {}}
              filters={filters}
              onFiltersChange={setFilters}
            />
          </div>
        )}
      </main>

      {/* Story Detail Modal */}
      <AnimatePresence>
        {selectedStory && (
          <StoryDetailView story={selectedStory} onClose={() => setSelectedStory(null)} />
        )}
      </AnimatePresence>

      {/* Mobile Filter Panel */}
      <AnimatePresence>
        {isFilterPanelOpen && activeView === "dashboard" && (
          <FilterPanel 
            isOpen={isFilterPanelOpen} 
            onClose={() => setIsFilterPanelOpen(false)}
            filters={filters}
            onFiltersChange={(newFilters) => {
              setFilters({
                platform: newFilters.platform,
                velocity: newFilters.velocity,
                credibility: newFilters.credibility,
                showHot: newFilters.showHot,
                kenyanOnly: newFilters.kenyanOnly,
              });
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
