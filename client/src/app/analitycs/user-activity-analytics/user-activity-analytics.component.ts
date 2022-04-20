import { Component, OnInit, Input } from '@angular/core';
import { AnalyticsService } from '../../_services/analytics';
import { OfferService } from '../../_services/offer.service';
import { INgxMyDpOptions, IMyDateModel } from 'ngx-mydatepicker';
import * as moment from 'moment';
import { environment } from '../../../environments/environment';


@Component({
  selector: 'app-user-activity-analytics',
  templateUrl: './user-activity-analytics.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css',
    '../../../assets/css/theme_analytics.css',
    '../../../assets/css/layout_analytics.css'
  ]
})
export class UserActivityAnalyticsComponent implements OnInit {
  @Input() userActiv: any;
  @Input() type: any;
  offerList: any;
  lastOffer: any;
  lastOfferID: number;
  offerActivity: any;
  actualite: any;
  dateFrom: any;
  dateTo: any;
  dateFromS: any;
  dateToS: any;
  environment = environment.api_url;
  myFile: File[];
  fileValid = false;
  timpu_mediu: any;
  myOptions: INgxMyDpOptions = { dateFormat: 'dd.mm.yyyy', disableWeekends: false };

  constructor(private analyticsService: AnalyticsService,
              private offerService: OfferService
  ) { }

  ngOnInit() {
    // console.log('userActiv', this.userActiv, this.type);
    const date =  new Date();
    this.dateFrom = { date: { year: date.getFullYear(), month: date.getUTCMonth(), day:  date.getUTCDate() } };
    this.dateTo = { date: { year: date.getFullYear(), month: date.getUTCMonth() + 1, day:  date.getUTCDate() } };

    const unu = { date: { year: date.getFullYear(), month: date.getUTCMonth() - 1, day:  date.getUTCDate() } };
    const doi = { date: { year: date.getFullYear(), month: date.getUTCMonth(), day:  date.getUTCDate() } };
    if (this.dateTo.date.day === 31 ) {this.dateFrom.date.day =  this.dateFrom.date.day - 1;  unu.date.day = unu.date.day - 1; }
    this.dateFromS = moment(unu.date).format('DD.MM.YYYY');
    this.dateToS = moment(doi.date).format('DD.MM.YYYY');

    if (this.type === 1) {
      this.getClientLogById(this.userActiv.id, this.dateFromS,  this.dateToS);
      this.offerById(this.userActiv.last_offer);
      this.offerLists(this.userActiv.id, '');
      // this.getOfferActivity(this.userActiv.last_offer, this.userActiv.id);
      // console.log('if');

    } else {
      // console.log('else');
      this.getClientLogById(this.userActiv.client.id, this.dateFromS,  this.dateToS);
      this.offerById(this.userActiv.last_offer);
      this.offerLists(this.userActiv.client.id, '');
      // this.getOfferActivity(this.userActiv.last_offer, this.userActiv.client.id);
    }
  }

  getClientLogById(id: number, dateFromS: any, dateToS: any) {
    this.analyticsService.getClientLogById(id, dateFromS, dateToS).subscribe((data) => {this.actualite = data; } );
  }

  getOfferActivity(ofId: number, clientId: number) {
    this.analyticsService.getOfferActivity(ofId, clientId).subscribe((data) => { this.offerActivity = data;
    this.timpu_mediu = moment.duration(this.offerActivity['med_time'], 'seconds');
  });
  }

  offerById(id: number) {
    this.offerService.getById(Number(id)).subscribe((data) => { this.lastOffer = data; } );
    if (this.type === 1) {
    this.getOfferActivity(id, this.userActiv.id);
    } else { this.getOfferActivity(id, this.userActiv.client.id); }
  }

  offerLists(id: number, type: string) {
    this.offerService.getOfferList(id, type).subscribe((data) =>  {  this.offerList = data; });
  }

  dateFromC(event: IMyDateModel): void {
    this.dateFromS = event.formatted;
    if (this.type === 1) {
    this.getClientLogById(this.userActiv.id, this.dateFromS, this.dateToS);
    } else {   this.getClientLogById(this.userActiv.client.id, this.dateFromS,  this.dateToS); }
  }

  dateToC(event: IMyDateModel): void {
    this.dateToS = event.formatted;
    if (this.type === 1) {
    this.getClientLogById(this.userActiv.id, this.dateFromS, this.dateToS);
    } else {   this.getClientLogById(this.userActiv.client.id, this.dateFromS,  this.dateToS); }
  }

  openFile(name: string) { window.open(this.environment  +  name); }

  // fileEvent(files: File[]) {
  //   for (let i = 0; i < files.length; i++) {
  //     const element = files[i];
  //     console.log(element.name);
  //   }
  //   this.myFile = files;
  //   if (this.myFile == null) { this.fileValid = false;
  //   } else { this.fileValid = true; }
  // }

}
