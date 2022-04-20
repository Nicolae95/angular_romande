import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AddChartsComponent } from './add-charts.component';

describe('AddChartsComponent', () => {
  let component: AddChartsComponent;
  let fixture: ComponentFixture<AddChartsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AddChartsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AddChartsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
