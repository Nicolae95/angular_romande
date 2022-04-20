import { AnalitycsModule } from './analitycs.module';

describe('AnalitycsModule', () => {
  let analitycsModule: AnalitycsModule;

  beforeEach(() => {
    analitycsModule = new AnalitycsModule();
  });

  it('should create an instance', () => {
    expect(analitycsModule).toBeTruthy();
  });
});
