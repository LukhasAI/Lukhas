'use client';

import { useUser } from '@clerk/nextjs';
import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '../../lib/api';

interface Symbol {
  symbol: string;
  frequency: number;
  emotional_charge: number;
  recent_dreams: string[];
}

export default function SymbolsPage() {
  const { user } = useUser();

  const { data: symbols, isLoading, error } = useQuery({
    queryKey: ['symbols', user?.id],
    queryFn: async () => {
      const response = await apiFetch('/api/symbols');
      return response.symbols as Symbol[];
    },
    enabled: !!user,
  });

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Please sign in to view your symbols</div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your symbols...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-red-600">Error loading symbols. Please try again.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Symbol Explorer
        </h1>
        <p className="text-gray-600">
          Discover patterns in your symbolic unconscious
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {symbols && symbols.length > 0 ? (
          symbols.map((symbol) => (
            <div 
              key={symbol.symbol} 
              className="bg-white rounded-lg p-6 shadow-sm border hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  {symbol.symbol}
                </h3>
                <span className="text-sm text-gray-500">
                  {symbol.frequency}x
                </span>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Emotional Charge:</span>
                  <span className={`font-medium ${
                    symbol.emotional_charge > 0.5 ? 'text-green-600' : 
                    symbol.emotional_charge < -0.5 ? 'text-red-600' : 
                    'text-gray-600'
                  }`}>
                    {symbol.emotional_charge.toFixed(2)}
                  </span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Recent Dreams:</span>
                  <span className="text-gray-500">
                    {symbol.recent_dreams.length}
                  </span>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t">
                <div className="flex flex-wrap gap-1">
                  {symbol.recent_dreams.slice(0, 3).map((dreamId) => (
                    <span 
                      key={dreamId}
                      className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
                    >
                      {dreamId.slice(-3)}
                    </span>
                  ))}
                  {symbol.recent_dreams.length > 3 && (
                    <span className="text-xs text-gray-500">
                      +{symbol.recent_dreams.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full text-center py-12">
            <p className="text-gray-600 mb-4">No symbols found yet</p>
            <p className="text-sm text-gray-500">
              Generate dreams to discover your symbolic patterns
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
