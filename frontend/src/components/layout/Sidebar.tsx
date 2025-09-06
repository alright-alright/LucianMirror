import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  Sparkles, 
  Image, 
  BookOpen, 
  Settings,
  Video,
  Palette,
  Users,
  Wand2,
  Database
} from 'lucide-react';
import clsx from 'clsx';

interface NavItem {
  path: string;
  label: string;
  icon: React.ElementType;
  badge?: string;
}

const navItems: NavItem[] = [
  { path: '/', label: 'Dashboard', icon: Home },
  { path: '/character-setup', label: 'Character Setup', icon: Users },
  { path: '/sprites', label: 'Sprite Library', icon: Sparkles },
  { path: '/editor', label: 'Sprite Editor', icon: Wand2 },
  { path: '/composer', label: 'Scene Composer', icon: Image },
  { path: '/story', label: 'Story Mode', icon: BookOpen },
  { path: '/backgrounds', label: 'Backgrounds', icon: Palette },
  { path: '/video', label: 'Video Creator', icon: Video, badge: 'Soon' },
  { path: '/library', label: 'Asset Library', icon: Database },
  { path: '/settings', label: 'Settings', icon: Settings }
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-gray-900 text-white h-screen flex flex-col border-r border-gray-800">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center space-x-2">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold">LucianMirror</h1>
            <p className="text-xs text-gray-400">Sprite Engine v2.0</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4">
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center justify-between px-4 py-3 rounded-lg transition-all duration-200',
                    'hover:bg-gray-800 hover:text-white',
                    isActive
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                      : 'text-gray-400'
                  )
                }
              >
                <div className="flex items-center space-x-3">
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </div>
                {item.badge && (
                  <span className="px-2 py-1 text-xs bg-gray-700 rounded-full">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center space-x-3 px-4 py-2">
          <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-blue-500 rounded-full"></div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">User</p>
            <p className="text-xs text-gray-400 truncate">Free Plan</p>
          </div>
        </div>
      </div>
    </aside>
  );
};