// server/src/domains/users/user.service.ts
import { postgres } from '../../infrastructure/database/postgres.client'
import { ApiError } from '../../core/exceptions/api.error'

/**
 * User domain service with business logic
 */
export class UserService {
  /**
   * Get user by ID with error handling
   */
  async getUserById(id: string) {
    try {
      const [user] = await postgres.query(
        'SELECT * FROM users WHERE id = $1 LIMIT 1',
        [id]
      )
      
      if (!user) {
        throw new ApiError(404, 'User not found')
      }

      return this.sanitizeUser(user)
    } catch (error) {
      if (error instanceof ApiError) throw error
      throw new ApiError(500, 'Failed to fetch user')
    }
  }

  private sanitizeUser(user: any) {
    const { password, ...sanitized } = user
    return sanitized
  }
}