import { useState, useEffect } from 'react';

export default function NordicCookies() {
  // State for authentication
  const [authState, setAuthState] = useState('unauthenticated');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [currentTier, setCurrentTier] = useState(1);

  // State for background images
  const [currentImage, setCurrentImage] = useState(0);
  const [fadeIn, setFadeIn] = useState(true);

  // State for cookie consent
  const [showCookieModal, setShowCookieModal] = useState(true);
  const [cookieState, setCookieState] = useState('initial'); // 'initial', 'choosing', 'rewarded'
  const [cookiePreferences, setCookiePreferences] = useState({
    essential: true,
    functional: false,
    analytics: false,
    marketing: false
  });
  const [cookiePoints, setCookiePoints] = useState(0);
  const [rewardTier, setRewardTier] = useState(0);

  // Nature-inspired background images
  const backgroundImages = [
    "https://images.unsplash.com/photo-1574169208507-84376144848b?auto=format&fit=crop&q=80", // Nordic mountains
    "https://images.unsplash.com/photo-1486082570281-d942af5c39b7?auto=format&fit=crop&q=80", // White marble
    "https://images.unsplash.com/photo-1481262492146-9a13e7b92450?auto=format&fit=crop&q=80"  // Dark stone
  ];

  // Calculate privacy points based on preferences
  useEffect(() => {
    let points = 6; // Start with maximum points

    // Subtract points for each cookie type enabled
    if (cookiePreferences.functional) points -= 1;
    if (cookiePreferences.analytics) points -= 2;
    if (cookiePreferences.marketing) points -= 3;

    setCookiePoints(points);

    // Set reward tier based on privacy points
    if (points >= 6) {
      setRewardTier(3); // Highest tier (most private)
    } else if (points >= 4) {
      setRewardTier(2); // Mid tier
    } else if (points >= 1) {
      setRewardTier(1); // Basic tier
    } else {
      setRewardTier(0); // No reward (least private)
    }
  }, [cookiePreferences]);

  // Toggle cookie preferences
  const toggleCookiePreference = (type) => {
    if (type === 'essential') return;

    setCookiePreferences(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };

  // Submit cookie choices
  const submitCookieConsent = () => {
    setCookieState('rewarded');

    if (rewardTier > 0) {
      setTimeout(() => {
        setShowCookieModal(false);
      }, 3000);
    } else {
      setShowCookieModal(false);
    }
  };

  // Handle background image transitions
  useEffect(() => {
    const interval = setInterval(() => {
      setFadeIn(false);
      setTimeout(() => {
        setCurrentImage((prev) => (prev + 1) % backgroundImages.length);
        setFadeIn(true);
      }, 1000);
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  // Handle login
  const handleLogin = () => {
    if (username && password) {
      setAuthState('authenticated');
    } else {
      alert('Please enter credentials');
    }
  };

  // Handle logout
  const handleLogout = () => {
    setAuthState('unauthenticated');
    setUsername('');
    setPassword('');
  };

  // Upgrade security tier
  const upgradeTier = () => {
    if (currentTier < 5) {
      setCurrentTier(prev => prev + 1);
    }
  };

  return (
    <div className="min-h-screen overflow-hidden relative font-['Inter',sans-serif] font-extralight">
      {/* Background images with fade transition */}
      <div className="fixed inset-0 z-[-1]">
        {backgroundImages.map((img, index) => (
          <div
            key={index}
            className="absolute inset-0 transition-opacity duration-1000"
            style={{
              backgroundImage: `url(${img})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              opacity: currentImage === index ? (fadeIn ? 1 : 0) : 0
            }}
          />
        ))}
        <div className="absolute inset-0 bg-black bg-opacity-40 backdrop-filter backdrop-blur-sm" />
      </div>

      {/* Main Content */}
      <div className="relative min-h-screen flex flex-col">
        {/* Header */}
        <header className="p-8">
          <div className="max-w-6xl mx-auto flex justify-between items-center">
            <div className="text-white text-2xl tracking-[0.15em] font-extralight">
              LUKHΛS
            </div>

            {authState === 'authenticated' && (
              <button
                onClick={handleLogout}
                className="px-6 py-2 border border-white border-opacity-30 rounded-sm text-white text-opacity-80 bg-black bg-opacity-20 hover:bg-opacity-30 backdrop-filter backdrop-blur-md transition-all text-sm font-light tracking-wider"
              >
                DISCONNECT
              </button>
            )}
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-md w-full">
            {/* Lambda Symbol */}
            <div className="flex justify-center mb-16">
              <div className="text-white text-9xl font-extralight leading-none tracking-wide opacity-90">
                Λ
              </div>
            </div>

            {/* Login or Dashboard Panel */}
            {authState === 'unauthenticated' ? (
              <div className="bg-black bg-opacity-30 backdrop-filter backdrop-blur-md border border-white border-opacity-10 p-8 rounded-sm">
                <h2 className="text-white text-xl font-extralight tracking-wide mb-8 text-center">
                  IDENTITY ACCESS
                </h2>

                <div className="space-y-6">
                  <div>
                    <label className="block text-white text-opacity-80 text-sm tracking-wider mb-2">
                      USERNAME
                    </label>
                    <input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className="w-full bg-black bg-opacity-30 border border-white border-opacity-20 rounded-sm px-4 py-3 text-white outline-none focus:border-opacity-40"
                      placeholder="Enter username"
                    />
                  </div>

                  <div>
                    <label className="block text-white text-opacity-80 text-sm tracking-wider mb-2">
                      PASSWORD
                    </label>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full bg-black bg-opacity-30 border border-white border-opacity-20 rounded-sm px-4 py-3 text-white outline-none focus:border-opacity-40"
                      placeholder="Enter password"
                    />
                  </div>

                  <button
                    onClick={handleLogin}
                    className="w-full bg-white bg-opacity-10 hover:bg-opacity-20 border border-white border-opacity-30 text-white py-3 rounded-sm transition-all tracking-widest text-sm font-light"
                  >
                    AUTHENTICATE
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-black bg-opacity-30 backdrop-filter backdrop-blur-md border border-white border-opacity-10 p-8 rounded-sm">
                <div className="mb-8">
                  <h2 className="text-white text-xl font-extralight tracking-wide">
                    {username}
                  </h2>
                  <div className="text-white text-opacity-70 text-sm tracking-wider mt-1">
                    SECURITY TIER {currentTier}
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="border border-white border-opacity-10 p-4 rounded-sm">
                    <h3 className="text-white text-opacity-80 tracking-wider text-sm mb-4">
                      IDENTITY STATUS
                    </h3>

                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-white text-opacity-70 text-sm">Security Level</span>
                        <span className="text-white text-sm">Tier {currentTier}</span>
                      </div>

                      <div className="flex justify-between items-center">
                        <span className="text-white text-opacity-70 text-sm">Verification</span>
                        <span className="text-white text-sm">Complete</span>
                      </div>

                      <div className="flex justify-between items-center">
                        <span className="text-white text-opacity-70 text-sm">Session</span>
                        <span className="text-white text-sm">Active</span>
                      </div>

                      {rewardTier >= 2 && (
                        <div className="flex justify-between items-center">
                          <span className="text-white text-opacity-70 text-sm">Extended Time</span>
                          <span className="text-white text-sm">Enabled</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {currentTier < 5 && (
                    <button
                      onClick={upgradeTier}
                      className="w-full bg-white bg-opacity-10 hover:bg-opacity-20 border border-white border-opacity-30 text-white py-3 rounded-sm transition-all tracking-widest text-sm font-light"
                    >
                      UPGRADE TO TIER {currentTier + 1}
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </main>

        {/* Footer */}
        <footer className="p-8">
          <div className="max-w-6xl mx-auto text-center">
            <div className="text-white text-opacity-50 text-xs tracking-wider">
              LUKHΛS SYSTEMS • EARTH DIVISION
            </div>
          </div>
        </footer>
      </div>

      {/* Cookie Consent Modal */}
      {showCookieModal && (
        <div className="fixed inset-0 flex items-center justify-center z-50 px-4">
          <div
            className="absolute inset-0 bg-black bg-opacity-70 backdrop-filter backdrop-blur-sm"
            onClick={() => cookieState === 'rewarded' && setShowCookieModal(false)}
          />

          <div className="relative max-w-md w-full bg-black bg-opacity-50 backdrop-filter backdrop-blur-lg border border-white border-opacity-20 rounded-sm overflow-hidden">
            {cookieState === 'initial' && (
              <div className="p-8">
                <h2 className="text-white text-xl font-extralight tracking-wide mb-2">
                  PRIVACY PREFERENCES
                </h2>
                <p className="text-white text-opacity-70 text-sm leading-relaxed mb-6">
                  We value your privacy. Unlike most sites, we reward you for protecting your data.
                  Disable optional cookies to unlock enhanced features and experiences.
                </p>

                <button
                  onClick={() => setCookieState('choosing')}
                  className="w-full bg-white bg-opacity-10 hover:bg-opacity-20 border border-white border-opacity-30 text-white py-3 rounded-sm transition-all tracking-widest text-sm font-light"
                >
                  CHOOSE PREFERENCES
                </button>

                <button
                  onClick={() => {
                    setCookiePreferences({
                      essential: true,
                      functional: false,
                      analytics: false,
                      marketing: false
                    });
                    setCookieState('rewarded');

                    setTimeout(() => setShowCookieModal(false), 3000);
                  }}
                  className="w-full mt-3 bg-transparent hover:bg-white hover:bg-opacity-5 text-white text-opacity-70 py-3 rounded-sm transition-all tracking-wider text-sm font-light"
                >
                  PRIVACY FIRST
                </button>
              </div>
            )}

            {cookieState === 'choosing' && (
              <div className="p-8">
                <h2 className="text-white text-xl font-extralight tracking-wide mb-6">
                  SELECT PREFERENCES
                </h2>

                <div className="space-y-4 mb-8">
                  {/* Essential Cookies - Always on and disabled */}
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="text-white text-sm">Essential</div>
                      <div className="text-white text-opacity-60 text-xs mt-1">Required for basic functionality</div>
                    </div>
                    <div className="relative">
                      <div className="w-12 h-6 bg-white bg-opacity-20 rounded-full"></div>
                      <div className="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full"></div>
                    </div>
                  </div>

                  {/* Functional Cookies */}
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="text-white text-sm">Functional</div>
                      <div className="text-white text-opacity-60 text-xs mt-1">
                        Store preferences and settings (costs 1 privacy point)
                      </div>
                    </div>
                    <div
                      className="relative cursor-pointer"
                      onClick={() => toggleCookiePreference('functional')}
                    >
                      <div className={`w-12 h-6 rounded-full transition-colors ${
                        cookiePreferences.functional ? 'bg-white bg-opacity-60' : 'bg-white bg-opacity-20'
                      }`}></div>
                      <div className={`absolute top-0.5 w-5 h-5 bg-white rounded-full transition-all ${
                        cookiePreferences.functional ? 'left-6' : 'left-0.5'
                      }`}></div>
                    </div>
                  </div>

                  {/* Analytics Cookies */}
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="text-white text-sm">Analytics</div>
                      <div className="text-white text-opacity-60 text-xs mt-1">
                        Track how you use our site (costs 2 privacy points)
                      </div>
                    </div>
                    <div
                      className="relative cursor-pointer"
                      onClick={() => toggleCookiePreference('analytics')}
                    >
                      <div className={`w-12 h-6 rounded-full transition-colors ${
                        cookiePreferences.analytics ? 'bg-white bg-opacity-60' : 'bg-white bg-opacity-20'
                      }`}></div>
                      <div className={`absolute top-0.5 w-5 h-5 bg-white rounded-full transition-all ${
                        cookiePreferences.analytics ? 'left-6' : 'left-0.5'
                      }`}></div>
                    </div>
                  </div>

                  {/* Marketing Cookies */}
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="text-white text-sm">Marketing</div>
                      <div className="text-white text-opacity-60 text-xs mt-1">
                        Show personalized content (costs 3 privacy points)
                      </div>
                    </div>
                    <div
                      className="relative cursor-pointer"
                      onClick={() => toggleCookiePreference('marketing')}
                    >
                      <div className={`w-12 h-6 rounded-full transition-colors ${
                        cookiePreferences.marketing ? 'bg-white bg-opacity-60' : 'bg-white bg-opacity-20'
                      }`}></div>
                      <div className={`absolute top-0.5 w-5 h-5 bg-white rounded-full transition-all ${
                        cookiePreferences.marketing ? 'left-6' : 'left-0.5'
                      }`}></div>
                    </div>
                  </div>
                </div>

                {/* Reward Display */}
                <div className="mb-6 border border-white border-opacity-10 rounded-sm p-4">
                  <div className="text-white text-opacity-80 text-sm tracking-wider mb-3">
                    PRIVACY REWARDS
                  </div>

                  <div className="flex items-center mb-3">
                    <div className="flex-1 h-2 bg-white bg-opacity-10 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-white bg-opacity-60 transition-all duration-500"
                        style={{ width: `${(cookiePoints / 6) * 100}%` }}
                      ></div>
                    </div>
                    <div className="ml-3 text-white text-sm">{cookiePoints}/6</div>
                  </div>

                  <div className="space-y-2">
                    <div className={`flex items-center ${rewardTier >= 1 ? 'text-white' : 'text-white text-opacity-40'}`}>
                      <div className={`w-3 h-3 rounded-full mr-2 ${
                        rewardTier >= 1 ? 'bg-white' : 'bg-white bg-opacity-20'
                      }`}></div>
                      <div className="text-xs">Enhanced security protocols</div>
                    </div>

                    <div className={`flex items-center ${rewardTier >= 2 ? 'text-white' : 'text-white text-opacity-40'}`}>
                      <div className={`w-3 h-3 rounded-full mr-2 ${
                        rewardTier >= 2 ? 'bg-white' : 'bg-white bg-opacity-20'
                      }`}></div>
                      <div className="text-xs">Faster application performance</div>
                    </div>

                    <div className={`flex items-center ${rewardTier >= 3 ? 'text-white' : 'text-white text-opacity-40'}`}>
                      <div className={`w-3 h-3 rounded-full mr-2 ${
                        rewardTier >= 3 ? 'bg-white' : 'bg-white bg-opacity-20'
                      }`}></div>
                      <div className="text-xs">Advanced dashboard features</div>
                    </div>
                  </div>
                </div>

                <button
                  onClick={submitCookieConsent}
                  className="w-full bg-white bg-opacity-10 hover:bg-opacity-20 border border-white border-opacity-30 text-white py-3 rounded-sm transition-all tracking-widest text-sm font-light"
                >
                  CONFIRM CHOICES
                </button>
              </div>
            )}

            {cookieState === 'rewarded' && (
              <div className="p-8 text-center">
                <div className="text-6xl mb-3">
                  {rewardTier === 0 && "📊"}
                  {rewardTier === 1 && "🔒"}
                  {rewardTier === 2 && "🛡️"}
                  {rewardTier === 3 && "✨"}
                </div>

                <h2 className="text-white text-xl font-extralight tracking-wide mb-2">
                  {rewardTier === 0 && "STANDARD EXPERIENCE"}
                  {rewardTier === 1 && "ENHANCED SECURITY"}
                  {rewardTier === 2 && "ADVANCED PRIVACY"}
                  {rewardTier === 3 && "MAXIMUM PRIVACY"}
                </h2>

                <p className="text-white text-opacity-70 text-sm leading-relaxed">
                  {rewardTier === 0 && "Preferences saved. Your experience includes all personalization features."}
                  {rewardTier === 1 && "You've unlocked enhanced security protocols by protecting some of your data."}
                  {rewardTier === 2 && "You've unlocked faster performance and enhanced security by valuing your privacy."}
                  {rewardTier === 3 && "You've unlocked all privacy rewards. Thank you for prioritizing your data privacy."}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
