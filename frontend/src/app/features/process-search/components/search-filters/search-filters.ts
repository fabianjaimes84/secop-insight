import { Component, EventEmitter, Output } from '@angular/core';
import { Card } from '../../../../shared/ui/card/card';

@Component({
  selector: 'app-search-filters',
  standalone: true,
  imports: [Card],
  templateUrl: './search-filters.html',
  styleUrl: './search-filters.scss',
})
export class SearchFilters {

  @Output()
  readonly onSearch = new EventEmitter<void>();

  search(): void {
    this.onSearch.emit();
  }

}