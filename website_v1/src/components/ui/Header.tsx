'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePathname } from 'next/navigation';
import { Button } from './Button';
import { 
  Menu, 
  X, 
  LogIn, 
  UserPlus, 
  Settings, 
  LogOut,
  ChevronDown,
  Zap,
  Shield,
  Eye,
  Brain,
  UserCircle
} from 'lucide-react';
import Link from 'next/link';
import type { User } from '@/types/auth';

export default function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    // Check authentication status on mount
    const checkAuth = async () => {
      try {
        const { authService } = await import('@/lib/auth');
        if (authService.isAuthenticated()) {
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
        }
      } catch (error) {
        console.error('Auth check error:', error);
      }
    };

    checkAuth();
  }, []);

  const navigation = [
    { name: 'Studio', href: '/studio', icon: Zap },
    { name: 'Products', href: '/products', icon: Brain },
    { name: 'Vision', href: '/vision', icon: Eye },
    { name: 'About', href: '/about', icon: Shield },
  ];

  const handleSignIn = () => {
    window.open('/auth/login', '_self');
  };

  const handleSignOut = async () => {
    try {
      const { authService } = await import('@/lib/auth');
      await authService.logout();
      setUser(null);
      setUserMenuOpen(false);
    } catch (error) {
      console.error('Logout error:', error);
      // Still clear user state even if logout request fails
      setUser(null);
      setUserMenuOpen(false);
    }
  };

  // Hide header on studio page
  if (pathname === '/studio') {
    return null;
  }

  return (
    <>
      <motion.header 
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled 
            ? 'bg-[var(--background)]/90 backdrop-blur-xl border-b border-[var(--border)]' 
            : 'bg-[var(--background)]'
        }`}
        style={{marginTop: 0, paddingTop: 0, top: 0, position: 'fixed'}}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <div className="container mx-auto px-2 sm:px-4 max-w-none">
          <div className="flex items-center justify-between h-16 pt-2">
            
            {/* Logo */}
            <Link href="/" className="flex items-center gap-3 group">
              <motion.div 
                className="relative"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <div className="w-8 h-8 bg-gradient-to-br from-[var(--gradient-start)] to-[var(--gradient-end)] rounded-lg flex items-center justify-center">
                  <motion.div
                    className="text-white font-bold text-sm"
                    initial={{ rotate: 0 }}
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                  >
                    Λ
                  </motion.div>
                </div>
              </motion.div>
              <span className="text-lg text-[var(--text-primary)] group-hover:text-[var(--accent)] transition-colors" style={{ fontFamily: 'Helvetica Neue, -apple-system, BlinkMacSystemFont, sans-serif', fontWeight: 100 }}>
                LUKHΛS
              </span>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center space-x-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link key={item.name} href={item.href}>
                    <motion.div
                      className="flex items-center gap-1 px-2 py-2 rounded-lg text-[var(--text-secondary)] hover:text-[var(--accent)] hover:bg-[var(--surface)]/50 transition-all duration-200 group"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Icon size={16} className="group-hover:rotate-12 transition-transform duration-200" />
                      <span className="font-medium">{item.name}</span>
                    </motion.div>
                  </Link>
                );
              })}
            </nav>

            {/* Auth Section */}
            <div className="hidden lg:flex items-center gap-2" style={{paddingTop: '10px'}}>
              {user ? (
                <div className="relative">
                  <motion.button
                    onClick={() => setUserMenuOpen(!userMenuOpen)}
                    className="flex items-center gap-3 p-2 rounded-lg hover:bg-[var(--surface)]/50 transition-colors"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="w-8 h-8 bg-gradient-to-br from-[var(--accent)] to-[var(--gradient-end)] rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-semibold">
                        {user.displayName ? user.displayName.split(' ').map((n: string) => n[0]).join('') : user.email.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div className="text-left">
                      <div className="text-sm font-medium text-[var(--text-primary)]">{user.displayName || user.email.split('@')[0]}</div>
                      <div className="text-xs text-[var(--text-secondary)]">{user.email}</div>
                    </div>
                    <ChevronDown size={16} className={`text-[var(--text-secondary)] transition-transform duration-200 ${userMenuOpen ? 'rotate-180' : ''}`} />
                  </motion.button>

                  <AnimatePresence>
                    {userMenuOpen && (
                      <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 10, scale: 0.95 }}
                        className="absolute right-0 mt-2 w-56 bg-[var(--surface)] border border-[var(--border)] rounded-xl shadow-2xl py-2"
                      >
                        <Link href="/profile" className="flex items-center gap-3 px-4 py-2 hover:bg-[var(--background)] transition-colors">
                          <UserCircle size={16} className="text-[var(--text-secondary)]" />
                          <span className="text-[var(--text-primary)]">Profile</span>
                        </Link>
                        <Link href="/settings" className="flex items-center gap-3 px-4 py-2 hover:bg-[var(--background)] transition-colors">
                          <Settings size={16} className="text-[var(--text-secondary)]" />
                          <span className="text-[var(--text-primary)]">Settings</span>
                        </Link>
                        <hr className="my-2 border-[var(--border)]" />
                        <button 
                          onClick={handleSignOut}
                          className="w-full flex items-center gap-3 px-4 py-2 hover:bg-red-500/10 hover:text-red-500 transition-colors text-left"
                        >
                          <LogOut size={16} />
                          <span>Sign Out</span>
                        </button>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Button 
                    variant="secondary" 
                    size="sm"
                    className="gap-1 px-2 text-xs"
                    onClick={handleSignIn}
                    disabled={isLoading}
                  >
                    <LogIn size={16} />
                    {isLoading ? 'Signing In...' : 'Sign In'}
                  </Button>
                  <Button 
                    size="sm"
                    className="gap-1 px-2 text-xs bg-gradient-to-r from-[var(--gradient-start)] to-[var(--gradient-end)]"
                    onClick={() => window.open('/auth/signup', '_self')}
                  >
                    <UserPlus size={16} />
                    Start
                  </Button>
                </div>
              )}
            </div>

            {/* Mobile menu button */}
            <motion.button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-lg hover:bg-[var(--surface)]/50 transition-colors"
              whileTap={{ scale: 0.95 }}
            >
              {mobileMenuOpen ? (
                <X size={24} className="text-[var(--text-primary)]" />
              ) : (
                <Menu size={24} className="text-[var(--text-primary)]" />
              )}
            </motion.button>
          </div>

          {/* Mobile Navigation */}
          <AnimatePresence>
            {mobileMenuOpen && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="lg:hidden border-t border-[var(--border)] pt-4 pb-6 mt-4"
              >
                <div className="flex flex-col space-y-2">
                  {navigation.map((item) => {
                    const Icon = item.icon;
                    return (
                      <Link 
                        key={item.name} 
                        href={item.href}
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        <motion.div
                          className="flex items-center gap-3 p-3 rounded-lg hover:bg-[var(--surface)]/50 transition-colors"
                          whileTap={{ scale: 0.98 }}
                        >
                          <Icon size={20} className="text-[var(--accent)]" />
                          <span className="text-[var(--text-primary)] font-medium">{item.name}</span>
                        </motion.div>
                      </Link>
                    );
                  })}
                  
                  <hr className="my-4 border-[var(--border)]" />
                  
                  {user ? (
                    <div className="flex flex-col space-y-2">
                      <div className="flex items-center gap-3 p-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-[var(--accent)] to-[var(--gradient-end)] rounded-full flex items-center justify-center">
                          <span className="text-white font-semibold">
                            {user.displayName ? user.displayName.split(' ').map((n: string) => n[0]).join('') : user.email.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <div className="text-[var(--text-primary)] font-medium">{user.displayName || user.email.split('@')[0]}</div>
                          <div className="text-[var(--text-secondary)] text-sm">{user.email}</div>
                        </div>
                      </div>
                      <button 
                        onClick={handleSignOut}
                        className="flex items-center gap-3 p-3 hover:bg-red-500/10 hover:text-red-500 transition-colors text-left rounded-lg"
                      >
                        <LogOut size={20} />
                        <span>Sign Out</span>
                      </button>
                    </div>
                  ) : (
                    <div className="flex flex-col space-y-2">
                      <Button 
                        variant="secondary" 
                        className="w-full justify-center gap-2"
                        onClick={handleSignIn}
                        disabled={isLoading}
                      >
                        <LogIn size={16} />
                        {isLoading ? 'Signing In...' : 'Sign In'}
                      </Button>
                      <Button 
                        className="w-full justify-center gap-2 bg-gradient-to-r from-[var(--gradient-start)] to-[var(--gradient-end)]"
                        onClick={() => window.open('/auth/signup', '_self')}
                      >
                        <UserPlus size={16} />
                        Start
                      </Button>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.header>
      
      {/* Backdrop for mobile menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm lg:hidden"
            onClick={() => setMobileMenuOpen(false)}
          />
        )}
      </AnimatePresence>
      
      {/* Spacer to prevent content from hiding under fixed header */}
      <div className="h-16" />
    </>
  );
}