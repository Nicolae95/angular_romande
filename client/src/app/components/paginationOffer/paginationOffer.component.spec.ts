import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PaginationOfferComponent } from './paginationOffer.component';

describe('PaginationOfferComponent', () => {
  let component: PaginationOfferComponent;
  let fixture: ComponentFixture<PaginationOfferComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PaginationOfferComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PaginationOfferComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
