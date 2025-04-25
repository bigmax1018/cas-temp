// server/src/core/database/prisma.service.ts
import { PrismaClient } from '@prisma/client';

class PrismaService extends PrismaClient {
  constructor() {
    super();
    this.$connect();
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }
}

export const prisma = new PrismaService();