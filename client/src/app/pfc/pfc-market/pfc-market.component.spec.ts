import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PfcMarketComponent } from './pfc-market.component';

describe('PfcMarketComponent', () => {
  let component: PfcMarketComponent;
  let fixture: ComponentFixture<PfcMarketComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PfcMarketComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PfcMarketComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
