import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-placeholder-section',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="flex flex-col items-center justify-center h-[60vh] text-center p-6 animate-fade-in">
      <div class="bg-gray-100 p-4 rounded-full mb-4">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
      </div>
      <h2 class="text-xl font-bold text-gray-800">{{ titulo }}</h2>
      <p class="text-gray-500 mt-2 max-w-md">Este módulo está en construcción y estará disponible pronto.</p>
    </div>
  `,
  styles: [`:host { display: block; } .animate-fade-in { animation: fadeIn 0.3s ease-in; } @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }`]
})
export class Configuracion { titulo = 'Configuración'; }
// Para IA, cambia la exportación a: export class IA { titulo = 'Asistente IA'; }
// Para Config, cambia la exportación a: export class Configuracion { titulo = 'Configuración'; }