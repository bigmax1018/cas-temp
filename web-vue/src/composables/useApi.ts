// web-vue/src/composables/useApi.ts
/**
 * Axios interceptor for trace propagation
 */
import { trace } from '@opentelemetry/api';
import { serializeSpanContext } from '@sentry/opentelemetry-node';

export function useApi() {
  const api = axios.create();

  api.interceptors.request.use(config => {
    const span = trace.getActiveSpan();
    if (span) {
      const spanContext = serializeSpanContext(span.spanContext());
      config.headers['sentry-trace'] = spanContext;
    }
    return config;
  });

  return api;
}