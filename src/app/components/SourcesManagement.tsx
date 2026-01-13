import { motion } from "motion/react";
import { Database, Play, Pause, Edit, Trash2, Shield, CheckCircle, RefreshCw } from "lucide-react";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Switch } from "./ui/switch";
import { useState, useEffect } from "react";
import { fetchSources, triggerScrape } from "../../services/api";

interface Source {
  id: number;
  platform: string;
  account_handle: string;
  account_name: string;
  is_trusted: boolean;
  is_kenyan?: boolean;
  location?: string;
  last_checked_at?: string;
}

export function SourcesManagement() {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState<number | null>(null);

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = async () => {
    try {
      setLoading(true);
      const data = await fetchSources();
      setSources(data);
    } catch (error) {
      console.error("Error loading sources:", error);
      setSources([]);
    } finally {
      setLoading(false);
    }
  };

  const handleScrape = async (sourceId: number) => {
    try {
      setScraping(sourceId);
      await triggerScrape(sourceId);
      // Reload sources after scraping
      setTimeout(() => loadSources(), 2000);
    } catch (error) {
      console.error("Error triggering scrape:", error);
    } finally {
      setScraping(null);
    }
  };

  const formatTimeAgo = (dateString?: string) => {
    if (!dateString) return "Never";
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins} min ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

  const platformColors: Record<string, string> = {
    X: "bg-black text-white dark:bg-white dark:text-black",
    Twitter: "bg-black text-white dark:bg-white dark:text-black",
    Facebook: "bg-blue-600 text-white",
    TikTok: "bg-pink-600 text-white",
    Instagram: "bg-gradient-to-r from-purple-600 to-pink-600 text-white",
    News: "bg-purple-600 text-white",
  };

  const getCredibilityColor = (isTrusted: boolean) => {
    return isTrusted ? "text-green-600" : "text-orange-600";
  };

  const getCredibilityScore = (isTrusted: boolean) => {
    return isTrusted ? 95 : 75;
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between mb-6"
      >
        <div className="flex items-center gap-3">
          <Database className="w-6 h-6 text-primary" />
          <div>
            <h2 className="text-2xl font-semibold text-foreground">Sources Management</h2>
            <p className="text-sm text-muted-foreground mt-1">
              {sources.length} source{sources.length !== 1 ? 's' : ''} configured
            </p>
          </div>
        </div>
        <Button onClick={loadSources} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </motion.div>

      {loading ? (
        <div className="text-center py-12 text-muted-foreground">Loading sources...</div>
      ) : sources.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground mb-4">No sources configured</p>
          <p className="text-sm text-muted-foreground">Configure sources in the backend to start scraping</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {sources.map((source, index) => {
            const credibility = getCredibilityScore(source.is_trusted);
            return (
              <motion.div
                key={source.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ scale: 1.01 }}
                className="p-5 rounded-xl border backdrop-blur-xl transition-all border-border/50 bg-card/50"
              >
                <div className="flex items-center justify-between gap-4">
                  {/* Source Info */}
                  <div className="flex items-center gap-4 flex-1">
                    <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-primary/10">
                      <CheckCircle className="w-6 h-6 text-primary" />
                    </div>

                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-foreground">{source.account_name || source.account_handle}</h3>
                        <Badge variant="secondary" className={`${platformColors[source.platform] || 'bg-gray-600 text-white'} text-xs`}>
                          {source.platform}
                        </Badge>
                        {source.is_trusted && (
                          <Badge variant="outline" className="text-xs border-green-600 text-green-600">
                            Trusted
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-2">
                          <Shield className={`w-4 h-4 ${getCredibilityColor(source.is_trusted)}`} />
                          <span>
                            Credibility:{" "}
                            <span className={`font-semibold ${getCredibilityColor(source.is_trusted)}`}>
                              {credibility}%
                            </span>
                          </span>
                        </div>
                        {source.location && (
                          <>
                            <span>•</span>
                            <span>{source.location}</span>
                          </>
                        )}
                        <span>•</span>
                        <span>Last checked: {formatTimeAgo(source.last_checked_at)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleScrape(source.id)}
                      disabled={scraping === source.id}
                    >
                      {scraping === source.id ? (
                        <RefreshCw className="w-4 h-4 animate-spin" />
                      ) : (
                        <Play className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </div>

                {/* Progress bar for credibility */}
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: "100%" }}
                  transition={{ delay: index * 0.05 + 0.2, duration: 0.5 }}
                  className="mt-4"
                >
                  <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${credibility}%` }}
                      transition={{ delay: index * 0.05 + 0.3, duration: 0.8 }}
                      className={`h-full ${
                        credibility >= 95
                          ? "bg-green-600"
                          : credibility >= 90
                          ? "bg-blue-600"
                          : "bg-orange-600"
                      }`}
                    />
                  </div>
                </motion.div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
