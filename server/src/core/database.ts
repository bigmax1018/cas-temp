// src/core/database.ts
import { Pool } from 'pg'; // PostgreSQL client

export const db = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Basic query helper
export const query = async (text: string, params?: any[]) => {
  const start = Date.now();
  const res = await db.query(text, params);
  const duration = Date.now() - start;
  console.log(`Executed query in ${duration}ms`, { text });
  return res;
};