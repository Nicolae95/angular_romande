import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CockpitsTabComponent } from './cockpits-tab.component';

describe('CockpitsTabComponent', () => {
  let component: CockpitsTabComponent;
  let fixture: ComponentFixture<CockpitsTabComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CockpitsTabComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CockpitsTabComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
