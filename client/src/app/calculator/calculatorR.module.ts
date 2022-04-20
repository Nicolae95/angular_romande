import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CalculatorTabComponent } from './calculator-tab/calculator-tab.component';
import { SiteComponent } from './site/site.component';
import { MultisiteComponent } from './multisite/multisite.component';
import { CalculatorRoutingModule } from './calculator.module';
import { NgxMyDatePickerModule } from 'ngx-mydatepicker';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { NO_ERRORS_SCHEMA } from '@angular/compiler/src/core';
import { ChartModule } from 'angular-highcharts';
import { HeaderComponent } from '../components/header/header.component';
import {CalculatorComponent} from './calculator/calculator.component';
import {CalculatorDiffComponent} from './calculator-diff/calculator-diff.component';
import {CalculatorMultisiteComponent} from './calculator-multisite/calculator-multisite.component';
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
    CalculatorRoutingModule,
    NgxMyDatePickerModule.forRoot(),
    ChartModule,
  ],
  declarations: [
    MultisiteComponent,
    SiteComponent,
    CalculatorTabComponent,
    CalculatorComponent,
    CalculatorDiffComponent,
    CalculatorMultisiteComponent,

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
export class CalculatorModule {
  static entry = CalculatorComponent;
 }
