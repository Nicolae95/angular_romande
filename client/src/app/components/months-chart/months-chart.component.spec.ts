import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MonthsChartComponent } from './months-chart.component';

describe('MonthsChartComponent', () => {
  let component: MonthsChartComponent;
  let fixture: ComponentFixture<MonthsChartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MonthsChartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MonthsChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
