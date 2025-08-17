/*
 * ================================================================================
 * LUKHAS ONEIRIC CORE - Navigation Bar Component
 * ================================================================================
 * Author: LUKHAS Development Team
 * Version: 1.0.0
 * Date: 2025-01-10
 * 
 * Description:
 * Main navigation bar component for the Oneiric Core application.
 * Provides navigation links and user authentication interface.
 * 
 * Copyright (c) 2025 LUKHAS. All rights reserved.
 * Licensed under the MIT License.
 * ================================================================================
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavBarProps {
  onOpenSettings: () => void;
}

export default function NavBar({ onOpenSettings }: NavBarProps) {
  const pathname = usePathname();
  // Preview mode - simulate user state
  const isAuthenticated = false; // Set to true for authenticated preview

  const navItems = [
    { name: 'Oracle Chat', href: '/' },
    { name: 'Dream Journal', href: '/journal' },
    { name: 'Symbol Explorer', href: '/symbols' },
  ];

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-4xl mx-auto px-4 flex justify-between items-center h-16">
        <div className="font-bold text-xl text-gray-900">
          Oneiric Core
        </div>
        
        <div className="flex items-center space-x-4">
          {navItems.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                pathname === item.href
                  ? 'bg-gray-900 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              {item.name}
            </Link>
          ))}
          
          {isAuthenticated && (
            <button
              onClick={onOpenSettings}
              title="Settings"
              className="text-sm px-3 py-2 border border-gray-300 rounded hover:bg-gray-100 transition-colors"
            >
              ⚙️
            </button>
          )}
          
          <div className="flex items-center space-x-2">
            {isAuthenticated ? (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">
                  demo@example.com
                </span>
                <button 
                  onClick={() => console.log('Sign out clicked')}
                  className="text-sm px-3 py-2 text-gray-700 hover:bg-gray-100 rounded"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <button 
                onClick={() => console.log('Sign in clicked')}
                className="text-sm px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

/*
 * ================================================================================
 * END OF LUKHAS ONEIRIC CORE - Navigation Bar Component
 * 
 * This component provides the main navigation interface for the Oneiric Core
 * application, including links to key features and user authentication controls.
 * 
 * For support: contact@lukhas.com
 * Documentation: https://docs.lukhas.com/oneiric-core
 * ================================================================================
 */
