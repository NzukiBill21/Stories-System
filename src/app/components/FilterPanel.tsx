import { motion } from "motion/react";
import { Filter, X } from "lucide-react";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Slider } from "./ui/slider";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { useState, useEffect } from "react";

interface FilterPanelProps {
  isOpen: boolean;
  onClose: () => void;
  filters?: {
    platform: string;
    velocity: string;
    credibility: number;
  };
  onFiltersChange?: (filters: { platform: string; velocity: string; credibility: number }) => void;
}

export function FilterPanel({ isOpen, onClose, filters: externalFilters, onFiltersChange }: FilterPanelProps) {
  const [platform, setPlatform] = useState(externalFilters?.platform || "all");
  const [velocity, setVelocity] = useState(externalFilters?.velocity || "all");
  const [credibility, setCredibility] = useState([externalFilters?.credibility || 0]);

  // Sync with external filters
  useEffect(() => {
    if (externalFilters) {
      setPlatform(externalFilters.platform);
      setVelocity(externalFilters.velocity);
      setCredibility([externalFilters.credibility]);
    }
  }, [externalFilters]);

  // Notify parent of filter changes
  useEffect(() => {
    if (onFiltersChange) {
      onFiltersChange({
        platform,
        velocity,
        credibility: credibility[0],
      });
    }
  }, [platform, velocity, credibility, onFiltersChange]);

  const resetFilters = () => {
    setPlatform("all");
    setVelocity("all");
    setCredibility([0]);
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
        onClick={onClose}
      />

      {/* Panel */}
      <motion.aside
        initial={{ x: 100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 100, opacity: 0 }}
        transition={{ type: "spring", damping: 25, stiffness: 300 }}
        className="fixed right-0 top-0 h-screen w-80 border-l border-border/50 backdrop-blur-xl bg-card/80 z-50 lg:sticky lg:top-0 overflow-y-auto"
      >
        <div className="p-6 border-b border-border/50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-foreground">Filters</h3>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="lg:hidden">
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="p-6 space-y-6">
          {/* Platform Filter */}
          <div className="space-y-3">
            <Label htmlFor="platform-filter">Platform</Label>
            <Select value={platform} onValueChange={setPlatform}>
              <SelectTrigger id="platform-filter">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Platforms</SelectItem>
                <SelectItem value="TikTok">TikTok</SelectItem>
                <SelectItem value="Facebook">Facebook</SelectItem>
                <SelectItem value="X">X (Twitter)</SelectItem>
                <SelectItem value="Instagram">Instagram</SelectItem>
                <SelectItem value="Reddit">Reddit</SelectItem>
                <SelectItem value="RSS">RSS</SelectItem>
                <SelectItem value="GoogleTrends">Google Trends</SelectItem>
                <SelectItem value="YouTube">YouTube</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Velocity Filter */}
          <div className="space-y-3">
            <Label htmlFor="velocity-filter">Engagement Velocity</Label>
            <Select value={velocity} onValueChange={setVelocity}>
              <SelectTrigger id="velocity-filter">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Velocities</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Credibility Filter */}
          <div className="space-y-3">
            <Label>Minimum Credibility Score</Label>
            <div className="space-y-3">
              <Slider
                value={credibility}
                onValueChange={setCredibility}
                max={100}
                step={5}
                className="w-full"
              />
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>0%</span>
                <span className="font-semibold text-foreground">{credibility[0]}%</span>
                <span>100%</span>
              </div>
            </div>
          </div>

          {/* Active Filters */}
          <div className="pt-6 border-t border-border/50">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-foreground">Active Filters</span>
              <Button variant="ghost" size="sm" onClick={resetFilters}>
                Clear all
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {platform !== "all" && (
                <Badge variant="secondary" className="capitalize">
                  {platform}
                </Badge>
              )}
              {velocity !== "all" && (
                <Badge variant="secondary" className="capitalize">
                  {velocity} velocity
                </Badge>
              )}
              {credibility[0] > 0 && (
                <Badge variant="secondary">Min credibility: {credibility[0]}%</Badge>
              )}
              {platform === "all" && velocity === "all" && credibility[0] === 0 && (
                <span className="text-sm text-muted-foreground">No active filters</span>
              )}
            </div>
          </div>

          {/* Quick Stats */}
          <div className="pt-6 border-t border-border/50 space-y-3">
            <h4 className="text-sm font-medium text-foreground">Quick Stats</h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Total Stories</span>
                <span className="font-semibold text-foreground">847</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">High Velocity</span>
                <span className="font-semibold text-foreground">234</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Active Sources</span>
                <span className="font-semibold text-foreground">8</span>
              </div>
            </div>
          </div>
        </div>
      </motion.aside>
    </>
  );
}
