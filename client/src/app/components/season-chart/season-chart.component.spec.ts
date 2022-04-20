import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SeasonChartComponent } from './season-chart.component';

describe('SeasonChartComponent', () => {
  let component: SeasonChartComponent;
  let fixture: ComponentFixture<SeasonChartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SeasonChartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SeasonChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
