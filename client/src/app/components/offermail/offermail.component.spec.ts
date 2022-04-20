import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { OffermailComponent } from './offermail.component';

describe('OffermailComponent', () => {
  let component: OffermailComponent;
  let fixture: ComponentFixture<OffermailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ OffermailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OffermailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
