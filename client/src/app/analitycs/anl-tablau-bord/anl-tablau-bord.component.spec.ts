import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AnlTablauBordComponent } from './anl-tablau-bord.component';

describe('AnlTablauBordComponent', () => {
  let component: AnlTablauBordComponent;
  let fixture: ComponentFixture<AnlTablauBordComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AnlTablauBordComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AnlTablauBordComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
