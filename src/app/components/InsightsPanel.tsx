import { motion } from "motion/react";
import { Lightbulb, TrendingUp, Clock } from "lucide-react";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";

interface TopicCluster {
  topic: string;
  count: number;
  velocity: "rising" | "stable" | "falling";
  keywords: string[];
}

export function InsightsPanel() {
  const topicClusters: TopicCluster[] = [
    {
      topic: "Climate Summit 2026",
      count: 847,
      velocity: "rising",
      keywords: ["climate", "summit", "policy", "renewable"],
    },
    {
      topic: "Tech Regulation",
      count: 623,
      velocity: "rising",
      keywords: ["AI", "regulation", "privacy", "data"],
    },
    {
      topic: "Global Markets",
      count: 512,
      velocity: "stable",
      keywords: ["stocks", "markets", "economy", "trade"],
    },
    {
      topic: "Sports Championship",
      count: 489,
      velocity: "rising",
      keywords: ["championship", "sports", "finals", "victory"],
    },
    {
      topic: "Health Research",
      count: 356,
      velocity: "stable",
      keywords: ["health", "research", "study", "medical"],
    },
    {
      topic: "Entertainment Awards",
      count: 298,
      velocity: "falling",
      keywords: ["awards", "entertainment", "film", "music"],
    },
  ];

  const trendingTopics = [
    { name: "Artificial Intelligence", mentions: 1234 },
    { name: "Climate Action", mentions: 987 },
    { name: "Global Economy", mentions: 845 },
    { name: "Healthcare Innovation", mentions: 723 },
    { name: "Space Exploration", mentions: 654 },
  ];

  const velocityColors = {
    rising: "text-green-600",
    stable: "text-blue-600",
    falling: "text-orange-600",
  };

  const velocityBg = {
    rising: "bg-green-600/10 border-green-600/30",
    stable: "bg-blue-600/10 border-blue-600/30",
    falling: "bg-orange-600/10 border-orange-600/30",
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-3 mb-6"
      >
        <Lightbulb className="w-6 h-6 text-primary" />
        <div>
          <h2 className="text-2xl font-semibold text-foreground">Insights & Analytics</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Discover patterns and trends across your sources
          </p>
        </div>
      </motion.div>

      <Tabs defaultValue="1h" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="1h">Last Hour</TabsTrigger>
          <TabsTrigger value="6h">Last 6 Hours</TabsTrigger>
          <TabsTrigger value="24h">Last 24 Hours</TabsTrigger>
        </TabsList>

        <TabsContent value="1h" className="space-y-6 mt-6">
          {/* Trending Topics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 rounded-xl border border-border/50 backdrop-blur-xl bg-card/50"
          >
            <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Trending Topics
            </h3>
            <div className="space-y-3">
              {trendingTopics.map((topic, index) => (
                <motion.div
                  key={topic.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex items-center justify-between p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-semibold text-muted-foreground w-6">
                      {index + 1}
                    </span>
                    <span className="text-foreground">{topic.name}</span>
                  </div>
                  <Badge variant="secondary">{topic.mentions.toLocaleString()} mentions</Badge>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Topic Clusters */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="p-6 rounded-xl border border-border/50 backdrop-blur-xl bg-card/50"
          >
            <h3 className="text-lg font-semibold text-foreground mb-4">Topic Clusters</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {topicClusters.map((cluster, index) => (
                <motion.div
                  key={cluster.topic}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ scale: 1.02 }}
                  className={`p-4 rounded-lg border ${velocityBg[cluster.velocity]} transition-all cursor-pointer`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <h4 className="font-semibold text-foreground">{cluster.topic}</h4>
                    <TrendingUp className={`w-4 h-4 ${velocityColors[cluster.velocity]}`} />
                  </div>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-2xl font-bold text-foreground">{cluster.count}</span>
                    <span className="text-sm text-muted-foreground">stories</span>
                    <Badge
                      variant="secondary"
                      className={`ml-auto ${velocityColors[cluster.velocity]}`}
                    >
                      {cluster.velocity}
                    </Badge>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {cluster.keywords.map((keyword) => (
                      <Badge
                        key={keyword}
                        variant="outline"
                        className="text-xs bg-background/50"
                      >
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </TabsContent>

        <TabsContent value="6h" className="space-y-6 mt-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-12 rounded-xl border border-border/50 backdrop-blur-xl bg-card/50 text-center"
          >
            <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">6-Hour Analytics</h3>
            <p className="text-muted-foreground">
              Extended analytics for the last 6 hours would appear here
            </p>
          </motion.div>
        </TabsContent>

        <TabsContent value="24h" className="space-y-6 mt-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-12 rounded-xl border border-border/50 backdrop-blur-xl bg-card/50 text-center"
          >
            <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">24-Hour Analytics</h3>
            <p className="text-muted-foreground">
              Daily analytics and trends for the last 24 hours would appear here
            </p>
          </motion.div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
