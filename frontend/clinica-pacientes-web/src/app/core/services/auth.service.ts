import { HttpClient } from '@angular/common/http';
import {
  Injectable,
  PLATFORM_ID,
  inject,
} from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

import {
  BehaviorSubject,
  Observable,
  tap,
} from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  CurrentUserResponse,
  LoginRequest,
  LoginResponse,
  User,
} from '../../models/user.model';


const TOKEN_STORAGE_KEY = 'access_token';
const USER_STORAGE_KEY = 'current_user';


@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly http = inject(HttpClient);

  private readonly platformId = inject(
    PLATFORM_ID,
  );

  private readonly apiUrl =
    `${environment.apiUrl}/auth`;

  private readonly currentUserSubject =
    new BehaviorSubject<User | null>(
      this.readStoredUser(),
    );

  readonly currentUser$ =
    this.currentUserSubject.asObservable();


  login(
    credentials: LoginRequest,
  ): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(
        `${this.apiUrl}/login`,
        credentials,
      )
      .pipe(
        tap((response) => {
          this.saveSession(
            response.access_token,
            response.user,
          );
        }),
      );
  }


  getCurrentUser(): Observable<CurrentUserResponse> {
    return this.http
      .get<CurrentUserResponse>(
        `${this.apiUrl}/me`,
      )
      .pipe(
        tap((response) => {
          this.storeUser(response.user);

          this.currentUserSubject.next(
            response.user,
          );
        }),
      );
  }


  logout(): void {
    if (this.isBrowser()) {
      sessionStorage.removeItem(
        TOKEN_STORAGE_KEY,
      );

      sessionStorage.removeItem(
        USER_STORAGE_KEY,
      );
    }

    this.currentUserSubject.next(null);
  }


  isAuthenticated(): boolean {
    return Boolean(this.getToken());
  }


  getToken(): string | null {
    if (!this.isBrowser()) {
      return null;
    }

    return sessionStorage.getItem(
      TOKEN_STORAGE_KEY,
    );
  }


  getCurrentUserSnapshot(): User | null {
    return this.currentUserSubject.value;
  }


  hasRole(role: User['rol']): boolean {
    return (
      this.currentUserSubject.value?.rol === role
    );
  }


  private saveSession(
    token: string,
    user: User,
  ): void {
    if (!this.isBrowser()) {
      return;
    }

    sessionStorage.setItem(
      TOKEN_STORAGE_KEY,
      token,
    );

    this.storeUser(user);

    this.currentUserSubject.next(user);
  }


  private storeUser(user: User): void {
    if (!this.isBrowser()) {
      return;
    }

    sessionStorage.setItem(
      USER_STORAGE_KEY,
      JSON.stringify(user),
    );
  }


  private readStoredUser(): User | null {
    if (!this.isBrowser()) {
      return null;
    }

    const storedUser = sessionStorage.getItem(
      USER_STORAGE_KEY,
    );

    if (!storedUser) {
      return null;
    }

    try {
      return JSON.parse(storedUser) as User;
    } catch {
      sessionStorage.removeItem(
        USER_STORAGE_KEY,
      );

      return null;
    }
  }


  private isBrowser(): boolean {
    return isPlatformBrowser(
      this.platformId,
    );
  }
}