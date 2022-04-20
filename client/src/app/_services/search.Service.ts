import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/debounceTime';
import 'rxjs/add/operator/distinctUntilChanged';
import 'rxjs/add/operator/switchMap';
import 'rxjs/add/operator/do';
import { Pagination } from '../_models/pagination';
import { Company, Offer , Site, Admin } from '../_models';


@Injectable()
export class SearchService {

  constructor(private http: HttpClient) { }

  searchCompany(keyword: any) {
      return this.http.get<Company[]>(environment.api_url + '/api/company/filter/?name=' + keyword);
  }
  searchNameOffer(id: number, cc: any, keyword: any) {
    return this.http.get<Offer[]>(environment.api_url + '/api/offer/company/' + id + '/?cc=' + cc + '&name=' + keyword );
 }

  searchNamePag(name: string, statut: string, pag: number, year: any, nr: any) {
      if (pag === undefined  || pag === null) { pag = 1; }
      if (name === undefined || name === null) { name = ''; }
      return this.http.get<Pagination<Offer>>(
          environment.api_url + '/api/offer/list/?name=' + name +
           '&stare=' + statut + '&pag=' + pag + '&year=' + year + '&nr=' + Number(nr));
  }

  searchNamePagCock(name: string, statut: string, pag: number, year: any, nr: any) {
    if (pag === undefined  || pag === null) { pag = 1; }
    if (name === undefined || name === null) { name = ''; }
    return this.http.get<Pagination<Offer>>(environment.api_url + '/api/offer/list/?name=' +
    name + '&stare=' + statut + '&pag=' + pag + '&year=' + year + '&cockpit=true' + '&nr=' + Number(nr));
  }

  searchNameSite(id: number, name: string, year: string, pag: number, nr: any) {
      return this.http.get<Pagination<Site>>(
      environment.api_url + '/api/company/site/filter/' + id + '/?name=' + name + '&year=' + year + '&pag=' + pag + '&nr=' + Number(nr));
 }

 searchAdmins(keyword: string, pag: number, nr: any) {
  return this.http.get<Pagination<Admin>>(environment.api_url + '/api/user/client/list/' + '?pag=' + pag +
        '&name=' + keyword + '&nr=' + Number(nr));
}

  searchVedeor(keyword: string) {
    return this.http.get<any>(environment.api_url + '/api/user/client/filter/?name=' + keyword);
  }


}


