import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EcoEnergiesComponent } from './eco-energies.component';

describe('EcoEnergiesComponent', () => {
  let component: EcoEnergiesComponent;
  let fixture: ComponentFixture<EcoEnergiesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EcoEnergiesComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EcoEnergiesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
