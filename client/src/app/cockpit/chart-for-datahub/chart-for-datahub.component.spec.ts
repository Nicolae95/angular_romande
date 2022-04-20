import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ChartForDatahubComponent } from './chart-for-datahub.component';

describe('ChartForDatahubComponent', () => {
  let component: ChartForDatahubComponent;
  let fixture: ComponentFixture<ChartForDatahubComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ChartForDatahubComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ChartForDatahubComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
