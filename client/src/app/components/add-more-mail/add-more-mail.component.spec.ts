import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AddMoreMailComponent } from './add-more-mail.component';

describe('AddMoreMailComponent', () => {
  let component: AddMoreMailComponent;
  let fixture: ComponentFixture<AddMoreMailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AddMoreMailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AddMoreMailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
