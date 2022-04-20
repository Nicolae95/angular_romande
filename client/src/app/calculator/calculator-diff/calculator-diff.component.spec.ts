import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CalculatorDiffComponent } from './calculator-diff.component';

describe('CalculatorDiffComponent', () => {
  let component: CalculatorDiffComponent;
  let fixture: ComponentFixture<CalculatorDiffComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CalculatorDiffComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CalculatorDiffComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
