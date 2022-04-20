import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MarketPricesComponent } from './market-prices.component';

describe('MarketPricesComponent', () => {
  let component: MarketPricesComponent;
  let fixture: ComponentFixture<MarketPricesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MarketPricesComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MarketPricesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
