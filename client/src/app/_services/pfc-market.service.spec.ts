import { TestBed, inject } from '@angular/core/testing';

import { PfcMarketService } from './pfc-market.service';

describe('PfcMarketService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [PfcMarketService]
    });
  });

  it('should be created', inject([PfcMarketService], (service: PfcMarketService) => {
    expect(service).toBeTruthy();
  }));
});
