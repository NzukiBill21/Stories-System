import { LayoutDashboard, Settings, Database, Lightbulb, Moon, Sun } from "lucide-react";
import { motion } from "motion/react";

interface SidebarProps {
  activeView: string;
  onViewChange: (view: string) => void;
  theme: "light" | "dark";
  onThemeToggle: () => void;
}

export function Sidebar({ activeView, onViewChange, theme, onThemeToggle }: SidebarProps) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "sources", label: "Sources", icon: Database },
    { id: "control", label: "Controls", icon: Settings },
    { id: "insights", label: "Insights", icon: Lightbulb },
  ];

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 border-r border-border/50 backdrop-blur-xl bg-sidebar/80 flex flex-col">
      <div className="p-6">
        <h1 className="text-xl font-semibold tracking-tight text-sidebar-foreground">
          Editorial Intelligence
        </h1>
        <p className="text-xs text-muted-foreground mt-1">Story Discovery Platform</p>
      </div>

      <nav className="flex-1 px-3">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;

          return (
            <motion.button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition-colors relative ${
                isActive
                  ? "text-sidebar-primary-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent/50"
              }`}
              whileHover={{ x: 4 }}
              whileTap={{ scale: 0.98 }}
            >
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute inset-0 bg-sidebar-primary rounded-lg"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                />
              )}
              <Icon className="w-5 h-5 relative z-10" />
              <span className="relative z-10">{item.label}</span>
            </motion.button>
          );
        })}
      </nav>

      <div className="p-3 border-t border-border/50">
        <button
          onClick={onThemeToggle}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sidebar-foreground hover:bg-sidebar-accent/50 transition-colors"
        >
          {theme === "light" ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
          <span>{theme === "light" ? "Dark Mode" : "Light Mode"}</span>
        </button>
      </div>
    </aside>
  );
}
