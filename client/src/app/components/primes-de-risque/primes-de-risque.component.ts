import { Component, OnInit } from '@angular/core';
import {  RiscService } from '../../_services/index';
import 'rxjs/add/operator/switchMap';



@Component({
  selector: 'app-primes-de-risque',
  templateUrl: './primes-de-risque.component.html',
  styleUrls: [
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css'
]
})


export class PrimesDeRisqueComponent implements OnInit {
  chart: any;
  loading: boolean;
  valute = 'CHF';
  market = false;
  year: number;
  yearList: number[] = [];
  count: number;
  dates: any[] = [];

    transform(arr: Array<any>): any {
      return arr.sort((a, b) => {
        if (a > b) {return  1; }
        if (a < b) {return -1; }
        return 0;
      });
    }

  constructor(private riscService: RiscService) {

  }


  ngOnInit() {
    this.year = new Date().getFullYear() + 1;
    let y: number;
    for (y = this.year; y < this.year + 4; y++) {
      this.yearList.push(y);
    }
    this.getRisq(this.year, this.market);
  }

  getRisq(year: number, market: boolean) {
    this.year = year;
    this.market = market;
    this.loading = true;
    this.chart = null;
    this.riscService.getPfcRisqs(year, market).subscribe(
      (data) => {
        this.chart = data;
        this.transform(data['pfcs']);
        this.count = this.chart['pfcs_len'];
        this.loading = false;
       },
      (e) => { this.loading = false; this.dates = []; },
      () => { this.loading = false; this.dates = []; }
    );
  }

}
