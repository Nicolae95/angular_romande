import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AnalyticsComponent } from './analytics/analytics.component';
import { AnlTablauBordComponent } from './anl-tablau-bord/anl-tablau-bord.component';
import { AnlOffersComponent } from './anl-offers/anl-offers.component';
import { AnlActivitiClientComponent } from './anl-activiti-client/anl-activiti-client.component';
import { AnlInteretBarChartComponent } from './anl-interet-bar-chart/anl-interet-bar-chart.component';
import { UserActivityAnalyticsComponent } from './user-activity-analytics/user-activity-analytics.component';
import { WysiwygComponent } from './wysiwyg/wysiwyg.component';
import { WorldMapComponent } from './world-map/world-map.component';

import { AnalitycsRoutingModule } from './analitycs-routing.module';
import { NgxMyDatePickerModule } from 'ngx-mydatepicker';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { NO_ERRORS_SCHEMA } from '@angular/compiler/src/core';
import { ChartModule } from 'angular-highcharts';
import { HeaderComponent } from '../components/header/header.component';
// FusionCharts
import { FusionChartsModule } from 'angular-fusioncharts';
import * as FusionCharts from 'fusioncharts';
import * as Maps from 'fusioncharts/fusioncharts.maps';
import * as World from 'fusionmaps/maps/fusioncharts.worldwithcountries';
// FusionCharts

// // Import FusionCharts library and chart modules
//  import { FusionChartsModule } from 'angular-fusioncharts';
//  import * as FusionCharts from 'fusioncharts';
//  import * as Maps from 'fusioncharts/fusioncharts.maps';
//  import * as Worldwithcountries from 'fusionmaps/maps/fusioncharts.worldwithcountries';
// // import * as Worldwithcountries from '../assets/js/fusioncharts.worldwithcountries';

// Maps(FusionCharts);
// Worldwithcountries(FusionCharts);
// FusionChartsModule.fcRoot(FusionCharts);



@NgModule({
  imports: [
    CommonModule,
    FusionChartsModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    NgbModule.forRoot(),
    AnalitycsRoutingModule,
    NgxMyDatePickerModule.forRoot(),
    ChartModule,
  ],
  declarations: [
    AnlTablauBordComponent,
    AnlOffersComponent,
    AnlActivitiClientComponent,
    AnalyticsComponent,
    AnlInteretBarChartComponent,
    UserActivityAnalyticsComponent,
    WysiwygComponent,
    WorldMapComponent,
  ],
  exports: [],
  // entryComponents: [ HeaderComponent ],
  // entryComponents: [ HeaderComponent ],
  // exports: [
  //   AnlTablauBordComponent,
  //   AnlOffersComponent,
  //   AnlActivitiClientComponent,
  //   AnalyticsComponent,
  //   AnlInteretBarChartComponent,
  //   UserActivityAnalyticsComponent,
  //   WysiwygComponent,
  //   WorldMapComponent, CommonModule,
  //   FormsModule
  // ],
  schemas: [ CUSTOM_ELEMENTS_SCHEMA ]
})
export class AnalitycsModule {
  static entry = AnalyticsComponent;
 }
