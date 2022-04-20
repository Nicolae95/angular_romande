import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { NewsDivComponent } from './news-div.component';


describe('NewsDivComponent', () => {
  let component: NewsDivComponent;
  let fixture: ComponentFixture<NewsDivComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ NewsDivComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(NewsDivComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
