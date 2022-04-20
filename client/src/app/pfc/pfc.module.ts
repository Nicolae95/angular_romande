import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PfcMarketUploadComponent } from './pfc-market-upload/pfc-market-upload.component';
import { PfcUploadComponent } from './pfc-upload/pfc-upload.component';
import { PfcComponent } from './pfc/pfc.component';
import { PfcMarketComponent } from './pfc-market/pfc-market.component';
import { PfcRoutingModule } from './pfc-routing.module';
import { NgxMyDatePickerModule } from 'ngx-mydatepicker';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { NO_ERRORS_SCHEMA } from '@angular/compiler/src/core';
import { ChartModule } from 'angular-highcharts';
import { ChartComponent } from './chart';
// import {  } from './components/chart/index';


@NgModule({
  imports: [
    CommonModule,
    PfcRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    NgbModule.forRoot(),
    NgxMyDatePickerModule.forRoot(),
    ChartModule,
  ],
  declarations: [
    ChartComponent,
    PfcMarketComponent,
    PfcComponent,
    PfcUploadComponent,
    PfcMarketUploadComponent,
  ],
  schemas: [ CUSTOM_ELEMENTS_SCHEMA ]
})
export class PfcModule { }
