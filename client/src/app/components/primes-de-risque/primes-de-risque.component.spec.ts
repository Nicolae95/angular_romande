import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PrimesDeRisqueComponent } from './primes-de-risque.component';

describe('PrimesDeRisqueComponent', () => {
  let component: PrimesDeRisqueComponent;
  let fixture: ComponentFixture<PrimesDeRisqueComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PrimesDeRisqueComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PrimesDeRisqueComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
