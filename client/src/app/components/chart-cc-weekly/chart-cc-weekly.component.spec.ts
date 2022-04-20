import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ChartCcWeeklyComponent } from './chart-cc-weekly.component';

describe('ChartCcWeeklyComponent', () => {
  let component: ChartCcWeeklyComponent;
  let fixture: ComponentFixture<ChartCcWeeklyComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ChartCcWeeklyComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ChartCcWeeklyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
