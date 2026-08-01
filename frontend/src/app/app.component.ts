import { Routes } from '@angular/router';
import { MainLayout } from './layout/main-layout/main-layout';
// Importa tus componentes reales o el Placeholder
import { Search } from './features/search/pages/search';
import { PlaceholderComponent } from './shared/components/placeholder/placeholder.component'; 

export const routes: Routes = [
  {
    path: '',
    component: MainLayout,
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', loadComponent: () => import('./features/dashboard/pages/dashboard').then(m => m.Dashboard) }, // Asegúrate de crear este o usar Placeholder
      { path: 'buscar-procesos', component: Search },
      { path: 'seguimiento', component: PlaceholderComponent }, // Temporal
      { path: 'ia', component: PlaceholderComponent }, // Temporal
      { path: 'configuracion', component: PlaceholderComponent }, // Temporal
    ],
  },
];