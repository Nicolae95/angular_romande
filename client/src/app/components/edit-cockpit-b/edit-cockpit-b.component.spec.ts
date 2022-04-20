import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EditCockpitBComponent } from './edit-cockpit-b.component';

describe('EditCockpitBComponent', () => {
  let component: EditCockpitBComponent;
  let fixture: ComponentFixture<EditCockpitBComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EditCockpitBComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditCockpitBComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
