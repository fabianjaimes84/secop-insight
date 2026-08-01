import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="p-6 animate-fade-in">
      <h1 class="text-2xl font-bold text-gray-800 mb-4">Panel General</h1>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 class="text-gray-500 text-sm">Procesos Activos</h3>
          <p class="text-3xl font-bold text-blue-600 mt-2">1,245</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 class="text-gray-500 text-sm">Entidades</h3>
          <p class="text-3xl font-bold text-green-600 mt-2">380</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 class="text-gray-500 text-sm">Valor Total</h3>
          <p class="text-3xl font-bold text-purple-600 mt-2">$45B</p>
        </div>
      </div>
    </div>
  `,
  styles: [`:host { display: block; } .animate-fade-in { animation: fadeIn 0.3s ease-in; } @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }`]
})
export class Dashboard {}