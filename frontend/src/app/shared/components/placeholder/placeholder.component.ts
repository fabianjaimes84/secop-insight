import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router'; // Para leer los datos de la ruta

@Component({
  selector: 'app-placeholder',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="flex flex-col items-center justify-center h-[80vh] text-center animate-fade-in-up">
      <div class="bg-blue-50 p-8 rounded-full mb-6 shadow-sm border border-blue-100">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </div>
      
      <h2 class="text-3xl font-bold text-gray-800 mb-3">{{ titulo }}</h2>
      <p class="text-gray-500 max-w-lg mb-8 text-lg leading-relaxed">{{ mensaje }}</p>
      
      <div class="px-6 py-3 bg-gray-100 rounded-lg text-sm text-gray-400 border border-gray-200 inline-flex items-center gap-3">
        <svg class="animate-spin h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="font-medium">En construcción - Próximamente</span>
      </div>
    </div>
  `,
  styles: [`
    :host { display: block; height: 100%; width: 100%; }
    .animate-fade-in-up { animation: fadeInUp 0.5s ease-out forwards; }
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `]
})
export class PlaceholderComponent {
  titulo: string = 'Sección en desarrollo';
  mensaje: string = 'Estamos trabajando en esta funcionalidad.';

  constructor(private route: ActivatedRoute) {
    // Leer los datos definidos en app.routes.ts
    this.route.data.subscribe(data => {
      if (data['title']) this.titulo = data['title'];
      if (data['message']) this.mensaje = data['message'];
    });
  }
}