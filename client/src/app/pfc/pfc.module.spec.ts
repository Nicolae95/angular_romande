import { PfcModule } from './pfc.module';

describe('PfcModule', () => {
  let pfcModule: PfcModule;

  beforeEach(() => {
    pfcModule = new PfcModule();
  });

  it('should create an instance', () => {
    expect(pfcModule).toBeTruthy();
  });
});
