import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { UserActivityAnalyticsComponent } from './user-activity-analytics.component';

describe('UserActivityAnalyticsComponent', () => {
  let component: UserActivityAnalyticsComponent;
  let fixture: ComponentFixture<UserActivityAnalyticsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ UserActivityAnalyticsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(UserActivityAnalyticsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
