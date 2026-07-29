import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SearchFilters } from './search-filters';

describe('SearchFilters', () => {
  let component: SearchFilters;
  let fixture: ComponentFixture<SearchFilters>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SearchFilters],
    }).compileComponents();

    fixture = TestBed.createComponent(SearchFilters);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
