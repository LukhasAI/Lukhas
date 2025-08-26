import { useState, useEffect } from 'react';

export default function NordicLukhas() {
  const [authState, setAuthState] = useState('unauthenticated');
  const [currentTier, setCurrentTier] = useState(1);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [currentImage, setCurrentImage] = useState(0);
  const [fadeIn, setFadeIn] = useState(true);

  // Nature-inspired background images
  const backgroundImages = [
    "https://images.unsplash.com/photo-1574169208507-84376144848b?auto=format&fit=crop&q=80", // Nordic mountains
    "https://images.unsplash.com/photo-1486082570281-d942af5c39b7?auto=format&fit=crop&q=80", // White marble
    "https://images.unsplash.com/photo-1481262492146-9a13e7b92450?auto=format&fit=crop&q=80", // Dark stone
    "https://images.unsplash.com/photo-1476610182048-b716b8518aae?auto=format&fit=crop&q=80"  // Earth landscape
  ];

  // Handle login
  const handleLogin = () => {
    if (username && password) {
      setAuthState('authenticated');
    } else {
      alert('Please enter credentials');
    }
  };

  // Handle tier upgrade
  const upgradeTier = () => {
    if (currentTier < 5) {
      setCurrentTier(prev => prev + 1);
    }
  };

  // Handle logout
  const handleLogout = () => {
    setAuthState('unauthenticated');
    setCurrentTier(1);
    setUsername('');
    setPassword('');
  };

  // Get tier name
  const getTierName = (tier) => {
    switch(tier) {
      case 1: return 'Basic Login';
      case 2: return 'Enhanced Login';
      case 3: return 'Passwordless & WebAuthn';
      case 4: return 'Full ΛID Protocol';
      case 5: return 'Lambda Supreme';
      default: return 'Unknown';
    }
  };

  // Background image transition
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

        {/* Central Content */}
        <main className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-md w-full">
            {/* Central Lambda Symbol */}
            <div className="flex justify-center mb-16">
              <div className="text-white text-9xl font-extralight leading-none tracking-wide opacity-90">
                Λ
              </div>
            </div>

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
                        <span className="text-white text-sm">{getTierName(currentTier)}</span>
                      </div>

                      <div className="flex justify-between items-center">
                        <span className="text-white text-opacity-70 text-sm">Verification</span>
                        <span className="text-white text-sm">Complete</span>
                      </div>

                      <div className="flex justify-between items-center">
                        <span className="text-white text-opacity-70 text-sm">Session</span>
                        <span className="text-white text-sm">Active</span>
                      </div>
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

                <div className="mt-8 pt-8 border-t border-white border-opacity-10">
                  <div className="text-white text-opacity-70 text-sm tracking-wider mb-4">
                    CURRENT SECURITY LEVEL
                  </div>
                  <div className="text-white text-sm leading-relaxed">
                    {currentTier === 1 && "Standard authentication protocol with minimal security requirements. Suitable for basic access."}
                    {currentTier === 2 && "Enhanced protocol utilizing secondary verification measures for improved identity confirmation."}
                    {currentTier === 3 && "Advanced passwordless authentication utilizing physical security keys and biometric verification."}
                    {currentTier === 4 && "Comprehensive biometric identity verification with facial recognition and voice pattern analysis."}
                    {currentTier === 5 && "Ultimate security with decentralized blockchain attestation and post-quantum cryptographic signatures."}
                  </div>
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
    </div>
  );
}
