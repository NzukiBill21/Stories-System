import { motion } from "motion/react";
import { StoryCard, Story } from "./StoryCard";

interface DashboardProps {
  stories: Story[];
  onStorySelect: (story: Story) => void;
  loadError?: string | null;
}

export function Dashboard({ stories, onStorySelect, loadError }: DashboardProps) {
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
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">
              {loadError ? "Cannot Load Stories" : "No Stories Yet"}
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              {loadError ?? "Start scraping to discover trending content from TikTok, Facebook, and other platforms."}
            </p>
            <p className="text-xs text-muted-foreground">
              {loadError
                ? "Fix the issue above, then refresh the page. Ensure MySQL is running in XAMPP and the backend is started (cd backend && python main.py)."
                : "Go to Sources Management to trigger scraping, or wait for automatic scraping to run."}
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
