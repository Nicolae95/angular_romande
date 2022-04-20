import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EditOfferSmeComponent } from './edit-offer-sme.component';

describe('EditOfferSmeComponent', () => {
  let component: EditOfferSmeComponent;
  let fixture: ComponentFixture<EditOfferSmeComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EditOfferSmeComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditOfferSmeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
