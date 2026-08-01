import { Routes } from '@angular/router';
import { MainLayout } from './layout/main-layout/main-layout';
import { Search } from './features/search/pages/search';
// Importa el componente Placeholder para las nuevas rutas
import { PlaceholderComponent } from './shared/components/placeholder/placeholder.component'; 

export const routes: Routes = [
  {
    path: '',
    component: MainLayout,
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: PlaceholderComponent, data: { title: 'Dashboard', message: 'Resumen general del sistema.' } },
      { path: 'buscar-procesos', component: Search },
      { path: 'seguimiento', component: PlaceholderComponent, data: { title: 'Seguimiento', message: 'Módulo de seguimiento de contratos.' } },
      { path: 'ia', component: PlaceholderComponent, data: { title: 'Inteligencia Artificial', message: 'Análisis predictivo con IA.' } },
      { path: 'configuracion', component: PlaceholderComponent, data: { title: 'Configuración', message: 'Ajustes del sistema.' } },
      { path: 'ayuda', component: PlaceholderComponent, data: { title: 'Centro de Ayuda', message: 'Documentación y soporte.' } },
    ],
  },
];