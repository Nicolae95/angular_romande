import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CalculatorTabComponent } from './calculator-tab.component';

describe('CalculatorTabComponent', () => {
  let component: CalculatorTabComponent;
  let fixture: ComponentFixture<CalculatorTabComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CalculatorTabComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CalculatorTabComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
