import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { AsyncPipe, CommonModule } from '@angular/common';
import { Component, DestroyRef, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTooltipModule } from '@angular/material/tooltip';

import {
  Router,
  RouterLink,
  RouterLinkActive,
  RouterOutlet,
} from '@angular/router';

import { map, shareReplay } from 'rxjs';

import { AuthService } from '../../core/services/auth.service';


@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [
    CommonModule,
    AsyncPipe,
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatDividerModule,
    MatTooltipModule,
  ],
  templateUrl: './main-layout.component.html',
  styleUrl: './main-layout.component.scss',
})

export class MainLayoutComponent {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly breakpointObserver = inject(BreakpointObserver);
  private readonly destroyRef = inject(DestroyRef);

  readonly currentUser$ = this.authService.currentUser$;

  readonly isMobile$ = this.breakpointObserver
    .observe([
      Breakpoints.Handset,
      Breakpoints.TabletPortrait,
    ])
    .pipe(
      map((result) => result.matches),
      shareReplay({
        bufferSize: 1,
        refCount: true,
      }),
    );

  sidebarOpened = true;
  isMobile = false;

  constructor() {
    this.isMobile$
      .pipe(
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe((isMobile) => {
        this.isMobile = isMobile;
        this.sidebarOpened = !isMobile;
      });
  }

  toggleSidebar(): void {
    this.sidebarOpened = !this.sidebarOpened;
  }

  closeSidebarOnMobile(): void {
    if (this.isMobile) {
      this.sidebarOpened = false;
    }
  }

  logout(): void {
    this.authService.logout();
    void this.router.navigate(['/login']);
  }

  getInitials(name: string | undefined): string {
    if (!name) {
      return 'U';
    }

    return name
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part.charAt(0).toUpperCase())
      .join('');
  }
}