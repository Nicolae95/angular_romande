import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PondereComponent } from './pondere.component';

describe('PondereComponent', () => {
  let component: PondereComponent;
  let fixture: ComponentFixture<PondereComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PondereComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PondereComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
