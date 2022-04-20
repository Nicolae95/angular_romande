import { CockpitModule } from './cockpit.module';

describe('CockpitModule', () => {
  let cockpitModule: CockpitModule;

  beforeEach(() => {
    cockpitModule = new CockpitModule();
  });

  it('should create an instance', () => {
    expect(cockpitModule).toBeTruthy();
  });
});
