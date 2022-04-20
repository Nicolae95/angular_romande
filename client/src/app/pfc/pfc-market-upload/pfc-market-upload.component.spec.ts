import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PfcMarketUploadComponent } from './pfc-market-upload.component';

describe('PfcMarketUploadComponent', () => {
  let component: PfcMarketUploadComponent;
  let fixture: ComponentFixture<PfcMarketUploadComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PfcMarketUploadComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PfcMarketUploadComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
