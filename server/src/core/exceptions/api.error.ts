// server/src/core/exceptions/api.error.ts
/**
 * Base API error class with status code and metadata
 * @extends Error
 */
export class ApiError extends Error {
    constructor(
      public statusCode: number,
      public message: string,
      public metadata?: Record<string, unknown>
    ) {
      super(message)
      Error.captureStackTrace(this, this.constructor)
    }
  }
  
  /**
   * Specific error for market data failures
   */
  export class MarketDataError extends ApiError {
    constructor(message: string, public pair?: string) {
      super(503, `Market data error: ${message}`)
    }
  }

  export class TooManyRequestsError extends ApiError {
    constructor(public retryAfter: number) {
      super(429, 'RATE_LIMIT_EXCEEDED', `Retry after ${retryAfter} seconds.`);
    }
  
    toJSON() {
      return { ...super.toJSON(), retryAfter: this.retryAfter };
    }
  }