import { Component, OnInit } from '@angular/core';
import { Company } from './../../_models/company';
import { Cc } from '../../_models/index';
import { CcService, CustomObservable } from '../../_services/index';
import 'rxjs/add/operator/switchMap';
import 'rxjs/add/operator/switchMap';
import { DashboardService } from '../../_services/dashboart.service';



@Component({
  selector: 'app-translate',
  templateUrl: './translate.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css'
  ]
})

export class TranslateComponent implements OnInit {
  CCs: Cc[] = [];
  chart: any;
  cc: Cc;
  loading = false;
  id: string;
  cc_day: string;
  nodata = false;
  company: Company;
  site: any;
  year: number;
  lastYear: number;
  yearList: number[] = [];
  data = true;
  typeRecques = true;

  constructor(private ccService: CcService,
              private customObservable: CustomObservable,
              private dashboardService: DashboardService
            ) { }

  ngOnInit() {
    this.ccService.isCompany.subscribe((data) => {this.company = data; this.getCCyear(this.lastYear, data); },
      (err) => { this.company = null; this.getCCyear(this.lastYear, null); }
    );

    this.customObservable.isSite.subscribe(
      (data) => { this.site = data;
                  if (this.site) {
                  this.years(this.site.year);
                  this.getCCyear(this.year, this.company);
                  this.getDashbord(this.site.id, this.year); }
                },
      (err) => { }
    );
  }

  years(year: any) {
    this.yearList.length = 0;
    this.year = year + 1 ;
    this.lastYear = year;
    for ( let y = this.year ; y < this.year + 6; y++) { this.yearList.push(y); }

  }

  getCCyear(year: number, cmp: Company) {
    this.chart = null;
    if (cmp && this.site ) {
      this.loading = true;
      this.year = null;
      this.year = year;
      if (this.site) { this.getDashbord(this.site.id, this.year); }
      this.customObservable.changeYear(this.year);
      if (this.site) {
        if (this.typeRecques) {
        this.ccService.getByYearByCompany(this.lastYear, String(cmp.id), this.site.id ).subscribe(
          (data) => {
            this.chart = data;
            this.loading = false;
          },
          (errores) => {
            this.loading = false;
          } ,
        );
      } else {this.ccService.hebdomadaire(year,  this.company.id,  this.site.id).subscribe(
        (data) => {
          this.chart = data;
          this.loading = false;
        });
      }
      }
    }
  }

  getTranslateYear (year: number, company: Company) {
    this.year = null;
    this.year = year;
    this.chart = null;
    this.customObservable.changeYear(this.year);
    if (this.company) {
      if (this.site) { this.getDashbord(this.site.id, this.year); console.log('site', this.site); }
      this.loading = true;
      if (this.typeRecques) {
      this.ccService.getTranslationByYearByCompany(year, String(this.company.id), this.site.id).subscribe(
        (data) => {
          this.chart = data;
          this.loading = false;
          },
        (errores) => {
          this.loading = false;
        },
        () => { this.loading = false;  }
      );
    } else {this.ccService.hebdomadaire(year,  this.company.id,  this.site.id).subscribe(
      (data) => {
        this.chart = data;
        this.loading = false;
      });
    }

    }
  }

  getDashbord(id: number, year: any) {
    this.year = year;
    this.dashboardService.getDashboard(id, year).subscribe(
      (data) => {
        this.customObservable.changeVolume(data.months_total);
      },
      (err) => {
        console.log('err:', err.error);
      }
    );
  }

  getCCs() {
    this.ccService.getAll().subscribe((data) => { this.CCs = data; });
  }

  getType(year: number) {
    console.log('typeRecques', this.typeRecques, year);
    if (this.typeRecques && year === 2017) {
      this.getCCyear(year, this.company);
    } else {   this.getTranslateYear (year, this.company);  }

  }

}
