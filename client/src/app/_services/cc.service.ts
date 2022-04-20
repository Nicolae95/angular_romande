import { Site } from './../_models/site';
import { Cc } from './../_models/cc';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { Company, Offer, Admin } from '../_models';

@Injectable()
export class CcService {
  private companyObesvable = new BehaviorSubject<Company>(null);
  private offerObesvable = new BehaviorSubject<any>(null);

  constructor(private http: HttpClient) { }

  get isCompany() {
    return this.companyObesvable.asObservable(); // {2}
  }

  change(cmp: Company) {
    this.companyObesvable.next(cmp);
  }

  get isOffer() {
    return this.offerObesvable.asObservable(); // {2}
  }

  changeSite(site: any) {
    this.offerObesvable.next(site);
  }

  getAll() {
    return this.http.get<Cc[]>(environment.api_url + '/api/cc/list/');
  }

  getById(id: number) {
    return this.http.get<Cc>(environment.api_url + '/api/cc/detail/' + id + '/');
  }

  getCcByCompany(id: number) {
    return this.http.get<Site[]>(environment.api_url + '/api/company/site/' + id + '/');
  }

  getSiteVolume(id: number) {
    return this.http.get<any>(environment.api_url + '/api/company/volume/' + id + '/');
  }

  getSiteData(id: number) {
    return this.http.get<any>(environment.api_url + '/api/company/cc/' + id + '/');
  }

  getGRD(id: number) {
    return this.http.get<any>(environment.api_url + '/api/offer/grd/' + id + '/');
  }

  getLissage(companyId: number, cc: number, percent: number, years: string) {
     return this.http.get<any>(environment.api_url + '/api/offer/lissage/?company='
                              + companyId + '&cc=' + cc + '&percent=' + percent + '&years=' + years);
  }


  getByYearByCompany(year: number, id: string, site: number) {
    return this.http.get(environment.api_url + '/api/cc/year/' + year + '/company/' + id + '/site/' + site + '/');
  }

  getTranslationByYearByCompany(year: number, id: string, site: number) {
    return this.http.get(environment.api_url + '/api/translation/year/' + year + '/company/' + id + '/site/' + site + '/');
  }

  uploadFileOffer(data: FormData, folder: string ) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            resolve(xhr.response);
          } else {
            reject(xhr.response);
          }
        }
      };
      const bearer = 'JWT ' + JSON.parse(localStorage.getItem('token'));
      xhr.open('POST', environment.api_url + '/api/offer/upload/' + folder + '/', true);
      xhr.setRequestHeader('Authorization', bearer);
      xhr.send(data);
    });
  }



  upload(data: FormData) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            resolve(xhr.response);
          } else {
            reject(xhr.response);
          }
        }
      };
      const bearer = 'JWT ' + JSON.parse(localStorage.getItem('token'));
      xhr.open('POST', environment.api_url + '/api/cc/upload/', true);
      xhr.setRequestHeader('Authorization', bearer);
      xhr.send(data);
    });
  }

  uploadPondere(data: FormData) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            resolve(xhr.response);
          } else {
            reject(xhr.response);
          }
        }
      };
      const bearer = 'JWT ' + JSON.parse(localStorage.getItem('token'));
      xhr.open('POST', environment.api_url + '/api/pondere/upload/', true);
      xhr.setRequestHeader('Authorization', bearer);
      xhr.send(data);
    });
  }

  // update(cc: Cc) {
  //   return this.http.put(environment.api_url + '/api/pfc/detail/' + cc.id + '/', cc);
  // }

  delete(id: number) {
    return this.http.delete(environment.api_url + '/api/pfc/detail/' + id + '/');
  }

  private handleError(error: Response) {
    return Observable.throw(error.statusText);
  }

  hebdomadaire(year: number, id: number, site: number) {
    return this.http.get(environment.api_url + '/api/cc/y/' + year + '/c/' + id + '/s/' + site + '/');
  }

  getFile(envir: any, fileName: string) {
    return this.http.delete(envir  + '/media/' + fileName);
  }

  getOfferByToken(token: string) {
    console.log(environment.api_url + '/api/offer/mail-admin/' + token + '/');
    return this.http.get<any>(environment.api_url + '/api/offer/mail-admin/' + token + '/');
  }

  acceptedOffer(token: string, accepted: any) {
    console.log(environment.api_url + '/api/offer/mail-admin/' + token + '/', accepted);
    return this.http.post(environment.api_url + '/api/offer/mail-admin/' + token + '/', accepted);
  }

  getClient(id: number) {
    return this.http.get<Admin>(environment.api_url + '/api/user/client/id/' + id + '/');
  }

  putClient(id: number, client: Admin) {
   return this.http.put(environment.api_url + '/api/user/client/id/' + id + '/', client);
  }

  deleteSite(id: number) {
    return this.http.delete(environment.api_url + '/api/company/delete-site/' + id + '/');
  }


}
