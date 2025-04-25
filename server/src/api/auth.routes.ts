// server/src/api/auth.routes.ts
import { Router } from 'express'
import { authController } from '../domains/users/user.controller'
import { validate } from '../core/middleware/validation.middleware'
import { userSchema } from '../domains/users/user.schema'

const router = Router()

/**
 * Authentication API routes
 */
router.post('/register', 
  validate(userSchema.register),
  authController.register
)
router.post('/login', 
  validate(userSchema.login),
  authController.login
)
router.post('/logout', 
  authController.logout
)
router.post('/forgot-password', 
  validate(userSchema.forgotPassword),
  authController.forgotPassword
)
router.post('/reset-password', 
  validate(userSchema.resetPassword),
  authController.resetPassword
)

export { router as authRoutes }