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
import { fetchStories, fetchHotStories, getHealth, fetchInsights, type Insights } from "../services/api";

export default function App() {
  const [theme, setTheme] = useState<"light" | "dark">("dark");
  const [activeView, setActiveView] = useState("dashboard");
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  const [isFilterPanelOpen, setIsFilterPanelOpen] = useState(false);
  const [stories, setStories] = useState<Story[]>([]);
  const [filteredStories, setFilteredStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [apiConnected, setApiConnected] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [quickStats, setQuickStats] = useState<Insights | null>(null);
  const [filters, setFilters] = useState({
    platform: "all",
    velocity: "all",
    credibility: 0,
    showHot: false,  // Show hot/emerging stories
    kenyanOnly: false,  // Filter Kenyan stories only
    topic: "all",  // Content category filter
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
      setLoadError(null);
      try {
        const health = await getHealth();
        setApiConnected(health.ok);

        if (!health.ok) {
          setLoadError(health.message ?? "Backend or database unavailable.");
          setStories([]);
          setQuickStats(null);
          setLoading(false);
          return;
        }

        if (filters.showHot) {
          const fetchedStories = await fetchHotStories(filters.kenyanOnly, 6);
          setStories(fetchedStories);
        } else {
          const params: any = { limit: 50, hours_back: 24 };
          if (filters.platform !== "all") params.platform = filters.platform;
          if (filters.kenyanOnly) params.is_kenyan = true;
          if (filters.topic !== "all") params.topic = filters.topic;
          const fetchedStories = await fetchStories(params);
          setStories(fetchedStories);
        }
        const insights = await fetchInsights(24);
        setQuickStats(insights ?? null);
      } catch (error) {
        const message = error instanceof Error ? error.message : "Failed to load stories.";
        setLoadError(message);
        setStories([]);
        setQuickStats(null);
        setApiConnected(false);
      } finally {
        setLoading(false);
      }
    };

    loadStories();
    
    // Refresh stories more frequently for hot stories (every 2 minutes)
    const refreshInterval = filters.showHot ? 2 * 60 * 1000 : 5 * 60 * 1000;
    const interval = setInterval(loadStories, refreshInterval);
    return () => clearInterval(interval);
  }, [filters.platform, filters.showHot, filters.kenyanOnly, filters.topic]);

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
              loadError={loadError}
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
              quickStats={quickStats}
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
                topic: newFilters.topic ?? "all",
              });
            }}
            quickStats={quickStats}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
