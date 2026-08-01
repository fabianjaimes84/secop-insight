import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router'; // 1. Importar RouterOutlet
import { SidebarComponent } from '../sidebar/sidebar.component';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, SidebarComponent], // 2. Agregar RouterOutlet a los imports
  template: `
    <div class="flex min-h-screen overflow-hidden bg-slate-100 font-sans text-slate-900">
      <app-sidebar></app-sidebar>

      <main class="flex flex-1 flex-col overflow-hidden">
        <header class="z-10 flex shrink-0 flex-col gap-3 border-b border-slate-200 bg-white px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between md:px-6">
          <div>
            <h2 class="text-lg font-semibold tracking-tight text-slate-800 sm:text-xl">SECOP II | Insight</h2>
            <p class="mt-1 text-xs text-slate-500">Plataforma de Inteligencia Contractual</p>
          </div>
          <div class="inline-flex w-fit items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
            <span class="h-2 w-2 animate-pulse rounded-full bg-emerald-500"></span>
            Sistema Activo
          </div>
        </header>

        <div class="flex-1 overflow-auto bg-slate-50 p-3 scroll-smooth sm:p-4 md:p-6">
          <router-outlet></router-outlet>
        </div>
      </main>
    </div>
  `,
  styles: [`:host { display: block; min-height: 100vh; }`]
})
export class MainLayout {}