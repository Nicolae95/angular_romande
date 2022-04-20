import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AnlInteretBarChartComponent } from './anl-interet-bar-chart.component';

describe('AnlInteretBarChartComponent', () => {
  let component: AnlInteretBarChartComponent;
  let fixture: ComponentFixture<AnlInteretBarChartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AnlInteretBarChartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AnlInteretBarChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
