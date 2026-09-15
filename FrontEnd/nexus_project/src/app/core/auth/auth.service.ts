import { HttpClient } from '@angular/common/http';
import { Injectable, signal } from '@angular/core';
import { Observable, catchError, finalize, shareReplay, tap, throwError } from 'rxjs';
import { AuthenticatedUser, AuthResponse, LoginCredentials, Permission, RegistrationData, RoleAssignment, UserRole } from './auth.models';
import { environment } from '../../../environments/environment';

const AUTH_API = `${environment.apiUrl}/v1/auth`;

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly access = signal<string | null>(this.saved('nexus_access'));
  private readonly refresh = signal<string | null>(this.saved('nexus_refresh'));
  readonly user = signal<AuthenticatedUser | null>(this.savedUser());
  readonly sessionExpired = signal(false);
  private refreshRequest?: Observable<{ access: string; refresh?: string }>;

  constructor(private readonly http: HttpClient) {}

  login(credentials: LoginCredentials): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${AUTH_API}/login/`, credentials).pipe(
      tap(response => {
        this.setSession(response);
        this.sessionExpired.set(false);
      }),
    );
  }

  register(data: RegistrationData): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${environment.apiUrl}/auth/register/`, data).pipe(
      tap(response => {
        this.setSession(response);
        this.sessionExpired.set(false);
      }),
    );
  }

  logout(): Observable<unknown> {
    const refresh = this.refresh();
    if (!refresh) {
      this.clearSession();
      return new Observable(subscriber => { subscriber.next(null); subscriber.complete(); });
    }
    return this.http.post(`${AUTH_API}/logout/`, { refresh }).pipe(
      catchError(error => { this.clearSession(); return throwError(() => error); }),
      tap(() => this.clearSession()),
    );
  }

  refreshAccessToken(): Observable<{ access: string; refresh?: string }> {
    if (this.refreshRequest) return this.refreshRequest;
    const refresh = this.refresh();
    if (!refresh) return throwError(() => new Error('No refresh token'));
    this.refreshRequest = this.http.post<{ access: string; refresh?: string }>(`${AUTH_API}/token/refresh/`, { refresh }).pipe(
      tap(tokens => {
        this.access.set(tokens.access);
        this.store('nexus_access', tokens.access);
        if (tokens.refresh) {
          this.refresh.set(tokens.refresh);
          this.store('nexus_refresh', tokens.refresh);
        }
      }),
      shareReplay(1),
      finalize(() => this.refreshRequest = undefined),
    );
    return this.refreshRequest;
  }

  loadUsers(): Observable<AuthenticatedUser[]> { return this.http.get<AuthenticatedUser[]>(`${environment.apiUrl}/auth/users/`); }
  assignRole(userId: number, role: UserRole): Observable<AuthenticatedUser> {
    return this.http.patch<AuthenticatedUser>(`${environment.apiUrl}/auth/users/${userId}/role/`, { role } satisfies RoleAssignment);
  }
  hasPermission(permission: Permission): boolean { return this.user()?.permissions.includes(permission) ?? false; }
  accessToken(): string | null { return this.access(); }
  isAuthenticated(): boolean { return this.access() !== null; }

  handleSessionExpired(): void {
    const hadSession = this.isAuthenticated() || this.refresh() !== null;
    this.clearSession();
    if (hadSession) this.sessionExpired.set(true);
  }
  dismissSessionExpired(): void { this.sessionExpired.set(false); }
  clearSession(): void {
    this.access.set(null); this.refresh.set(null); this.user.set(null);
    try {
      if (typeof window !== 'undefined') ['nexus_access', 'nexus_refresh', 'nexus_user', 'nexus_token'].forEach(key => localStorage.removeItem(key));
    } catch {}
  }

  private setSession(response: AuthResponse): void {
    this.access.set(response.access); this.refresh.set(response.refresh); this.user.set(response.user);
    this.store('nexus_access', response.access); this.store('nexus_refresh', response.refresh);
    this.store('nexus_user', JSON.stringify(response.user));
  }
  private saved(key: string): string | null {
    try { return typeof window !== 'undefined' ? localStorage.getItem(key) : null; } catch { return null; }
  }
  private savedUser(): AuthenticatedUser | null {
    try { const raw = this.saved('nexus_user'); return raw ? JSON.parse(raw) : null; } catch { return null; }
  }
  private store(key: string, value: string): void {
    try { if (typeof window !== 'undefined') localStorage.setItem(key, value); } catch {}
  }
}
