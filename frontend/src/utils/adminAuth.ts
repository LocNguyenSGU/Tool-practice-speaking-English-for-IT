import { isAuthenticated, getUser } from './auth';

/**
 * Check if the current user is an admin
 */
export const isAdmin = (): boolean => {
  const user = getUser();
  return user?.is_admin === true;
};

/**
 * Admin route guard - redirects to /lessons if user is not admin
 * Returns true if user is admin, false otherwise
 */
export const requireAdmin = (): boolean => {
  if (!isAuthenticated()) {
    window.location.href = '/auth';
    return false;
  }

  if (!isAdmin()) {
    window.location.href = '/lessons';
    return false;
  }

  return true;
};

/**
 * Check if current user has admin access without redirecting
 */
export const hasAdminAccess = (): boolean => {
  return isAuthenticated() && isAdmin();
};
