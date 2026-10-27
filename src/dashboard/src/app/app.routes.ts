import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./features/monitoring/monitoring.component').then(
        (m) => m.MonitoringComponent
      ),
  },
  {
    path: '**',
    redirectTo: '',
  },
];
