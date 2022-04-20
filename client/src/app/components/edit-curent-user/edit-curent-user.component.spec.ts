import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EditCurentUserComponent } from './edit-curent-user.component';

describe('EditCurentUserComponent', () => {
  let component: EditCurentUserComponent;
  let fixture: ComponentFixture<EditCurentUserComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EditCurentUserComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditCurentUserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
