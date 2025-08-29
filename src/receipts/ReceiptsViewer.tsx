/**
 * Receipts Viewer - Wallet tab for browsing all user transaction events
 * Shows opportunity.rendered, purchase.attributed, payout.settled with human explanations and raw JSON
 */

import React, { useState, useEffect, useCallback } from 'react';
import { DateTime } from 'luxon';

export interface OpportunityRendered {
  receipt_id: string;
  user_id: string;
  opportunity_id: string;
  rendered_at: string;
  campaign: {
    id: string;
    name: string;
    merchant: string;
    category: string;
  };
  rendering: {
    format: 'push' | 'email' | 'sms' | 'banner';
    channel: string;
    content_hash: string;
    abas_decision: {
      decision: 'allow' | 'block' | 'defer';
      reason: string;
      rule_id?: string;
    };
  };
  attribution: {
    click_id?: string;
    impression_id?: string;
    referrer?: string;
    device_fingerprint: string;
  };
  context: {
    location?: string;
    device_type: string;
    user_agent: string;
    timestamp: string;
  };
}

export interface PurchaseAttributed {
  receipt_id: string;
  user_id: string;
  opportunity_id: string;
  purchase_id: string;
  attributed_at: string;
  purchase: {
    merchant: string;
    amount: number;
    currency: string;
    product_categories: string[];
    order_id: string;
  };
  attribution: {
    method: 'affiliate' | 's2s' | 'receipt' | 'behavioral' | 'last_touch' | 'default';
    confidence: number;
    attribution_window_hours: number;
    signals: {
      device_match: boolean;
      temporal_proximity: number;
      behavioral_signals: string[];
      fraud_score: number;
    };
  };
  commission: {
    rate: number;
    amount: number;
    currency: string;
    tier: string;
  };
}

export interface PayoutSettled {
  receipt_id: string;
  user_id: string;
  purchase_receipt_id: string;
  settled_at: string;
  payout: {
    amount: number;
    currency: string;
    method: 'wallet' | 'bank' | 'paypal' | 'crypto';
    destination: string;
    reference_id: string;
  };
  commission_split: {
    user_share: number;
    lukhas_share: number;
    escalation_applied: boolean;
    escalation_reason?: string;
  };
  settlement: {
    batch_id: string;
    processed_at: string;
    confirmed_at: string;
    status: 'pending' | 'confirmed' | 'failed';
    fees: {
      processing_fee: number;
      currency_conversion_fee: number;
      total_fees: number;
    };
  };
}

export type ReceiptType = 'opportunity' | 'purchase' | 'payout' | 'all';
export type Receipt = OpportunityRendered | PurchaseAttributed | PayoutSettled;

export interface ReceiptsViewerProps {
  user_id: string;
  api_base?: string;
  api_key?: string;
  default_filter?: ReceiptType;
  page_size?: number;
  show_raw_json?: boolean;
  className?: string;
}

const formatCurrency = (amount: number, currency: string): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency.toUpperCase(),
    minimumFractionDigits: 2
  }).format(amount);
};

const getReceiptTypeFromId = (receipt_id: string): ReceiptType => {
  if (receipt_id.startsWith('opp_')) return 'opportunity';
  if (receipt_id.startsWith('pur_')) return 'purchase';
  if (receipt_id.startsWith('pay_')) return 'payout';
  return 'all';
};

