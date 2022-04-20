import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AsideOfferComponent } from './aside-offer.component';

describe('AsideOfferComponent', () => {
  let component: AsideOfferComponent;
  let fixture: ComponentFixture<AsideOfferComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AsideOfferComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AsideOfferComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
