import { Routes } from '@angular/router';

import { MainLayout } from './layout/main-layout/main-layout';
import { Search } from './features/process-search/pages/search/search';
import { ROUTES } from './core/constants/routes';

export const routes: Routes = [
  {
    path: ROUTES.HOME,
    component: MainLayout,
    children: [
      {
        path: ROUTES.HOME,
        redirectTo: ROUTES.SEARCH,
        pathMatch: 'full',
      },
      {
        path: ROUTES.SEARCH,
        component: Search,
      },
    ],
  },
];