import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MultisiteComponent } from './multisite.component';

describe('MultisiteComponent', () => {
  let component: MultisiteComponent;
  let fixture: ComponentFixture<MultisiteComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MultisiteComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MultisiteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
