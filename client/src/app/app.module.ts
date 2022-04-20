import { NgModule, NO_ERRORS_SCHEMA } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { ChartModule, HIGHCHARTS_MODULES } from 'angular-highcharts';
import { ReactiveFormsModule, FormsModule} from '@angular/forms';
import { AppComponent } from './app.component';
import { routing } from './app.routing';
import { AlertComponent } from './_directives/index';
import { AuthGuard } from './_guards/index';
import { JwtInterceptor } from './_helpers/index';
import { AlertService, AuthenticationService, UserService, PfcService, CcService,
        CompanyService, RiscService, CustomObservable, FileService } from './_services/index';
import { HomeComponent } from './components/home/index';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/index';
import { ChartComponent } from './components/chart/index';
import { CcComponent } from './components/cc/cc.component';
import { PfcMarketService } from './_services/pfc-market.service';
import { HeaderComponent } from './components/header/header.component';
import { AngularFontAwesomeModule } from 'angular-font-awesome';
import { CompanyComponent } from './components/company/company.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { CcUploadComponent } from './components/ccupload/ccupload.component';
import { CommonModule } from '@angular/common';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ToastrModule } from 'ngx-toastr';
import { OfferComponent } from './components/offer/offer.component';
import { OfferService } from './_services/offer.service';
import { AngularMultiSelectModule } from 'angular2-multiselect-dropdown/angular2-multiselect-dropdown';
import { NgxMyDatePickerModule } from 'ngx-mydatepicker';
import { OffermailComponent } from './components/offermail/offermail.component';
import { AdmincontrolsComponent } from './components/admincontrols/admincontrols.component';
import { AdminService } from './_services/admin.service';
import { SearchService } from './_services/search.Service';
import { ClickOutsideModule } from 'ng-click-outside';
import { RisqueComponent } from './components/risque/risque.component';
import { TranslateComponent } from './components/translate/translate.component';
import { TableofferComponent } from './components/tableoffer/tableoffer.component';
import { PaginationOfferComponent } from './components/paginationOffer/paginationOffer.component';
import { OffercockpitComponent } from './components/offercockpit/offercockpit.component';
import { InfOfferComponent } from './components/inf-offer/inf-offer.component';
import { SiteDashboardComponent } from './components/site-dashboard/site-dashboard.component';
import { PondereComponent } from './components/pondere/pondere.component';
import { PondereService } from './_services/pondere.service';
import { DashboardService } from './_services/dashboart.service';
import { MonthsChartComponent } from './components/months-chart/months-chart.component';
import { SeasonChartComponent } from './components/season-chart/season-chart.component';
import { WeeklyChartComponent } from './components/weekly-chart/weekly-chart.component';
import { ReloadService } from './_services/reload.sevice';
import { ChartCcWeeklyComponent } from './components/chart-cc-weekly/chart-cc-weekly.component';
import { EditOfferComponent } from './components/edit-offer/edit-offer.component';
import { PrimesDeRisqueComponent } from './components/primes-de-risque/primes-de-risque.component';
import { AsideOfferComponent } from './components/aside-offer/aside-offer.component';
import { RisqueChartComponent } from './components/risque-chart/risque-chart.component';
import { AddMoreMailComponent } from './components/add-more-mail/add-more-mail.component';
import { InfOfferMailComponent } from './components/inf-offer-mail/inf-offer-mail.component';
import { DataHubComponent } from './components/data-hub/data-hub.component';
import { DataHubService } from './_services/datahub.service';
import { CharByYearsComponent } from './components/char-by-years/char-by-years.component';
import { ChartForDatahubComponent } from './components/chart-for-datahub/chart-for-datahub.component';
import { EditCurentUserComponent } from './components/edit-curent-user/edit-curent-user.component';
import { EcoEnergiesComponent } from './components/eco-energies/eco-energies.component';
import { ClientsComponent } from './components/clients/clients.component';
import { AddNewClientComponent } from './components/add-new-client/add-new-client.component';
import { EditOfferSmeComponent } from './components/edit-offer-sme/edit-offer-sme.component';
import { OfferManualComponent } from './components/offer-manual/offer-manual.component';
import { SetPasswordComponent } from './components/set-password/set-password.component';
import { AnalyticsService } from './_services/analytics';
import { MyDezactives } from './_guards/dezactive.guard';
import { RouterModule } from '@angular/router';
// import { AddCockpitComponent } from './components/add-cockpit/add-cockpit.component';
import { CockpitService } from './_services/cockpit.service';
import { CockpitsTabComponent } from './components/cockpits-tab/cockpits-tab.component';
import { EditCockpitBComponent } from './components/edit-cockpit-b/edit-cockpit-b.component';
import { NgxEditorModule } from 'ngx-editor';
import { CalculatorService } from './_services/calculator.service';

