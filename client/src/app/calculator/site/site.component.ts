import { AnalyticsService } from '../../_services/analytics';
import { ClientLog, AnalyticsOffers, User } from '../../_models';
import { Pagination } from '../../_models/pagination';
import * as moment from 'moment';
import { CustomObservable, UserService } from '../../_services';
import { Component, OnInit, TemplateRef, ViewChild } from '@angular/core';
import { CalculatorService } from '../../_services/calculator.service';
import { EventEmitter, Input, Output, NgZone } from '@angular/core';

@Component({
  selector: 'app-site',
  templateUrl: './site.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/animate.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css',
      '../../../assets/css/theme_analytics.css',
       '../../../assets/css/layout_analytics.css',
       './site.component.css'
  ]
})

export class SiteComponent implements OnInit {


  @ViewChild('Shop')
  Shop: TemplateRef<any>;

  @ViewChild('Notification')
  Notification: TemplateRef<any>;

  @ViewChild('Review')
  Review: TemplateRef<any>;
  @Output() valueChange = new EventEmitter();

  @Input() value: any = null;
  @Input() type = 'text';
 @Input() min: number;
 @Input() max: number;
  allTabs: any;
site: boolean;
multisite: boolean;
step: string ;
step2: string;
ans: string;
counter = 5;
  showResume = true;
  // showNotifications = false;
  offerInfo: AnalyticsOffers[];
  clientPagination: Pagination<ClientLog>;
  pag = 1;
  nr: number;
  dateFrom: any;
  dateTo: any;
  dateFromS: any;
  dateToS: any;
  topUser: any;
  alarm_A = false;
  notif_A = false;
  pecent = 0;
  ipecent = 100 - this.pecent;
  percentDesc = 0;
  currentUser: User;
  userActiv: any;
  allOrUne = false;
  loading = false;
  translateyear: number;
  values2: any;
  step3: any;
  yeartranslate: any;
  translateyears: any[];
  finaltranslateyear: any[];


  constructor( private analyticsService: AnalyticsService,
               private userService: UserService,
               private pfcUpload: CalculatorService,
               private customObservable: CustomObservable) {
               this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
               this.nr = this.currentUser.nr; }

  ngOnInit() {
    this.pfcUpload.changeMessage('false', 'true');
    const date =  new Date();
    this.dateFrom = { date: { year: date.getFullYear(), month: date.getUTCMonth(), day:  date.getUTCDate() } };
    this.dateTo = { date: { year: date.getFullYear(), month: date.getUTCMonth() + 1, day:  date.getUTCDate() } };
    // for first request
    const unu = { date: { year: date.getFullYear(), month: date.getUTCMonth() - 1, day:  date.getUTCDate() } };
    const doi = { date: { year: date.getFullYear(), month: date.getUTCMonth(), day:  date.getUTCDate() } };
    if (this.dateTo.date.day === 31 ) {this.dateFrom.date.day =  this.dateFrom.date.day - 1;  unu.date.day = unu.date.day - 1; }
    this.dateFromS = moment(unu.date).format('DD.MM.YYYY');
    this.dateToS = moment(doi.date).format('DD.MM.YYYY');
    this.getDateOffer(this.dateFromS,  this.dateToS);



    this.customObservable.isNotification.subscribe(
      (data) => {
      if (data === true) {
       this.getClientLog(this.dateFromS, this.dateToS, this.pag, this.nr);
       this.showResume = false;
      }
     });
     this.step = 'upload-convert';
     this.ans = 'one';
     this.step2 = 'site';
     console.log(this.step);
     this.site = true;
this.multisite = false;
this.step = 'upload-convert';
this.ans = 'one';
console.log('qqqqqq', this.step2);
this.translateyear = (new Date()).getFullYear();
 this.values2 = [0, 0, 0, 0, 0, 0];
 this.step3 = 'dsadas';
 this.translateyears = ['true', 'false', 'false', 'false', 'false', 'false'];
 this.finaltranslateyear = this.values2[0];
  }

  getDateOffer(date_from: any, date_to: any, id?: any) {
    if (id === undefined) { id = ''; }
    this.analyticsService.getAll(date_from, date_to, id).subscribe(
      (data) => {
      this.offerInfo = data;
      this.pecent = this.offerInfo['max_weekday']['count'] / this.offerInfo['len_logs'] * 100;
      this.percentDesc = 100 - (this.offerInfo['len_mobile'] / this.offerInfo['len_desktop'] * 100);  //  caculam mobil dar ne trebuie desck
     },
      (er) => {}
    );
  }


  translateyearap(index45: any) {

    this.finaltranslateyear = [];
this.translateyears = [];
for (let i = 0; i < index45; i++) {

  this.translateyears[i] = 'true';
this.finaltranslateyear.push(this.values2[i]);
}

  }



  getClientLog(date_from: any, date_to: any, pag: number, nr: number) {
    this.loading = true;
    this.analyticsService.getClientLogList(pag, nr, this.currentUser.id, date_from, date_to).subscribe(
      (data) => { this.clientPagination = data; this.loading = false; },
      (er) => { this.loading = false; }
    );
  }

  pags(pag: number) { this.pag = pag; this.getClientLog(this.dateFromS, this.dateToS, this.pag, this.nr); }

  setNumberperPag(nr: number) {
    this.nr = Number(nr);
    this.userService.chnageNrPerPag(this.currentUser, nr).subscribe((data) => { this.pags(1); });
  }


  change(value: any, index: any): void {
    this.values2[index] = value;
    console.log(this.values2);
    if (this.max) {
      if (value > this.max) {
        this.value = this.max;
        this.valueChange.emit(this.value);
        console.log(value);
        return;
      }
    }

    if (this.min) {
      if (value < this.min) {
        this.value = this.min;
        this.valueChange.emit(this.value);
        return;
      }
    }
    this.value = value;
    this.valueChange.emit(this.value);
  }

  translateyearplus() {
  if (this.translateyear !== (new Date()).getFullYear() + 6 ) {
    this.translateyear = this.translateyear + 1 ;
  }
}

translateyearminus() {
  if (this.translateyear !== (new Date()).getFullYear() - 6 ) {
    this.translateyear = this.translateyear - 1 ;
  }
}

}
