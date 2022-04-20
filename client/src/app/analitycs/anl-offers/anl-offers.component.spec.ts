import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AnlOffersComponent } from './anl-offers.component';

describe('AnlOffersComponent', () => {
  let component: AnlOffersComponent;
  let fixture: ComponentFixture<AnlOffersComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AnlOffersComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AnlOffersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
