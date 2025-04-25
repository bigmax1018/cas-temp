import { Request, Response, NextFunction } from 'express';
import redis from '../infrastructure/cache/redis.client';
import { TooManyRequestsError } from '../exceptions';

type WindowConfig = {
  windowMs: number;    // e.g., 60000ms = 1 minute
  maxRequests: number; // e.g., 100 requests per window
};

const DEFAULT_LIMIT = { windowMs: 60_000, maxRequests: 100 };

export function rateLimiter(config: Partial<WindowConfig> = {}) {
  const { windowMs, maxRequests } = { ...DEFAULT_LIMIT, ...config };

  return async (req: Request, res: Response, next: NextFunction) => {
    const clientId = req.ip || 'unknown';
    const redisKey = `rate_limit:${clientId}:${req.originalUrl}`;

    try {
      const now = Date.now();
      const [, count] = await redis
        .multi()
        .zremrangebyscore(redisKey, 0, now - windowMs) // Clear old entries
        .zcard(redisKey)                              // Count remaining
        .zadd(redisKey, now, now)                    // Add current request
        .expire(redisKey, Math.ceil(windowMs / 1000)) // Reset TTL
        .exec();

      if (count >= maxRequests) {
        const oldestReq = await redis.zrange(redisKey, 0, 0);
        const retryAfter = Math.ceil((Number(oldestReq[0]) + windowMs - now) / 1000);
        throw new TooManyRequestsError(retryAfter);
      }

      // Set rate limit headers
      res.set({
        'X-RateLimit-Limit': maxRequests.toString(),
        'X-RateLimit-Remaining': (maxRequests - count - 1).toString(),
        'X-RateLimit-Reset': Math.ceil((now + windowMs) / 1000).toString()
      });

      next();
    } catch (err) {
      req.logger?.warn(`Rate limit exceeded for ${clientId}`);
      next(err);
    }
  };
}