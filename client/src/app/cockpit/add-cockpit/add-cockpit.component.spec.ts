import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AddCockpitComponent } from './add-cockpit.component';

describe('AddCockpitComponent', () => {
  let component: AddCockpitComponent;
  let fixture: ComponentFixture<AddCockpitComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AddCockpitComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AddCockpitComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