// Import angular-fusioncharts
// import { FusionChartsModule } from 'angular-fusioncharts';

// Import FusionCharts library and chart modules
///////// import * as FusionCharts from 'fusioncharts';
///////// import * as Maps from 'fusioncharts/fusioncharts.maps';
///////// import * as Worldwithcountries from 'fusionmaps/maps/fusioncharts.worldwithcountries';
// import * as Worldwithcountries from '../assets/js/fusioncharts.worldwithcountries';

// Maps(FusionCharts);
// Worldwithcountries(FusionCharts);
// FusionChartsModule.fcRoot(FusionCharts);



// import FusionCharts from 'fusioncharts/core';
// import Maps from 'fusioncharts/maps';

// import worldwithcountries from 'fusionmaps/maps/es/fusioncharts.worldwithcountries';

// // // Pass the fusioncharts library and chart modules
// FusionChartsModule.fcRoot(FusionCharts, Maps, worldwithcountries);


@NgModule({
    imports: [
        BrowserModule,
        // FusionChartsModule,
        FormsModule,
        ReactiveFormsModule,
        HttpClientModule,
        ChartModule,
        routing,
        AngularFontAwesomeModule,
        NgbModule.forRoot(),
        CommonModule,
        BrowserAnimationsModule,
        ToastrModule.forRoot(),
        AngularMultiSelectModule,
        NgxMyDatePickerModule.forRoot(),
        ClickOutsideModule,
        RouterModule.forRoot([
            {
              path: 'offer/mail/:token',
              component: OffermailComponent,
              canDeactivate: [MyDezactives]
            }
          ]),
        NgxEditorModule,
    ],
    declarations: [
        AppComponent,
        AlertComponent,
        HomeComponent,
        LoginComponent,
        RegisterComponent,
        ChartComponent,
        CcComponent,
        HeaderComponent,
        CompanyComponent,
        CcUploadComponent,
        OfferComponent,
        OffermailComponent,
        AdmincontrolsComponent,
        RisqueComponent,
        TranslateComponent,
        TableofferComponent,
        PaginationOfferComponent,
        OffercockpitComponent,
        InfOfferComponent,
        InfOfferMailComponent,
        SiteDashboardComponent,
        PondereComponent,
        MonthsChartComponent,
        SeasonChartComponent,
        WeeklyChartComponent,
        ChartCcWeeklyComponent,
        EditOfferComponent,
        PrimesDeRisqueComponent,
        AsideOfferComponent,
        RisqueChartComponent,
        AddMoreMailComponent,
        DataHubComponent,
        CharByYearsComponent,
        ChartForDatahubComponent,
        EditCurentUserComponent,
        EcoEnergiesComponent,
        ClientsComponent,
        AddNewClientComponent,
        EditOfferSmeComponent,
        OfferManualComponent,
        SetPasswordComponent,
        // AddCockpitComponent,
        CockpitsTabComponent,
        EditCockpitBComponent,
    ],
    exports: [
        HeaderComponent
    ],
    providers: [
        AuthGuard,
        AlertService,
        AuthenticationService,
        UserService,
        PfcService,
        PfcMarketService,
        CcService,
        CompanyService,
        OfferService,
        AdminService,
        SearchService,
        RiscService,
        CustomObservable,
        PondereService,
        DashboardService,
        ReloadService,
        DataHubService,
        AnalyticsService,
        MyDezactives,
        CockpitService,
        FileService,
        CalculatorService,
        {
            provide: HTTP_INTERCEPTORS,
            useClass: JwtInterceptor,
            multi: true
        },
    ],
    bootstrap: [AppComponent],
    schemas: [ NO_ERRORS_SCHEMA ]
})



export class AppModule { }
