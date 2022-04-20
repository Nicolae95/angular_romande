import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CalculatorMultisiteComponent } from './calculator-multisite.component';

describe('CalculatorMultisiteComponent', () => {
  let component: CalculatorMultisiteComponent;
  let fixture: ComponentFixture<CalculatorMultisiteComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CalculatorMultisiteComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CalculatorMultisiteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
