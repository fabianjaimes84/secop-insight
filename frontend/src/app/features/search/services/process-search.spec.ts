import { TestBed } from '@angular/core/testing';

import { ProcessSearch } from './process-search';

describe('ProcessSearch', () => {
  let service: ProcessSearch;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ProcessSearch);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
