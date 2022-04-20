import { Component, OnInit } from '@angular/core';
import { Pfc } from '../../_models/index';
import { PfcService } from '../../_services/index';
import * as moment from 'moment';
import 'rxjs/add/operator/switchMap';
import { ToastrService } from 'ngx-toastr';
import {INgxMyDpOptions, IMyDateModel} from 'ngx-mydatepicker';
import { ReloadService } from '../../_services/reload.sevice';

@Component({
  selector: 'app-pfc',
  templateUrl: './pfc.component.html',
  styleUrls: [
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css'
]
})

export class PfcComponent implements OnInit {
  pfcs: Pfc[] = [];
  chart: any;
  year: number;
  yearList: number[] = [];
  pfc_day: string;
  pfc: Pfc;
  loading: boolean;
  valute = 'CHF';
  enmData = [];
  currentDate = {};
  currentUser: any;
  pfcPeakData = {result: []};


  myOptions: INgxMyDpOptions = {
    dateFormat: 'dd.mm.yyyy',
    disableWeekends: true,
    enableDates: this.enmData,
    disableDateRanges: [{begin: {year: 2008, month: 11, day: 14}, end: {year: 2028, month: 11, day: 20}}]
  };



  constructor(private pfcService: PfcService,
              private reloadService: ReloadService,
              private toastr: ToastrService) {
              this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
  }



  ngOnInit() {
    this.getPfcs();
    const date =  new Date();
    this.year = new Date().getFullYear();
    this.pfc_day = moment(new Date()).format('DD.MM.YYYY');
    let y: number;
    for (y = this.year; y < this.year + 5; y++) { this.yearList.push(y); }
    this.year = new Date().getFullYear() + 1;


    this.reloadService.isReloadPfc.subscribe(
      (data) => {
        if (data === true) {
          this.getPfcs();
          this.getPfcYear(this.year, this.valute, this.pfc_day);
          this.reloadService.changePfc(false);
        }
      }
    );
  }

  getPfcYear(year: number, valute: string, formatt: any) {
    this.valute = '';
    this.valute = valute;
    this.loading = true;
    this.chart = null;
    this.year = year;
    this.pfc_day = formatt;
    this.pfcService.getByYear(this.year, this.valute, this.pfc_day).subscribe(
      (data) => {
        this.chart = data;
        this.loading = false; },
      (er) => { this.loading = false; },
      () => { this.loading = false;  }
    );
    this.getPfcPeakData(this.pfc_day);
  }

  getPfcs() {
    this.pfcService.getAll().subscribe((data) => {
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


      // console.log('mom', moment(this.enmData[0]).format('DD.MM.YYYY'));
      // console.log('enmData[0]', this.enmData[0]);


      const last_data = this.enmData[0];
      last_data.month = this.enmData[0].month - 1;
      // console.log('last_data', last_data);
      const pfc =  moment(last_data).format('DD.MM.YYYY');
      // console.log('pfc', pfc);


      const curent = this.enmData[0];
      curent.month =  this.enmData[0].month + 1;
      // console.log
      this.currentDate = { date: curent };
      this.getPfcYear(this.year, this.valute, pfc);

      // this.getPfcPeakData(this.pfc_day);
    });
  }

  getPfcPeakData(pfc_id: string) {
    this.pfcs.forEach(element => {
      if (element.pfc_id === pfc_id) {
      // console.log(element.pfc_id);
        this.pfcService.getPfcPeakData(element.id).subscribe(
          (data) => { this.pfcPeakData = data;
            console.log('pfcPeakData', data);
          },
          (er) => {}
        );
      }
    });
  }

  getPfcass() {
    this.pfcService.getAll().subscribe((data) => { this.pfcs = data; });
  }

  getPfc(id: number) {
    this.pfcService.getById(id).subscribe((data) => { this.pfc = data; });
  }

  onDateChanged(event: IMyDateModel): void {
    // this.setNewId(event.formatted);
    this.getPfcYear(this.year, this.valute, event.formatted);
    this.currentDate = event;
  }

}
