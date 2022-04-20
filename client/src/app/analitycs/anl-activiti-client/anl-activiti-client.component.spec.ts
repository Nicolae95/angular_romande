import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AnlActivitiClientComponent } from './anl-activiti-client.component';

describe('AnlActivitiClientComponent', () => {
  let component: AnlActivitiClientComponent;
  let fixture: ComponentFixture<AnlActivitiClientComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AnlActivitiClientComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AnlActivitiClientComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
