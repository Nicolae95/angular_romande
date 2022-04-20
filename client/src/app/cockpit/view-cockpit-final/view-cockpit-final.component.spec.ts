import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewCockpitFinalComponent } from './view-cockpit-final.component';

describe('ViewCockpitFinalComponent', () => {
  let component: ViewCockpitFinalComponent;
  let fixture: ComponentFixture<ViewCockpitFinalComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ViewCockpitFinalComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ViewCockpitFinalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
