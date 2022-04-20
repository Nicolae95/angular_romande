import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AdmincontrolsComponent } from './admincontrols.component';

describe('AdmincontrolsComponent', () => {
  let component: AdmincontrolsComponent;
  let fixture: ComponentFixture<AdmincontrolsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AdmincontrolsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AdmincontrolsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
