import { TestBed, inject } from '@angular/core/testing';

import { CcService } from './cc.service';

describe('CcService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [CcService]
    });
  });

  it('should be created', inject([CcService], (service: CcService) => {
    expect(service).toBeTruthy();
  }));
});
