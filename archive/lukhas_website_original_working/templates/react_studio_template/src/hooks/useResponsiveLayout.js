/**
 * Responsive Layout Hook
 * Bay Area Standards: Mobile-first responsive design 📱
 */
import { useState, useEffect } from 'react'

export const useResponsiveLayout = () => {
  const [screenSize, setScreenSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1024,
    height: typeof window !== 'undefined' ? window.innerHeight : 768,
    isMobile: false,
    isTablet: false,
    isDesktop: false
  })

  useEffect(() => {
    const updateScreenSize = () => {
      const width = window.innerWidth
      const height = window.innerHeight
      
      setScreenSize({
        width,
        height,
        isMobile: width < 768,
        isTablet: width >= 768 && width < 1024,
        isDesktop: width >= 1024
      })
    }

    // Initial call
    updateScreenSize()

    // Debounced resize handler
    let timeoutId
    const debouncedResize = () => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(updateScreenSize, 150)
    }

    window.addEventListener('resize', debouncedResize, { passive: true })
    
    return () => {
      window.removeEventListener('resize', debouncedResize)
      clearTimeout(timeoutId)
    }
  }, [])

  return screenSize
}

// Adaptive layout configurations
export const getLayoutConfig = (screenSize) => {
  if (screenSize.isMobile) {
    return {
      showLeftDock: false,
      showRightDock: false,
      headerHeight: '60px',
      chatModeDisplay: 'icons', // Only show icons
      commandPaletteSize: 'full', // Take full width on mobile
    }
  }
  
  if (screenSize.isTablet) {
    return {
      showLeftDock: false,
      showRightDock: true,
      headerHeight: '64px',
      chatModeDisplay: 'minimal', // Show icon + label
      commandPaletteSize: 'large',
    }
  }
  
  // Desktop
  return {
    showLeftDock: true,
    showRightDock: true,
    headerHeight: '80px',
    chatModeDisplay: 'full', // Show full labels
    commandPaletteSize: 'normal',
  }
}