export const ReceiptsViewer: React.FC<ReceiptsViewerProps> = ({
  user_id,
  api_base = 'https://api.lukhas.ai',
  api_key,
  default_filter = 'all',
  page_size = 20,
  show_raw_json = false,
  className = ''
}) => {
  const [receipts, setReceipts] = useState<Receipt[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<ReceiptType>(default_filter);
  const [showJson, setShowJson] = useState(show_raw_json);
  const [selectedReceipt, setSelectedReceipt] = useState<Receipt | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const fetchReceipts = useCallback(async (reset = false) => {
    if (!user_id || (!api_key && typeof window !== 'undefined')) {
      setError('User ID and API key required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const currentPage = reset ? 1 : page;
      const params = new URLSearchParams({
        user_id,
        type: filter === 'all' ? '' : filter,
        page: currentPage.toString(),
        limit: page_size.toString()
      });

      const response = await fetch(`${api_base}/receipts?${params}`, {
        headers: {
          'Authorization': `Bearer ${api_key || 'demo_key'}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const newReceipts = data.receipts || [];

      if (reset) {
        setReceipts(newReceipts);
        setPage(2);
      } else {
        setReceipts(prev => [...prev, ...newReceipts]);
        setPage(prev => prev + 1);
      }

      setHasMore(newReceipts.length === page_size);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to fetch receipts';
      setError(errorMsg);
      console.error('Receipts fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [user_id, api_key, api_base, filter, page, page_size]);

  useEffect(() => {
    fetchReceipts(true);
  }, [filter, user_id, api_key]);

  const handleFilterChange = (newFilter: ReceiptType) => {
    setFilter(newFilter);
    setReceipts([]);
    setPage(1);
    setHasMore(true);
  };

  const downloadReceipt = (receipt: Receipt) => {
    const filename = `receipt_${receipt.receipt_id}.json`;
    const blob = new Blob([JSON.stringify(receipt, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getHumanExplanation = (receipt: Receipt): string => {
    const receiptType = getReceiptTypeFromId(receipt.receipt_id);
    
    switch (receiptType) {
      case 'opportunity':
        const opp = receipt as OpportunityRendered;
        const decision = opp.rendering.abas_decision;
        return `You were shown "${opp.campaign.name}" from ${opp.campaign.merchant} via ${opp.rendering.format}. ${decision.decision === 'allow' ? 'Delivered successfully' : `Blocked: ${decision.reason}`}.`;

      case 'purchase':
        const pur = receipt as PurchaseAttributed;
        const confidence = Math.round(pur.attribution.confidence * 100);
        return `Purchase of ${formatCurrency(pur.purchase.amount, pur.purchase.currency)} at ${pur.purchase.merchant} was attributed to LUKHAS with ${confidence}% confidence using ${pur.attribution.method} method. Commission: ${formatCurrency(pur.commission.amount, pur.commission.currency)}.`;

      case 'payout':
        const pay = receipt as PayoutSettled;
        const userShare = formatCurrency(pay.payout.amount - pay.settlement.fees.total_fees, pay.payout.currency);
        const escalation = pay.commission_split.escalation_applied ? ' (escalated rate applied)' : '';
        return `Payout of ${userShare} settled to your ${pay.payout.method} ending in ${pay.payout.destination.slice(-4)}${escalation}. ${pay.settlement.status === 'confirmed' ? 'Confirmed' : 'Processing'}.`;

      default:
        return 'Receipt details available in JSON view.';
    }
  };

  const getReceiptIcon = (receipt: Receipt): string => {
    const receiptType = getReceiptTypeFromId(receipt.receipt_id);
    switch (receiptType) {
      case 'opportunity': return '👁️';
      case 'purchase': return '🛒';
      case 'payout': return '💰';
      default: return '📄';
    }
  };

  const getReceiptTimestamp = (receipt: Receipt): string => {
    const receiptType = getReceiptTypeFromId(receipt.receipt_id);
    let timestamp: string;
    
    switch (receiptType) {
      case 'opportunity':
        timestamp = (receipt as OpportunityRendered).rendered_at;
        break;
      case 'purchase':
        timestamp = (receipt as PurchaseAttributed).attributed_at;
        break;
      case 'payout':
        timestamp = (receipt as PayoutSettled).settled_at;
        break;
      default:
        timestamp = new Date().toISOString();
    }
    
    return DateTime.fromISO(timestamp).toFormat('MMM dd, yyyy HH:mm');
  };

  if (error && receipts.length === 0) {
    return (
      <div className={`receipts-viewer-error p-6 text-center ${className}`}>
        <div className="text-red-600 dark:text-red-400 mb-4">
          <span className="text-2xl">⚠️</span>
          <p className="mt-2">Failed to load receipts</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
        <button
          onClick={() => fetchReceipts(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className={`receipts-viewer ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Transaction Receipts</h2>
        <div className="flex gap-2">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showJson}
              onChange={(e) => setShowJson(e.target.checked)}
              className="rounded"
            />
            Show JSON
          </label>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-1 mb-6 border-b">
        {(['all', 'opportunity', 'purchase', 'payout'] as ReceiptType[]).map((filterType) => (
          <button
            key={filterType}
            onClick={() => handleFilterChange(filterType)}
            className={`px-4 py-2 capitalize border-b-2 transition-colors ${
              filter === filterType
                ? 'border-blue-600 text-blue-600 font-medium'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            {filterType === 'all' ? 'All Receipts' : `${filterType} Events`}
            {filter === filterType && (
              <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                {receipts.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Receipts List */}
      <div className="space-y-4">
        {receipts.map((receipt) => (
          <div
            key={receipt.receipt_id}
            className="border rounded-lg p-4 bg-white dark:bg-gray-800 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-lg">{getReceiptIcon(receipt)}</span>
                  <div>
                    <span className="font-mono text-sm text-gray-500">
                      {receipt.receipt_id}
                    </span>
                    <div className="text-sm text-gray-500">
                      {getReceiptTimestamp(receipt)}
                    </div>
                  </div>
                </div>
                
                <p className="text-gray-900 dark:text-gray-100 mb-3">
                  {getHumanExplanation(receipt)}
                </p>

                {showJson && (
                  <details className="mt-3">
                    <summary className="cursor-pointer text-sm text-blue-600 hover:text-blue-800">
                      Raw JSON Data
                    </summary>
                    <pre className="mt-2 p-3 bg-gray-100 dark:bg-gray-700 rounded text-xs overflow-x-auto">
                      {JSON.stringify(receipt, null, 2)}
                    </pre>
                  </details>
                )}
              </div>

              <div className="flex gap-2 ml-4">
                <button
                  onClick={() => setSelectedReceipt(receipt)}
                  className="text-sm px-3 py-1 border rounded hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Details
                </button>
                <button
                  onClick={() => downloadReceipt(receipt)}
                  className="text-sm px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Download
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Load More */}
      {hasMore && receipts.length > 0 && (
        <div className="text-center mt-6">
          <button
            onClick={() => fetchReceipts()}
            disabled={loading}
            className="bg-gray-200 dark:bg-gray-700 px-6 py-2 rounded hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Load More'}
          </button>
        </div>
      )}

      {/* Empty State */}
      {receipts.length === 0 && !loading && !error && (
        <div className="text-center py-12 text-gray-500">
          <span className="text-4xl mb-4 block">📄</span>
          <p>No receipts found</p>
          <p className="text-sm mt-2">
            {filter === 'all' 
              ? 'Your transaction history will appear here'
              : `No ${filter} events found`
            }
          </p>
        </div>
      )}

      {/* Loading State */}
      {loading && receipts.length === 0 && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-500">Loading receipts...</p>
        </div>
      )}

      {/* Receipt Detail Modal */}
      {selectedReceipt && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Receipt Details</h3>
              <button
                onClick={() => setSelectedReceipt(null)}
                className="text-gray-500 hover:text-gray-700 text-xl"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-gray-100">
                  Human Explanation
                </h4>
                <p className="mt-1 text-gray-700 dark:text-gray-300">
                  {getHumanExplanation(selectedReceipt)}
                </p>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                  Raw JSON Data
                </h4>
                <pre className="bg-gray-100 dark:bg-gray-700 p-3 rounded text-xs overflow-x-auto">
                  {JSON.stringify(selectedReceipt, null, 2)}
                </pre>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => downloadReceipt(selectedReceipt)}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Download JSON
              </button>
              <button
                onClick={() => setSelectedReceipt(null)}
                className="flex-1 border border-gray-300 dark:border-gray-600 px-4 py-2 rounded hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Usage Examples:
 * 
 * // Basic receipts viewer
 * <ReceiptsViewer user_id="user_123" />
 * 
 * // With specific filter and API config
 * <ReceiptsViewer 
 *   user_id="user_456"
 *   api_base="https://api.lukhas.ai"
 *   api_key={userApiKey}
 *   default_filter="purchase"
 *   show_raw_json={true}
 * />
 * 
 * // In wallet dashboard
 * <div className="wallet-tabs">
 *   <ReceiptsViewer 
 *     user_id={user.id}
 *     className="receipts-tab"
 *     page_size={10}
 *   />
 * </div>
 */

export default ReceiptsViewer;