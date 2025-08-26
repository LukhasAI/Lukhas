import { useState, useEffect } from 'react';
import { Menu, X, Shield, Lock, Key, Globe, Fingerprint } from 'lucide-react';

export default function SimpleLukhasSystem() {
  const [authState, setAuthState] = useState('unauthenticated'); // 'unauthenticated', 'authenticating', 'authenticated'
  const [currentTier, setCurrentTier] = useState(1); // Tiers 1-5
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  // Handle login form submission
  const handleLogin = (e) => {
    if (e) e.preventDefault();
    setAuthState('authenticating');

    // Simulate login process
    setTimeout(() => {
      if (username && password) {
        setAuthState('authenticated');
        setCurrentTier(1); // Start at Tier 1
      } else {
        setAuthState('unauthenticated');
        alert('Please enter credentials');
      }
    }, 1000);
  };

  // Handle tier upgrade
  const upgradeTier = () => {
    if (currentTier < 5) {
      setAuthState('authenticating');

      // Simulate verification process
      setTimeout(() => {
        setCurrentTier(prev => prev + 1);
        setAuthState('authenticated');
      }, 1000);
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

  return (
    <div className="min-h-screen bg-gradient-to-b from-black to-gray-900 text-white p-6">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-black bg-opacity-80 backdrop-blur-sm py-4 z-10">
        <div className="container mx-auto flex justify-between items-center px-4">
          <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
            LUKHΛS ΛID
          </div>

          {authState === 'authenticated' ? (
            <button
              onClick={handleLogout}
              className="px-4 py-2 rounded-full border border-white hover:bg-white hover:text-black transition-all"
            >
              Log Out
            </button>
          ) : (
            <div className="invisible">Placeholder</div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto pt-24 flex flex-col items-center">
        {/* Central Lambda Symbol */}
        <div className="text-8xl font-bold my-8 text-center">
          <span className={
            authState === 'unauthenticated'
              ? 'text-blue-500'
              : authState === 'authenticating'
                ? 'text-yellow-400'
                : currentTier === 5
                  ? 'text-yellow-300'
                  : 'text-purple-500'
          }>
            Λ
          </span>
        </div>

        {/* Login Form */}
        {authState === 'unauthenticated' && (
          <div className="w-full max-w-md bg-black bg-opacity-50 rounded-xl p-8 border border-gray-800">
            <h2 className="text-2xl font-bold text-center mb-6">ΛID Access</h2>
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm mb-1">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg bg-gray-900 border border-gray-700 focus:border-blue-500 focus:outline-none"
                  placeholder="Enter your username"
                />
              </div>
              <div>
                <label className="block text-sm mb-1">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg bg-gray-900 border border-gray-700 focus:border-blue-500 focus:outline-none"
                  placeholder="Enter your password"
                />
              </div>

              <button
                type="submit"
                className="w-full px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all mt-2"
              >
                Log In
              </button>
            </form>
          </div>
        )}

        {/* Authenticating State */}
        {authState === 'authenticating' && (
          <div className="w-full max-w-md bg-black bg-opacity-50 rounded-xl p-8 border border-gray-800 text-center">
            <h2 className="text-2xl font-bold mb-4">Verifying Identity</h2>
            <p className="text-gray-300 mb-6">Please wait while we authenticate your credentials...</p>
            <div className="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-blue-500 to-purple-600 animate-pulse"
                   style={{width: '70%'}}></div>
            </div>
          </div>
        )}

        {/* Authenticated State */}
        {authState === 'authenticated' && (
          <div className="w-full max-w-2xl bg-black bg-opacity-50 rounded-xl p-8 border border-gray-800">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-bold">Welcome, {username}</h2>
                <div className="mt-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    currentTier === 5
                      ? 'bg-yellow-500 bg-opacity-20 text-yellow-300 border border-yellow-500'
                      : 'bg-purple-500 bg-opacity-20 text-purple-300 border border-purple-500'
                  }`}>
                    Tier {currentTier} Security
                  </span>
                </div>
              </div>

              {currentTier < 5 && (
                <button
                  onClick={upgradeTier}
                  className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all"
                >
                  Upgrade to Tier {currentTier + 1}
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-900 bg-opacity-60 rounded-lg p-4 border border-gray-800">
                <h3 className="text-lg font-semibold mb-3 flex items-center">
                  <Shield className="mr-2 text-blue-400" size={20} />
                  Identity Status
                </h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Security Level</span>
                    <span>{getTierName(currentTier)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Status</span>
                    <span className="text-green-400">Active</span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-900 bg-opacity-60 rounded-lg p-4 border border-gray-800">
                <h3 className="text-lg font-semibold mb-3 flex items-center">
                  <Lock className="mr-2 text-blue-400" size={20} />
                  Security Factors
                </h3>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Password</span>
                    <span className="text-green-400">Verified</span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Emoji + Keyword</span>
                    <span className={currentTier >= 2 ? "text-green-400" : "text-gray-500"}>
                      {currentTier >= 2 ? "Verified" : "Not Required"}
                    </span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">WebAuthn</span>
                    <span className={currentTier >= 3 ? "text-green-400" : "text-gray-500"}>
                      {currentTier >= 3 ? "Verified" : "Not Required"}
                    </span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Biometric ID</span>
                    <span className={currentTier >= 4 ? "text-green-400" : "text-gray-500"}>
                      {currentTier >= 4 ? "Verified" : "Not Required"}
                    </span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Blockchain</span>
                    <span className={currentTier >= 5 ? "text-green-400" : "text-gray-500"}>
                      {currentTier >= 5 ? "Verified" : "Not Required"}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Current Tier Display */}
            <div className="mt-6 p-4 rounded-lg border border-gray-700 bg-black bg-opacity-30">
              <h3 className="text-xl font-semibold mb-3">
                Current Security: {getTierName(currentTier)}
              </h3>
              <p className="text-gray-300">
                {currentTier === 1 && "Basic username + password authentication."}
                {currentTier === 2 && "Enhanced security with emoji-keyword combination for added protection."}
                {currentTier === 3 && "Passwordless authentication using WebAuthn and device biometrics."}
                {currentTier === 4 && "Full multi-biometric identity protocol with Face ID and Voice ID."}
                {currentTier === 5 && "Supreme security with blockchain attestation and Ed25519 signatures."}
              </p>
            </div>

            {/* QR Glyph for Tier 4+ */}
            {currentTier >= 4 && (
              <div className="mt-6 p-6 rounded-lg border border-gray-700 bg-black bg-opacity-30 flex flex-col items-center">
                <h3 className="text-xl font-semibold mb-4">ΛID QRGlyph</h3>
                <div className="w-48 h-48 border-2 border-purple-500 rounded-lg p-2 flex items-center justify-center">
                  <div className="relative w-full h-full bg-black flex items-center justify-center">
                    {/* Stylized QR with lambda symbol */}
                    <div className="absolute inset-0 grid grid-cols-7 grid-rows-7 gap-1 p-2">
                      {Array.from({ length: 49 }).map((_, i) => {
                        // Simple pattern for QR modules
                        const isActive = Math.random() > 0.4;
                        return (
                          <div
                            key={i}
                            className={`rounded-sm ${isActive ? 'bg-purple-500' : 'bg-transparent'}`}
                          />
                        );
                      })}
                    </div>
                    <div className="text-3xl font-bold z-10 text-transparent">Λ</div>
                  </div>
                </div>
                <p className="mt-4 text-sm text-center text-gray-400">
                  This QR Glyph represents your unique ΛID identity hash
                </p>
              </div>
            )}
          </div>
        )}

        {/* Feature Overview - Only shown when not logged in */}
        {authState === 'unauthenticated' && (
          <div className="mt-16 max-w-4xl text-center">
            <h2 className="text-3xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
              The Future of Identity Security
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
              <div className="bg-black bg-opacity-50 p-6 rounded-xl border border-gray-800">
                <div className="w-16 h-16 mx-auto rounded-full bg-blue-900 bg-opacity-30 flex items-center justify-center mb-4">
                  <Shield size={32} className="text-blue-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Tiered Security</h3>
                <p className="text-gray-400">
                  Five progressive security tiers from basic to enterprise-grade blockchain verification.
                </p>
              </div>

              <div className="bg-black bg-opacity-50 p-6 rounded-xl border border-gray-800">
                <div className="w-16 h-16 mx-auto rounded-full bg-purple-900 bg-opacity-30 flex items-center justify-center mb-4">
                  <Fingerprint size={32} className="text-purple-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Multi-Biometric</h3>
                <p className="text-gray-400">
                  Advanced verification with Face ID, Voice ID, and emoji-keyword combinations.
                </p>
              </div>

              <div className="bg-black bg-opacity-50 p-6 rounded-xl border border-gray-800">
                <div className="w-16 h-16 mx-auto rounded-full bg-indigo-900 bg-opacity-30 flex items-center justify-center mb-4">
                  <Globe size={32} className="text-indigo-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Blockchain Verified</h3>
                <p className="text-gray-400">
                  Tier 5 security with blockchain technology on Ethereum and XRP for tamper-proof identity.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 py-8 border-t border-gray-800">
        <div className="container mx-auto text-center text-gray-500 text-sm">
          &copy; 2025 LUKHΛS Systems. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
