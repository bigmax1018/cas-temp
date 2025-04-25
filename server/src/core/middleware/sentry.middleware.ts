// server/src/core/middleware/sentry.middleware.ts
/**
 * Captures errors and transactions in Sentry with OTEL context
 */
import { Request, Response, NextFunction } from 'express';
import * as Sentry from '@sentry/node';
import { trace } from '@opentelemetry/api';

export function sentryErrorHandler() {
  return (err: Error, req: Request, _res: Response, next: NextFunction) => {
    const transaction = Sentry.getCurrentHub()?.getScope()?.getTransaction();
    
    // Capture exceptions with context
    Sentry.withScope(scope => {
      scope.setContext('request', {
        method: req.method,
        url: req.url,
        headers: req.headers
      });
      
      if (transaction) {
        scope.setSpan(transaction);
      }
      
      Sentry.captureException(err);
    });

    // Ensure the error is passed to OpenTelemetry
    const activeSpan = trace.getActiveSpan();
    if (activeSpan) {
      activeSpan.recordException(err);
      activeSpan.setStatus({ code: trace.StatusCode.ERROR });
    }

    next(err);
  };
}