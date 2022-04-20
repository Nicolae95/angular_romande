import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PfcUploadComponent } from './pfc-upload.component';

describe('PfcUploadComponent', () => {
  let component: PfcUploadComponent;
  let fixture: ComponentFixture<PfcUploadComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PfcUploadComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PfcUploadComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
