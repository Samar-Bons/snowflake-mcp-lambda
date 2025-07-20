// ABOUTME: Main application header with navigation and user menu
// ABOUTME: Displays application title and authenticated user controls

import { UserMenu } from '../auth/UserMenu';
import { ChatIcon } from '../icons';

export function Header() {
  return (
    <header className="bg-slate-800 border-b border-slate-700">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <ChatIcon className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-bold text-white">Snowflake Chat</h1>
          </div>
          <UserMenu />
        </div>
      </div>
    </header>
  );
}
