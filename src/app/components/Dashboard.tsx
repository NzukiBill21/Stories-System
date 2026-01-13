import { motion } from "motion/react";
import { StoryCard, Story } from "./StoryCard";

interface DashboardProps {
  stories: Story[];
  onStorySelect: (story: Story) => void;
}

export function Dashboard({ stories, onStorySelect }: DashboardProps) {
  return (
    <div className="space-y-4">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between mb-6"
      >
        <div>
          <h2 className="text-2xl font-semibold text-foreground">Trending Stories</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {stories.length} {stories.length === 1 ? 'story' : 'stories'} detected
          </p>
        </div>
      </motion.div>

      {stories.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-16 px-4"
        >
          <div className="max-w-md mx-auto">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
              <svg className="w-8 h-8 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">No Stories Yet</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Start scraping to discover trending content from TikTok, Facebook, and other platforms.
            </p>
            <p className="text-xs text-muted-foreground">
              Go to Sources Management to trigger scraping, or wait for automatic scraping to run.
            </p>
          </div>
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {stories.map((story, index) => (
            <motion.div
              key={story.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <StoryCard story={story} onClick={() => onStorySelect(story)} />
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
