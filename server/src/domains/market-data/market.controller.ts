// server/src/domains/market-data/market.controller.ts
/**
 * Market API controller
 * Handles HTTP requests for market data
 * Input validation and response formatting
 */

import { Controller, Get, Query, Param } from '@nestjs/common';
import { MarketService } from './market.service';
import { ApiTags, ApiResponse, ApiQuery } from '@nestjs/swagger';

@Controller('market')
@ApiTags('market')
export class MarketController {
  constructor(private readonly marketService: MarketService) {}

  @Get('networks')
  @ApiResponse({ status: 200, description: 'List of available networks' })
  async getNetworks() {
    return this.marketService.getActiveNetworks();
  }

  @Get('pairs')
  @ApiQuery({ name: 'network', required: true })
  @ApiResponse({ status: 200, description: 'Token pairs for specified network' })
  async getTokenPairs(@Query('network') networkId: string) {
    return this.marketService.getTokenPairs(networkId);
  }

  @Get('history/:pairId')
  @ApiQuery({ name: 'timeframe', required: true })
  @ApiResponse({ status: 200, description: 'Price history for token pair' })
  async getPriceHistory(
    @Param('pairId') pairId: string,
    @Query('timeframe') timeframe: string
  ) {
    return this.marketService.getPriceHistory(pairId, timeframe);
  }
}