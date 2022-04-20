import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RisqueChartComponent } from './risque-chart.component';

describe('RisqueChartComponent', () => {
  let component: RisqueChartComponent;
  let fixture: ComponentFixture<RisqueChartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RisqueChartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RisqueChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
