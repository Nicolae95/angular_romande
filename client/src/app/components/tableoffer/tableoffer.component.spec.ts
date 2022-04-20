import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TableofferComponent } from './tableoffer.component';

describe('TableofferComponent', () => {
  let component: TableofferComponent;
  let fixture: ComponentFixture<TableofferComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TableofferComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TableofferComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
