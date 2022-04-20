import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CharByYearsComponent } from './char-by-years.component';

describe('CharByYearsComponent', () => {
  let component: CharByYearsComponent;
  let fixture: ComponentFixture<CharByYearsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CharByYearsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CharByYearsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
