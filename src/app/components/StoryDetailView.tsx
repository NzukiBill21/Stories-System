import { motion } from "motion/react";
import { X, ExternalLink, ThumbsUp, ThumbsDown, Search, TrendingUp, Shield } from "lucide-react";
import { Story } from "./StoryCard";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface StoryDetailViewProps {
  story: Story;
  onClose: () => void;
}

export function StoryDetailView({ story, onClose }: StoryDetailViewProps) {
  // Mock engagement timeline data
  const engagementData = [
    { time: "10:00", value: 120 },
    { time: "10:15", value: 340 },
    { time: "10:30", value: 890 },
    { time: "10:45", value: 1850 },
    { time: "11:00", value: 3200 },
    { time: "11:15", value: 5100 },
    { time: "11:30", value: story.engagement },
  ];

  const platformColors = {
    X: "bg-black text-white dark:bg-white dark:text-black",
    Facebook: "bg-blue-600 text-white",
    TikTok: "bg-pink-600 text-white",
    Instagram: "bg-gradient-to-r from-purple-600 to-pink-600 text-white",
    News: "bg-purple-600 text-white",
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-6"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-card border border-border rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="sticky top-0 bg-card/80 backdrop-blur-xl border-b border-border p-6 flex items-start justify-between">
          <div className="flex-1 pr-4">
            <h2 className="text-2xl font-semibold text-foreground mb-2">{story.headline}</h2>
            <div className="flex items-center gap-3">
              <Badge variant="secondary" className={`${platformColors[story.platform]} text-xs`}>
                {story.platform}
              </Badge>
              <span className="text-sm text-muted-foreground">{story.source}</span>
              <span className="text-sm text-muted-foreground">•</span>
              <span className="text-sm text-muted-foreground">{story.timestamp}</span>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-muted/30 border border-border/50">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <TrendingUp className="w-4 h-4" />
                <span className="text-sm">Engagement</span>
              </div>
              <p className="text-2xl font-semibold text-foreground">
                {story.engagement.toLocaleString()}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-muted/30 border border-border/50">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <TrendingUp className="w-4 h-4" />
                <span className="text-sm">Velocity</span>
              </div>
              <p className="text-2xl font-semibold text-foreground capitalize">{story.velocity}</p>
            </div>
            <div className="p-4 rounded-xl bg-muted/30 border border-border/50">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <Shield className="w-4 h-4" />
                <span className="text-sm">Credibility</span>
              </div>
              <p className="text-2xl font-semibold text-foreground">{story.credibility}%</p>
            </div>
          </div>

          {/* Engagement Timeline */}
          <div className="p-6 rounded-xl bg-muted/30 border border-border/50">
            <h3 className="text-lg font-semibold text-foreground mb-4">Engagement Timeline</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={engagementData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
                <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="hsl(var(--chart-1))"
                  strokeWidth={3}
                  dot={{ fill: "hsl(var(--chart-1))", r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Reason Flagged */}
          <div className="p-4 rounded-xl bg-orange-500/10 border border-orange-500/30">
            <h3 className="text-lg font-semibold text-foreground mb-2">Why This Was Flagged</h3>
            <p className="text-muted-foreground">{story.reason}</p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button className="flex-1 gap-2" size="lg">
              <ThumbsUp className="w-4 h-4" />
              Use Story
            </Button>
            <Button variant="outline" className="flex-1 gap-2" size="lg">
              <Search className="w-4 h-4" />
              Investigate
            </Button>
            <Button variant="ghost" className="flex-1 gap-2" size="lg">
              <ThumbsDown className="w-4 h-4" />
              Ignore
            </Button>
          </div>

          {/* Original Source */}
          <Button variant="outline" className="w-full gap-2" asChild>
            <a href={story.url} target="_blank" rel="noopener noreferrer">
              <ExternalLink className="w-4 h-4" />
              View Original Source
            </a>
          </Button>
        </div>
      </motion.div>
    </motion.div>
  );
}
