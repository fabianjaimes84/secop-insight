import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router'; // 1. Importar RouterOutlet
import { SidebarComponent } from '../sidebar/sidebar.component';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, SidebarComponent], // 2. Agregar RouterOutlet a los imports
  template: `
    <div class="flex h-screen bg-gray-50 overflow-hidden font-sans text-gray-900">
      
      <!-- Sidebar: Ahora maneja la navegación interna -->
      <app-sidebar></app-sidebar>

      <!-- Área Principal -->
      <main class="flex-1 flex flex-col h-full overflow-hidden relative">
        
        <!-- Header Superior (Opcional, si quieres mantenerlo aquí) -->
        <header class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm z-10 shrink-0">
          <div>
            <h2 class="text-xl font-bold text-gray-800 tracking-tight">SECOP II | Insight</h2>
            <p class="text-xs text-gray-500 mt-1">Plataforma de Inteligencia Contractual</p>
          </div>
          <div class="flex items-center gap-2 px-3 py-1 bg-green-50 text-green-700 rounded-full text-xs font-medium border border-green-200">
            <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            Sistema Activo
          </div>
        </header>

        <!-- 3. AQUÍ SE CARGAN LAS PÁGINAS (Dashboard, Buscar, IA, etc.) -->
        <div class="flex-1 overflow-auto p-4 md:p-6 scroll-smooth bg-gray-50">
          <router-outlet></router-outlet>
        </div>
        
      </main>
    </div>
  `,
  styles: [`:host { display: block; height: 100%; }`]
})
export class MainLayout {}