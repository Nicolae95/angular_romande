import { NgModule, CUSTOM_ELEMENTS_SCHEMA, ApplicationModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CockpitRoutingModule } from './cockpit-routing.module';
import { CockpitsTabComponent } from './cockpits-tab/cockpits-tab.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { ChartModule } from 'angular-highcharts';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { NgxMyDatePickerModule } from 'ngx-mydatepicker';
// import { HeaderComponent } from './header/header.component';
// import { HeaderComponent } from '../components/header/header.component';
import { AddCockpitComponent } from './add-cockpit/add-cockpit.component';
import { EditCockpitBComponent } from './edit-cockpit-b/edit-cockpit-b.component';
import { AddChartsComponent } from './add-charts/add-charts.component';
import { ChartForDatahubComponent } from './chart-for-datahub/chart-for-datahub.component';
import { StatsDivComponent } from './stats-div/stats-div.component';
import { HeaderDivComponent } from './header-div/header-div.component';
import { MarketPricesComponent } from './market-prices/market-prices.component';
import { NewsDetailsComponent } from './news-details/news-details.component';
import { HedgeDivComponent } from './hedge-div/hedge-div.component';
import { ScoringComponent } from './scoring/scoring.component';
import { ChartdataComponent } from './chartdata/chartdata.component';
import { NewsEditComponent } from './news-edit/news-edit.component';
import { ColorSchemeComponent } from './color-scheme/color-scheme.component';
import { DeletesectionComponent } from './deletesection/deletesection.component';
import { ChartDetailComponent } from './chart-detail/chart-detail.component';
import { NewsDivComponent } from './news-div/news-div.component';
import { SharableService, CockpitBService } from '../_services';
import { ViewCockpitFinalComponent } from './view-cockpit-final/view-cockpit-final.component';
import { WysiwygComponent } from './wysiwyg/wysiwyg.component';
import { NgxEditorModule } from 'ngx-editor';
import { HeaderComponent } from '../components/header/header.component';
import { AppModule } from '../app.module';
import { AngularMultiSelectModule } from 'angular2-multiselect-dropdown/multiselect.component';

@NgModule({
  imports: [
    CommonModule,
    CockpitRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    NgbModule.forRoot(),
    NgxMyDatePickerModule.forRoot(),
    ChartModule,
    NgxEditorModule,
    AngularMultiSelectModule
    // HeaderComponent
    // CockpitModule

    // ApplicationModule,
    // AppModule
  ],
  declarations: [
    AddCockpitComponent,
    CockpitsTabComponent,
    EditCockpitBComponent,
    AddChartsComponent,
    // HeaderComponent,
    ChartForDatahubComponent,
    NewsDivComponent,
    StatsDivComponent,
    HeaderDivComponent,
    MarketPricesComponent,
    HedgeDivComponent,
    NewsDetailsComponent,
    ChartdataComponent,
    ScoringComponent,
    NewsEditComponent,
    ColorSchemeComponent,
    DeletesectionComponent,
    ChartDetailComponent,
    WysiwygComponent,
    ViewCockpitFinalComponent,
  ],
  exports: [
    // AddCockpitComponent,
    // CockpitsTabComponent,
    // EditCockpitBComponent,
    // AddChartsComponent,
    // HeaderComponent,
    // ChartForDatahubComponent,
    // NewsDivComponent,
    // StatsDivComponent,
    // HeaderDivComponent,
    // MarketPricesComponent,
    // HedgeDivComponent,
    // NewsDetailsComponent,
    // ChartdataComponent,
    // ScoringComponent,
    // NewsEditComponent,
    // ColorSchemeComponent,
    // DeletesectionComponent,
    // ChartDetailComponent,
    ViewCockpitFinalComponent,
  ],
  providers: [ SharableService, CockpitBService ],
  schemas: [ CUSTOM_ELEMENTS_SCHEMA ],
})
export class CockpitModule { }
