import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { OffercockpitComponent } from './offercockpit.component';

describe('OffercockpitComponent', () => {
  let component: OffercockpitComponent;
  let fixture: ComponentFixture<OffercockpitComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ OffercockpitComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OffercockpitComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
