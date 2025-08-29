/**
 * Receipts API - Backend service for transaction receipt retrieval
 * Provides secure access to opportunity, purchase, and payout events
 */

import { Request, Response } from 'express';
import { DateTime } from 'luxon';

export interface ReceiptsQuery {
  user_id: string;
  type?: 'opportunity' | 'purchase' | 'payout' | 'all';
  page?: number;
  limit?: number;
  start_date?: string;
  end_date?: string;
  receipt_id?: string;
}

export interface ReceiptsResponse {
  receipts: any[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    has_more: boolean;
  };
  summary: {
    total_opportunities: number;
    total_purchases: number;
    total_payouts: number;
    total_earnings: number;
    currency: string;
  };
}

export class ReceiptsAPI {
  private db: any; // Database connection
  private auditLogger: any; // Audit logger

  constructor(database: any, auditLogger: any) {
    this.db = database;
    this.auditLogger = auditLogger;
  }

  /**
   * Get receipts for a user with filtering and pagination
   */
  async getReceipts(req: Request, res: Response): Promise<void> {
    try {
      const query: ReceiptsQuery = {
        user_id: req.query.user_id as string,
        type: (req.query.type as any) || 'all',
        page: parseInt(req.query.page as string) || 1,
        limit: Math.min(parseInt(req.query.limit as string) || 20, 100),
        start_date: req.query.start_date as string,
        end_date: req.query.end_date as string,
        receipt_id: req.query.receipt_id as string
      };

      // Validate user authorization
      const requestingUserId = req.headers['x-user-id'] as string;
      if (!requestingUserId || requestingUserId !== query.user_id) {
        res.status(403).json({
          error: 'forbidden',
          message: 'Cannot access receipts for other users'
        });
        return;
      }

      // Build query conditions
      const conditions: any = { user_id: query.user_id };
      
      if (query.type && query.type !== 'all') {
        conditions.receipt_type = query.type;
      }
      
      if (query.start_date) {
        conditions.created_at = { ...conditions.created_at, $gte: new Date(query.start_date) };
      }
      
      if (query.end_date) {
        conditions.created_at = { ...conditions.created_at, $lte: new Date(query.end_date) };
      }
      
      if (query.receipt_id) {
        conditions.receipt_id = query.receipt_id;
      }

      // Execute queries in parallel
      const offset = (query.page - 1) * query.limit;
      const [receipts, totalCount, summary] = await Promise.all([
        this.db.collection('receipts').find(conditions)
          .sort({ created_at: -1 })
          .skip(offset)
          .limit(query.limit)
          .toArray(),
        this.db.collection('receipts').countDocuments(conditions),
        this.getUserSummary(query.user_id)
      ]);

      // Format response
      const response: ReceiptsResponse = {
        receipts: receipts.map(this.formatReceiptForClient),
        pagination: {
          page: query.page,
          limit: query.limit,
          total: totalCount,
          has_more: offset + receipts.length < totalCount
        },
        summary
      };

      // Log access for audit
      await this.auditLogger.log({
        action: 'receipts_accessed',
        user_id: query.user_id,
        metadata: {
          type: query.type,
          count: receipts.length,
          page: query.page
        },
        timestamp: new Date().toISOString()
      });

      res.json(response);

    } catch (error) {
      console.error('Receipts API error:', error);
      res.status(500).json({
        error: 'internal_server_error',
        message: 'Failed to retrieve receipts'
      });
    }
  }

  /**
   * Get a single receipt by ID
   */
  async getReceiptById(req: Request, res: Response): Promise<void> {
    try {
      const receiptId = req.params.receipt_id;
      const requestingUserId = req.headers['x-user-id'] as string;

      const receipt = await this.db.collection('receipts').findOne({
        receipt_id: receiptId,
        user_id: requestingUserId
      });

      if (!receipt) {
        res.status(404).json({
          error: 'receipt_not_found',
          message: 'Receipt not found or access denied'
        });
        return;
      }

      // Log access
      await this.auditLogger.log({
        action: 'receipt_accessed',
        user_id: requestingUserId,
        metadata: {
          receipt_id: receiptId,
          receipt_type: receipt.receipt_type
        },
        timestamp: new Date().toISOString()
      });

      res.json({
        receipt: this.formatReceiptForClient(receipt)
      });

    } catch (error) {
      console.error('Receipt retrieval error:', error);
      res.status(500).json({
        error: 'internal_server_error',
        message: 'Failed to retrieve receipt'
      });
    }
  }

