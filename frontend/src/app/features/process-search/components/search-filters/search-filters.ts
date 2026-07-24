import { Component, EventEmitter, Output } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';

import { Card } from '../../../../shared/ui/card/card';
import { SearchRequest } from '../../models/search-request.model';

@Component({
  selector: 'app-search-filters',
  standalone: true,
  imports: [Card, ReactiveFormsModule],
  templateUrl: './search-filters.html',
  styleUrl: './search-filters.scss',
})
export class SearchFilters {

  @Output()
  readonly onSearch = new EventEmitter<SearchRequest>();

  searchForm: FormGroup;

  constructor(private fb: FormBuilder) {

    this.searchForm = this.fb.group({

      buscar: [''],

      estado: [''],

      tipo_proceso: [''],

      fecha_publicacion_desde: [''],

      fecha_publicacion_hasta: [''],

      fecha_presentacion_desde: [''],

      fecha_presentacion_hasta: [''],

      limit: [50],

    });

  }

  search(): void {

    console.log('Filtros enviados:');
    console.log(this.searchForm.getRawValue());

    this.onSearch.emit(this.searchForm.getRawValue());

  }

  clear(): void {

    this.searchForm.reset({
      buscar: '',
      estado: '',
      tipo_proceso: '',
      fecha_publicacion_desde: '',
      fecha_publicacion_hasta: '',
      fecha_presentacion_desde: '',
      fecha_presentacion_hasta: '',
      limit: 50,
    });

  }

}