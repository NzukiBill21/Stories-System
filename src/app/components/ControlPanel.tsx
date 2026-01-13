import { motion } from "motion/react";
import { Settings, Info } from "lucide-react";
import { Label } from "./ui/label";
import { Slider } from "./ui/slider";
import { Switch } from "./ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./ui/tooltip";
import { useState } from "react";

export function ControlPanel() {
  const [scrapeFrequency, setScrapeFrequency] = useState("10min");
  const [priorityWeight, setPriorityWeight] = useState([70]);
  const [enableRealTime, setEnableRealTime] = useState(true);
  const [enableBreakingNews, setEnableBreakingNews] = useState(true);

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-3 mb-6"
      >
        <Settings className="w-6 h-6 text-primary" />
        <div>
          <h2 className="text-2xl font-semibold text-foreground">Scraping & Scheduling Controls</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Configure how and when the system monitors sources
          </p>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scrape Frequency */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="p-6 rounded-xl border border-border/50 backdrop-blur-xl bg-card/50 space-y-4"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Label htmlFor="frequency">Scrape Frequency</Label>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger>
                    <Info className="w-4 h-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="max-w-xs">
                      How often the system checks sources for new content. More frequent checks use
                      more resources but provide faster updates.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>
          <Select value={scrapeFrequency} onValueChange={setScrapeFrequency}>
            <SelectTrigger id="frequency">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="5min">Every 5 minutes</SelectItem>
              <SelectItem value="10min">Every 10 minutes</SelectItem>
              <SelectItem value="30min">Every 30 minutes</SelectItem>
              <SelectItem value="hourly">Hourly</SelectItem>
              <SelectItem value="daily">Daily</SelectItem>
            </SelectContent>
          </Select>
          <motion.div
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.3 }}
            className="p-3 rounded-lg bg-muted/50 text-sm text-muted-foreground"
          >
            Current setting: Checking sources <strong>{scrapeFrequency}</strong>
          </motion.div>
        </motion.div>

        {/* Priority Weighting */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="p-6 rounded-xl border border-border/50 backdrop-blur-xl bg-card/50 space-y-4"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Label>Priority Weight for High-Credibility Sources</Label>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger>
                    <Info className="w-4 h-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="max-w-xs">
                      Stories from high-credibility sources get boosted. Higher values = more
                      emphasis on trusted sources.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>
          <div className="space-y-3">
            <Slider
              value={priorityWeight}
              onValueChange={setPriorityWeight}
              max={100}
              step={5}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Low Priority</span>
              <span className="font-semibold text-foreground">{priorityWeight[0]}%</span>
              <span>High Priority</span>
            </div>
          </div>
          <motion.div
            key={priorityWeight[0]}
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.3 }}
            className="p-3 rounded-lg bg-muted/50 text-sm text-muted-foreground"
          >
            High-credibility sources will be <strong>prioritized by {priorityWeight[0]}%</strong>
          </motion.div>
        </motion.div>

        {/* Real-Time Monitoring */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="p-6 rounded-xl border border-border/50 backdrop-blur-xl bg-card/50 space-y-4"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Label htmlFor="realtime">Real-Time Monitoring</Label>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger>
                    <Info className="w-4 h-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="max-w-xs">
                      Enable continuous monitoring for instant story detection. Uses streaming APIs
                      for fastest updates.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            <Switch
              id="realtime"
              checked={enableRealTime}
              onCheckedChange={setEnableRealTime}
            />
          </div>
          <motion.div
            animate={{
              backgroundColor: enableRealTime
                ? "hsl(var(--chart-2) / 0.1)"
                : "hsl(var(--muted) / 0.5)",
            }}
            className="p-3 rounded-lg text-sm"
          >
            <p className={enableRealTime ? "text-foreground" : "text-muted-foreground"}>
              {enableRealTime
                ? "✓ Real-time monitoring is active"
                : "Real-time monitoring is paused"}
            </p>
          </motion.div>
        </motion.div>

        {/* Breaking News Alerts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="p-6 rounded-xl border border-border/50 backdrop-blur-xl bg-card/50 space-y-4"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Label htmlFor="breaking">Breaking News Alerts</Label>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger>
                    <Info className="w-4 h-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="max-w-xs">
                      Get immediate notifications when breaking news keywords are detected with high
                      engagement velocity.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            <Switch
              id="breaking"
              checked={enableBreakingNews}
              onCheckedChange={setEnableBreakingNews}
            />
          </div>
          <motion.div
            animate={{
              backgroundColor: enableBreakingNews
                ? "hsl(var(--chart-2) / 0.1)"
                : "hsl(var(--muted) / 0.5)",
            }}
            className="p-3 rounded-lg text-sm"
          >
            <p className={enableBreakingNews ? "text-foreground" : "text-muted-foreground"}>
              {enableBreakingNews
                ? "✓ Breaking news alerts are enabled"
                : "Breaking news alerts are disabled"}
            </p>
          </motion.div>
        </motion.div>

        {/* Advanced Settings Panel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="lg:col-span-2 p-6 rounded-xl border border-border/50 backdrop-blur-xl bg-card/50 space-y-4"
        >
          <h3 className="text-lg font-semibold text-foreground">Advanced Configuration</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="min-engagement">Minimum Engagement Threshold</Label>
              <Select defaultValue="500">
                <SelectTrigger id="min-engagement">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="100">100 engagements</SelectItem>
                  <SelectItem value="500">500 engagements</SelectItem>
                  <SelectItem value="1000">1,000 engagements</SelectItem>
                  <SelectItem value="5000">5,000 engagements</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="velocity-threshold">Velocity Detection Level</Label>
              <Select defaultValue="medium">
                <SelectTrigger id="velocity-threshold">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low (catch everything)</SelectItem>
                  <SelectItem value="medium">Medium (balanced)</SelectItem>
                  <SelectItem value="high">High (only fast-growing)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
