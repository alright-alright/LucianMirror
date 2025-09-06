import React from 'react';
import { 
  Bell, 
  Search, 
  Moon, 
  Sun, 
  Monitor,
  RefreshCw,
  Zap,
  Cloud,
  Activity
} from 'lucide-react';
import clsx from 'clsx';
import { APIConnectionIndicator } from '../status/APIConnectionIndicator';
import { LucianMetrics } from '../metrics/LucianMetrics';

interface TopBarProps {
  title?: string;
  showSearch?: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({ 
  title = 'Dashboard', 
  showSearch = true 
}) => {
  const [isDark, setIsDark] = React.useState(true);
  const [mode, setMode] = React.useState<'sprite' | 'story' | 'video'>('sprite');
  const [showMetrics, setShowMetrics] = React.useState(false);

  return (
    <>
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
        {/* Left side */}
        <div className="flex items-center space-x-6">
          <h2 className="text-2xl font-bold text-white">{title}</h2>
          
          {/* Mode Switcher */}
          <div className="flex items-center bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setMode('sprite')}
              className={clsx(
                'px-3 py-1.5 rounded-md text-sm font-medium transition-all',
                mode === 'sprite'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Zap className="w-4 h-4 inline mr-1" />
              Sprites
            </button>
            <button
              onClick={() => setMode('story')}
              className={clsx(
                'px-3 py-1.5 rounded-md text-sm font-medium transition-all',
                mode === 'story'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              Story
            </button>
            <button
              onClick={() => setMode('video')}
              className={clsx(
                'px-3 py-1.5 rounded-md text-sm font-medium transition-all',
                mode === 'video'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              Video
            </button>
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Search */}
          {showSearch && (
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search sprites..."
                className="pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 w-64"
              />
            </div>
          )}

          {/* API Connection Indicator - Your Signature Style */}
          <APIConnectionIndicator />

          {/* LucianOS Metrics Toggle */}
          <button 
            onClick={() => setShowMetrics(!showMetrics)}
            className={clsx(
              "p-2 rounded-lg transition-colors",
              showMetrics ? "bg-purple-900/30 text-purple-400" : "hover:bg-gray-800 text-gray-400"
            )}
            title="Toggle LucianOS Metrics"
          >
            <Activity className="w-5 h-5" />
          </button>

          {/* Sync Button */}
          <button className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
            <RefreshCw className="w-5 h-5 text-gray-400" />
          </button>

          {/* Notifications */}
          <button className="p-2 hover:bg-gray-800 rounded-lg transition-colors relative">
            <Bell className="w-5 h-5 text-gray-400" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* Theme Toggle */}
          <button
            onClick={() => setIsDark(!isDark)}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            {isDark ? (
              <Sun className="w-5 h-5 text-gray-400" />
            ) : (
              <Moon className="w-5 h-5 text-gray-400" />
            )}
          </button>

          {/* Display Mode */}
          <button className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
            <Monitor className="w-5 h-5 text-gray-400" />
          </button>
        </div>
      </div>

        {/* Breadcrumbs */}
        <div className="flex items-center space-x-2 mt-4 text-sm">
          <span className="text-gray-400">Home</span>
          <span className="text-gray-600">/</span>
          <span className="text-white">{title}</span>
        </div>
      </header>

      {/* LucianOS Metrics Panel - Slides Down */}
      {showMetrics && (
        <div className="bg-gray-900/95 backdrop-blur-sm border-b border-gray-800 px-6 py-4">
          <LucianMetrics />
        </div>
      )}
    </>
  );
};