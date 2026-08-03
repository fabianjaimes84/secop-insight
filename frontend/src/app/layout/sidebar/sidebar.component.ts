import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';

interface MenuItem {
  id: string;
  label: string;
  route: string;
  icon: string;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent {
  @Input() isOpen: boolean = false;
  @Output() toggleMobileSidebar = new EventEmitter<void>();

  isDesktop: boolean = typeof window !== 'undefined' && window.innerWidth >= 768;

  constructor(private router: Router) {}

  // Lista de menú actualizada con Centro de Ayuda
  readonly menuItems: MenuItem[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      route: '/dashboard',
      icon: '<i class="fa-solid fa-gauge-high"></i>',
    },
    {
      id: 'buscar',
      label: 'Buscar Procesos',
      route: '/buscar-procesos',
      icon: '<i class="fa-solid fa-magnifying-glass"></i>',
    },
    {
      id: 'seguimiento',
      label: 'Seguimiento',
      route: '/seguimiento',
      icon: '<i class="fa-solid fa-bookmark"></i>',
    },
    {
      id: 'ia',
      label: 'IA',
      route: '/ia',
      icon: '<i class="fa-solid fa-brain"></i>',
    },
    {
      id: 'configuracion',
      label: 'Configuración',
      route: '/configuracion',
      icon: '<i class="fa-solid fa-gear"></i>',
    }
  ];

  // Método auxiliar para verificar si una ruta está activa
  isActiveRoute(route: string): boolean {
    return this.router.url === route;
  }
}