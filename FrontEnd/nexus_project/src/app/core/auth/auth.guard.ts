import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';
import { Permission, UserRole } from './auth.models';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return auth.isAuthenticated() || inject(Router).createUrlTree(['/login']);
};

export const permissionGuard: CanActivateFn = (route) => {
  const auth = inject(AuthService);
  const requiredPermission = route.data['requiredPermission'] as Permission | undefined;
  return auth.isAuthenticated() && (!requiredPermission || auth.hasPermission(requiredPermission))
    ? true
    : inject(Router).createUrlTree(['/home']);
};

export const roleGuard: CanActivateFn = (route) => {
  const auth = inject(AuthService);
  const allowedRoles = route.data['allowedRoles'] as UserRole[] | undefined;
  const user = auth.user();
  if (!auth.isAuthenticated() || !user) {
    return inject(Router).createUrlTree(['/login']);
  }
  if (!allowedRoles || allowedRoles.includes(user.role)) {
    return true;
  }
  return inject(Router).createUrlTree(['/home']);
};
