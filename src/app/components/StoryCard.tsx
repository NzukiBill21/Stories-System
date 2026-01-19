import { motion } from "motion/react";
import { TrendingUp, AlertCircle, Clock, ExternalLink, Shield } from "lucide-react";
import { Badge } from "./ui/badge";

export interface Story {
  id: string;
  headline: string;
  source: string;
  platform: "X" | "Facebook" | "TikTok" | "Instagram" | "News" | "Reddit" | "RSS" | "GoogleTrends" | "YouTube" | string;
  engagement: number;
  velocity: "high" | "medium" | "low";
  reason: string;
  timestamp: string;
  credibility: number;
  url: string;
}

interface StoryCardProps {
  story: Story;
  onClick: () => void;
}

export function StoryCard({ story, onClick }: StoryCardProps) {
  const velocityColors = {
    high: "text-red-500",
    medium: "text-orange-500",
    low: "text-blue-500",
  };

  const platformColors: Record<string, string> = {
    X: "bg-black text-white dark:bg-white dark:text-black",
    Facebook: "bg-blue-600 text-white",
    TikTok: "bg-pink-600 text-white",
    Instagram: "bg-gradient-to-r from-purple-600 to-pink-600 text-white",
    News: "bg-purple-600 text-white",
    Reddit: "bg-orange-600 text-white",
    RSS: "bg-indigo-600 text-white",
    GoogleTrends: "bg-blue-500 text-white",
    YouTube: "bg-red-600 text-white",
  };
  
  const getPlatformColor = (platform: string) => {
    return platformColors[platform] || "bg-gray-600 text-white";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ duration: 0.3 }}
      onClick={onClick}
      className="group relative cursor-pointer rounded-xl border border-border/50 backdrop-blur-xl bg-card/50 p-5 shadow-sm hover:shadow-xl hover:border-border transition-all"
    >
      {/* Glassmorphism overlay */}
      <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-card/80 to-card/40 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity" />

      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1">
            <h3 className="text-lg leading-snug text-card-foreground group-hover:text-primary transition-colors line-clamp-2">
              {story.headline}
            </h3>
          </div>
          <TrendingUp className={`w-5 h-5 ${velocityColors[story.velocity]} flex-shrink-0`} />
        </div>

        {/* Source and Platform */}
        <div className="flex items-center gap-2 mb-3">
          <Badge variant="secondary" className={`${getPlatformColor(story.platform)} text-xs`}>
            {story.platform}
          </Badge>
          <span className="text-sm text-muted-foreground truncate">{story.source}</span>
        </div>

        {/* Engagement Metrics */}
        <div className="flex items-center gap-4 mb-3 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <TrendingUp className="w-4 h-4" />
            <span>{story.engagement.toLocaleString()} engagements</span>
          </div>
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            <span>{story.timestamp}</span>
          </div>
        </div>

        {/* Reason Flagged */}
        <div className="flex items-center gap-2 mb-3">
          <AlertCircle className="w-4 h-4 text-orange-500" />
          <span className="text-sm text-muted-foreground">{story.reason}</span>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-border/50">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-green-600" />
            <span className="text-sm text-muted-foreground">
              Credibility: <span className="text-foreground font-medium">{story.credibility}%</span>
            </span>
          </div>
          <ExternalLink className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
        </div>
      </div>
    </motion.div>
  );
}
