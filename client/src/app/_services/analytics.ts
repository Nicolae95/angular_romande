import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { ClientLog, AnalyticsOffers, LastActivity } from '../_models';
import { Pagination } from '../_models/pagination';


@Injectable()
export class AnalyticsService {

  constructor(private http: HttpClient) { }

  getAll(date_from: any, date_to: any, id?: number) {
    return this.http.get<AnalyticsOffers[]>(environment.api_url + '/api/company/analytics/?date_from=' +
    date_from + '&date_to=' + date_to + '&client=' + id );
  }

  getClientLogList(pag: number, nr: number, id: number, date_from: any, date_to: any) {
    return this.http.get<Pagination<ClientLog>>(environment.api_url +
       '/api/company/client-log/?pag=' + pag + '&nr=' + nr + '&user=' + id + '&date_from=' + date_from + '&date_to=' + date_to);
  }




  getClientLogById(id: number, date_from: any, date_to: any) {
    return this.http.get(environment.api_url +
      '/api/company/client-log/id/?client=' + id + '&date_from=' + date_from + '&date_to=' + date_to);
  }

  getOfferActivity(ofId: number, clientId: number) {
    return this.http.get(environment.api_url + '/api/company/offer-activity/?offer=' + ofId + '&client=' + clientId);
  }

  getLastActivity(name: string, pag: number, nr: number) {
    return this.http.get<Pagination<LastActivity>>(environment.api_url +
       '/api/company/last-activity/?name=' + name + '&pag=' + pag + '&nr=' + nr);
  }


  getClientLogTop(id) {
    return this.http.get(environment.api_url + '/api/company/client-log-top/?user=' + id);
  }

}
