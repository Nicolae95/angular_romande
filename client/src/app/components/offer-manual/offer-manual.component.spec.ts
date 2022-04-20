import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { OfferManualComponent } from './offer-manual.component';

describe('OfferManualComponent', () => {
  let component: OfferManualComponent;
  let fixture: ComponentFixture<OfferManualComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ OfferManualComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OfferManualComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
