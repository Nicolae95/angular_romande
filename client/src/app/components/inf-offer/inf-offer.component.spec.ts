import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { InfOfferComponent } from './inf-offer.component';

describe('InfOfferComponent', () => {
  let component: InfOfferComponent;
  let fixture: ComponentFixture<InfOfferComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ InfOfferComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(InfOfferComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
