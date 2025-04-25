import { MarketData } from '../../domains/market-data/market.schema';
import { DatabaseError } from '../exceptions/database.error';
import { prisma } from './prisma.service';
import { PrismaMarketData, toMarketData } from './prisma.types';

export class DatabaseModule {
  async getMarketData(pair: string): Promise<MarketData | null> {
    try {
      const data = await prisma.marketData.findFirst({
        where: { pair },
        orderBy: { timestamp: 'desc' },
        select: {
          id: true,
          pair: true,
          price: true,
          volume: true,
          timestamp: true,
          exchange: true
        }
      });
      return data ? toMarketData(data) : null;
    } catch (error) {
      throw new DatabaseError('Failed to query market data', {
        code: 'MARKET_DATA_QUERY_FAILED',
        cause: error instanceof Error ? error : undefined
      });
    }
  }

  async insertMarketData(data: MarketData): Promise<void> {
    try {
      await prisma.marketData.create({
        data: {
          pair: data.pair,
          price: data.price,
          volume: data.volume ?? null, // Convert undefined to null
          exchange: data.exchange ?? null,
          timestamp: data.timestamp || new Date()
        }
      });
    } catch (error) {
      throw new DatabaseError('Failed to insert market data', {
        code: 'MARKET_DATA_INSERT_FAILED',
        cause: error instanceof Error ? error : undefined
      });
    }
  }
}