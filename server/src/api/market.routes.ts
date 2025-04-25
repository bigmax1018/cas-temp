// server/src/api/market.routes.ts
import { Router } from 'express'
import { marketController } from '../domains/market-data/market.controller'
import { validate } from '../core/middleware/validation.middleware'
import { marketSchema } from '../domains/market-data/market.schema'

const router = Router()

/**
 * Market data API routes
 */
router.get('/networks', marketController.getNetworks)
router.get('/tokens/:network', marketController.getTokensByNetwork)
router.get('/pairs/:network', marketController.getTokenPairs)
router.get('/history/:pair', 
  validate(marketSchema.historyQuery),
  marketController.getPriceHistory
)
router.get('/predictions/:pair', 
  validate(marketSchema.predictionQuery),
  marketController.getPredictions
)

export { router as marketRoutes }