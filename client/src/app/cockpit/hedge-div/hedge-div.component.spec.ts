import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { HedgeDivComponent } from './hedge-div.component';

describe('HedgeDivComponent', () => {
  let component: HedgeDivComponent;
  let fixture: ComponentFixture<HedgeDivComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ HedgeDivComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(HedgeDivComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
