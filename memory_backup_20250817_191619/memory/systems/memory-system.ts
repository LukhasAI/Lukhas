/**
 * Public interface for Lukhas AGI memory system.
 * Jobs: Beautiful simplicity for end users.
 * Altman: Safety and security by default.
 */

export interface LucasMemory {
  /**
   * Store a memory with automatic dream processing.
   * It just works - handles all complexity internally.
   */
  store(content: any, context?: string): Promise<{
    success: boolean;
    memory_id?: string;
    error?: string;
  }>;

  /**
   * Retrieve a memory with automatic access control.
   * Simple retrieval that handles security transparently.
   */
  retrieve(memory_id: string): Promise<{
    success: boolean;
    memory?: any;
    error?: string;
  }>;

  /**
   * Process a dream and enhance related memories.
   * Automatic enhancement that maintains safety.
   */
  dream(content: any): Promise<{
    success: boolean;
    dream_id?: string;
    insights?: any[];
    error?: string;
  }>;

  /**
   * Request elevated access with automatic quorum handling.
   * Simple elevation that ensures security.
   */
  requestAccess(justification: string): Promise<{
    success: boolean;
    elevation_id?: string;
    error?: string;
  }>;
}
