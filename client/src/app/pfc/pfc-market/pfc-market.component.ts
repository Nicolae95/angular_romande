import { Pfc } from '../../_models/index';
import { PfcMarketService } from './../../_services/pfc-market.service';
import { Component, OnInit } from '@angular/core';
import * as moment from 'moment';
import 'rxjs/add/operator/switchMap';
import { ToastrService } from 'ngx-toastr';
import {INgxMyDpOptions, IMyDateModel} from 'ngx-mydatepicker';

@Component({
  selector: 'app-pfc',
  templateUrl: './pfc-market.component.html',
  styleUrls: [
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css'
  ]
})

export class PfcMarketComponent implements OnInit {
  pfcs: Pfc[] = [];
  chart: any;
  year: number;
  yearList: number[] = [];
  pfc_day: string;
  pfc: Pfc;
  loading: boolean;
  valute = 'CHF';
  enmData = [];
  currentDate: any;

  myOptions: INgxMyDpOptions = {
    dateFormat: 'dd.mm.yyyy',
    disableWeekends: true,
    enableDates: this.enmData,
    disableDateRanges: [{begin: {year: 2008, month: 11, day: 14}, end: {year: 2028, month: 11, day: 20}}]
  };


  constructor(private pfcMarketService: PfcMarketService,
              private toastr: ToastrService
    ) {
  }

  ngOnInit() {
    const date =  new Date();
    this.currentDate = { date: { year: date.getFullYear(), month: date.getUTCMonth() + 1, day:  date.getUTCDate() } };
    this.year = new Date().getFullYear();
    this.pfc_day = moment(new Date()).format('DDMMYYYY');
    this.getPfcYear(this.year, this.valute);
    let y: number;
    for (y = this.year; y < this.year + 5; y++) {
      this.yearList.push(y);
    }
    this.getPfcs();
  }

  getPfcMarketYear(year: number, valute: any) {
    this.valute =  valute;
    this.chart = null;
    this.year = year;
    this.pfcMarketService.getByYear(year, this.pfc_day, this.valute).subscribe((data) => { this.chart = data; });
  }

  setNewId(id: string) {
    this.loading = true;
    this.chart = null;
    this.pfc_day = id;
    this.pfcMarketService.getByYear(this.year, id, this.valute).subscribe((data) => { this.chart = data; this.loading = false;  });
  }

  getPfcs() {
    this.pfcMarketService.getAll().subscribe((data) => {
      this.pfcs = data;
      data.forEach(element => {
        if (element.pfc_id.length === 10) {
          this.enmData.push({
            'day': Number(element['pfc_id'].slice(0, 2)),
            'month': Number(element['pfc_id'].slice(3, 5)),
            'year': Number(element['pfc_id'].slice(6, 10))
          });
        } else {
          this.enmData.push({
            'day': Number(element['pfc_id'].slice(0, 1)),
            'month': Number(element['pfc_id'].slice(2, 4)),
            'year': Number(element['pfc_id'].slice(5, 9))
          });
      }
      });
    }, );
  }


  getPfcYear(year: number, valute: string) {
    this.valute = '';
    this.valute = valute;
    this.loading = true;
    this.chart = null;
    this.year = year;
    this.pfcMarketService.getByYear(year, this.pfc_day, this.valute).subscribe(
      (data) => {
        this.chart = data;
        this.loading = false; },
      (errores) => { this.loading = false; },
      () => { this.loading = false;  }
    );
  }

  onDateChanged(event: IMyDateModel): void {
    this.setNewId(event.formatted);
    this.currentDate = event;
  }

}
