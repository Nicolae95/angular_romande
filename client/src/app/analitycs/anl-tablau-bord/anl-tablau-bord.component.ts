import { Component, OnInit } from '@angular/core';
import { AnalyticsService } from '../../_services/analytics';
import { ClientLog, AnalyticsOffers, User } from '../../_models';
import { Pagination } from '../../_models/pagination';
import { INgxMyDpOptions, IMyDateModel } from 'ngx-mydatepicker';
import * as moment from 'moment';
import { CustomObservable, UserService } from '../../_services';

@Component({
  selector: 'app-anl-tablau-bord',
  templateUrl: './anl-tablau-bord.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/animate.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css',
      '../../../assets/css/theme_analytics.css',
       '../../../assets/css/layout_analytics.css'
  ]
})

export class AnlTablauBordComponent implements OnInit {
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

  myOptions: INgxMyDpOptions = { dateFormat: 'dd.mm.yyyy', disableWeekends: false};

  constructor( private analyticsService: AnalyticsService,
               private userService: UserService,
               private customObservable: CustomObservable) {
               this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
               this.nr = this.currentUser.nr; }

  ngOnInit() {
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

  dateFromC(event: IMyDateModel): void {
    this.dateFromS = event.formatted;
    if (this.showResume) { this.getDateOffer( this.dateFromS,  this.dateToS);
    } else { this.getClientLog(this.dateFromS, this.dateToS, this.pag, this.nr); }
  }
  dateToC(event: IMyDateModel): void {
    this.dateToS = event.formatted;
    if (this.showResume) { this.getDateOffer( this.dateFromS,  this.dateToS);
    } else { this.getClientLog(this.dateFromS, this.dateToS, this.pag, this.nr); }

  }

}