  /**
   * Export receipts as downloadable file
   */
  async exportReceipts(req: Request, res: Response): Promise<void> {
    try {
      const query: ReceiptsQuery = {
        user_id: req.query.user_id as string,
        type: (req.query.type as any) || 'all',
        start_date: req.query.start_date as string,
        end_date: req.query.end_date as string
      };

      const requestingUserId = req.headers['x-user-id'] as string;
      if (!requestingUserId || requestingUserId !== query.user_id) {
        res.status(403).json({
          error: 'forbidden',
          message: 'Cannot export receipts for other users'
        });
        return;
      }

      // Build conditions (no pagination for export)
      const conditions: any = { user_id: query.user_id };
      
      if (query.type && query.type !== 'all') {
        conditions.receipt_type = query.type;
      }
      
      if (query.start_date || query.end_date) {
        conditions.created_at = {};
        if (query.start_date) {
          conditions.created_at.$gte = new Date(query.start_date);
        }
        if (query.end_date) {
          conditions.created_at.$lte = new Date(query.end_date);
        }
      }

      // Get all matching receipts
      const receipts = await this.db.collection('receipts')
        .find(conditions)
        .sort({ created_at: -1 })
        .toArray();

      const format = req.query.format as string || 'json';
      const filename = `receipts_${query.user_id}_${DateTime.now().toFormat('yyyy-MM-dd')}.${format}`;

      if (format === 'csv') {
        const csv = this.convertToCSV(receipts);
        res.setHeader('Content-Type', 'text/csv');
        res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
        res.send(csv);
      } else {
        const json = JSON.stringify({
          export_metadata: {
            user_id: query.user_id,
            exported_at: new Date().toISOString(),
            total_receipts: receipts.length,
            date_range: {
              start: query.start_date,
              end: query.end_date
            }
          },
          receipts: receipts.map(this.formatReceiptForClient)
        }, null, 2);

        res.setHeader('Content-Type', 'application/json');
        res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
        res.send(json);
      }

      // Log export
      await this.auditLogger.log({
        action: 'receipts_exported',
        user_id: query.user_id,
        metadata: {
          format,
          count: receipts.length,
          type: query.type
        },
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      console.error('Receipt export error:', error);
      res.status(500).json({
        error: 'export_failed',
        message: 'Failed to export receipts'
      });
    }
  }

  /**
   * Store a new receipt (internal use)
   */
  async storeReceipt(receiptData: any): Promise<string> {
    try {
      const receipt = {
        ...receiptData,
        created_at: new Date(),
        updated_at: new Date()
      };

      const result = await this.db.collection('receipts').insertOne(receipt);
      
      // Log creation
      await this.auditLogger.log({
        action: 'receipt_created',
        user_id: receipt.user_id,
        metadata: {
          receipt_id: receipt.receipt_id,
          receipt_type: receipt.receipt_type
        },
        timestamp: new Date().toISOString()
      });

      return result.insertedId;

    } catch (error) {
      console.error('Receipt storage error:', error);
      throw new Error('Failed to store receipt');
    }
  }

  /**
   * Get user summary statistics
   */
  private async getUserSummary(userId: string): Promise<any> {
    try {
      const pipeline = [
        { $match: { user_id: userId } },
        {
          $group: {
            _id: '$receipt_type',
            count: { $sum: 1 },
            total_amount: {
              $sum: {
                $cond: [
                  { $eq: ['$receipt_type', 'payout'] },
                  '$payout.amount',
                  0
                ]
              }
            }
          }
        }
      ];

      const results = await this.db.collection('receipts').aggregate(pipeline).toArray();
      
      const summary = {
        total_opportunities: 0,
        total_purchases: 0,
        total_payouts: 0,
        total_earnings: 0,
        currency: 'USD'
      };

      results.forEach(result => {
        switch (result._id) {
          case 'opportunity':
            summary.total_opportunities = result.count;
            break;
          case 'purchase':
            summary.total_purchases = result.count;
            break;
          case 'payout':
            summary.total_payouts = result.count;
            summary.total_earnings = result.total_amount;
            break;
        }
      });

      return summary;

    } catch (error) {
      console.error('Summary generation error:', error);
      return {
        total_opportunities: 0,
        total_purchases: 0,
        total_payouts: 0,
        total_earnings: 0,
        currency: 'USD'
      };
    }
  }

  /**
   * Format receipt for client response (remove sensitive fields)
   */
  private formatReceiptForClient(receipt: any): any {
    const { _id, internal_notes, fraud_flags, ...clientReceipt } = receipt;
    return clientReceipt;
  }

  /**
   * Convert receipts to CSV format
   */
  private convertToCSV(receipts: any[]): string {
    if (receipts.length === 0) {
      return 'No receipts found\n';
    }

    // Define common CSV headers
    const headers = [
      'Receipt ID',
      'Type',
      'Date',
      'Amount',
      'Currency',
      'Status',
      'Description'
    ];

    const rows = receipts.map(receipt => {
      let amount = '';
      let description = '';
      let status = '';

      switch (receipt.receipt_type) {
        case 'opportunity':
          description = `${receipt.campaign?.name || 'N/A'} - ${receipt.campaign?.merchant || 'N/A'}`;
          status = receipt.rendering?.abas_decision?.decision || 'unknown';
          break;
        case 'purchase':
          amount = receipt.purchase?.amount || '';
          description = `Purchase at ${receipt.purchase?.merchant || 'N/A'}`;
          status = 'attributed';
          break;
        case 'payout':
          amount = receipt.payout?.amount || '';
          description = `Payout to ${receipt.payout?.method || 'N/A'}`;
          status = receipt.settlement?.status || 'unknown';
          break;
      }

      return [
        receipt.receipt_id,
        receipt.receipt_type,
        receipt.created_at,
        amount,
        receipt.currency || receipt.purchase?.currency || receipt.payout?.currency || '',
        status,
        description
      ];
    });

    return [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');
  }
}

/**
 * Express router setup example:
 * 
 * import { Router } from 'express';
 * import { ReceiptsAPI } from './receipts/api';
 * 
 * const router = Router();
 * const receiptsAPI = new ReceiptsAPI(db, auditLogger);
 * 
 * router.get('/receipts', receiptsAPI.getReceipts.bind(receiptsAPI));
 * router.get('/receipts/:receipt_id', receiptsAPI.getReceiptById.bind(receiptsAPI));
 * router.get('/receipts/export', receiptsAPI.exportReceipts.bind(receiptsAPI));
 * 
 * export default router;
 */

export default ReceiptsAPI;