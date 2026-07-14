import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';
import { publicGuard } from './core/guards/public.guard';

export const routes: Routes = [

  // ===========================
  // Rutas públicas
  // ===========================

  {
    path: 'login',
    title: 'Iniciar sesión',
    canActivate: [publicGuard],
    loadComponent: () =>
      import(
        './features/auth/login/login.component'
      ).then(
        (module) => module.LoginComponent,
      ),
  },

  // ===========================
  // Rutas protegidas
  // ===========================

  {
    path: '',
    canActivate: [authGuard],

    loadComponent: () =>
      import(
        './layout/main-layout/main-layout.component'
      ).then(
        (module) => module.MainLayoutComponent,
      ),

    children: [

      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'dashboard',
      },

      {
        path: 'dashboard',
        title: 'Dashboard',
        loadComponent: () =>
          import(
            './features/dashboard/dashboard.component'
          ).then(
            (module) => module.DashboardComponent,
          ),
      },

      {
        path: 'patients',
        title: 'Pacientes',
        loadComponent: () =>
          import(
            './features/patients/patient-list/patient-list.component'
          ).then(
            (module) => module.PatientListComponent,
          ),
      },

      {
        path: 'patients/new',
        title: 'Nuevo paciente',
        loadComponent: () =>
          import(
            './features/patients/patient-form/patient-form.component'
          ).then(
            (module) => module.PatientFormComponent,
          ),
      },

      {
        path: 'patients/:id/edit',
        title: 'Editar paciente',
        loadComponent: () =>
          import(
            './features/patients/patient-form/patient-form.component'
          ).then(
            (module) => module.PatientFormComponent,
          ),
      },

    ],
  },

  // ===========================
  // Ruta no encontrada
  // ===========================

  {
    path: '**',
    redirectTo: 'dashboard',
  },

];