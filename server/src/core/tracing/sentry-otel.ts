// server/src/core/tracing/sentry-otel.ts
/**
 * Configures Sentry and OpenTelemetry with:
 * - Error tracking
 * - Performance monitoring
 * - Distributed trace propagation
 */
import * as Sentry from '@sentry/node';
import { NodeSDK } from '@opentelemetry/sdk-node';
import { SentrySpanProcessor, SentryPropagator } from '@sentry/opentelemetry-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';

export function initMonitoring() {
  // Initialize Sentry
  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    environment: process.env.NODE_ENV,
    tracesSampleRate: 1.0, // Capture 100% of transactions
    integrations: [new Sentry.Integrations.Http({ tracing: true })]
  });

  // Configure OpenTelemetry with Sentry
  const sdk = new NodeSDK({
    resource: new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: 'cas-server'
    }),
    spanProcessors: [new SentrySpanProcessor()],
    instrumentations: [getNodeAutoInstrumentations()],
    textMapPropagator: new SentryPropagator()
  });

  sdk.start();

  return {
    shutdown: async () => {
      await Sentry.close(2000);
      await sdk.shutdown();
    }
  };
}

// Custom Instrumentation:
// typescript
// // Track specific functions
// const transaction = Sentry.startTransaction({ name: 'processOrder' });
// try {
//   await processOrder();
//   transaction.finish();
// } catch (err) {
//   transaction.finish();
//   throw err;
// }
// Sampling Control:
// typescript
// Sentry.init({
//   tracesSampler: samplingContext => {
//     if (samplingContext.request?.url?.includes('/health')) {
//       return 0.1; // Sample 10% of health checks
//     }
//     return 1.0;
//   }
// });