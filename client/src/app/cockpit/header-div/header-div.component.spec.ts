import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { HeaderDivComponent } from './header-div.component';

describe('HeaderDivComponent', () => {
  let component: HeaderDivComponent;
  let fixture: ComponentFixture<HeaderDivComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ HeaderDivComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(HeaderDivComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
