import { TestBed, inject } from '@angular/core/testing';

import { PfcService } from './pfc.service';

describe('PfcService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [PfcService]
    });
  });

  it('should be created', inject([PfcService], (service: PfcService) => {
    expect(service).toBeTruthy();
  }));
});
