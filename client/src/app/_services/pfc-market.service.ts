import { Pfc } from './../_models/pfc';
import { PfcMarket } from './../_models/market';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';


@Injectable()
export class PfcMarketService {

  constructor(private http: HttpClient) { }


  getAll() {
        return this.http.get<Pfc[]>(environment.api_url + '/api/pfc-market/list/');
    }

    getById(id: number) {
        return this.http.get(environment.api_url + '/api/pfc-market/detail-market/' + id + '/');
    }

    getByDate(id: string) {
      console.log(environment.api_url + '/api/pfc-market/date/?date=' + id );
      return this.http.get<Pfc>(environment.api_url + '/api/pfc-market/date/?date=' + id );
  }
    getByYear(year: number, id: string, valute: string) {
      console.log(environment.api_url + '/api/pfc-market/year/' + year + '/?unit=' + valute + '&pfc=' + id);
      return this.http.get(environment.api_url + '/api/pfc-market/year/' + year + '/?unit=' + valute + '&pfc=' + id);
    }

    create(pfc: PfcMarket) {
      return this.http.post(environment.api_url + '/api/pfc-market/list/', pfc);
    }

    update(pfc: PfcMarket) {
      return this.http.put(environment.api_url + '/api/pfc-market/detail-market/' + pfc.id + '/', pfc);
    }

    delete(id: number) {
      return this.http.delete(environment.api_url + '/api/pfc-market/detail-market/' + id + '/');
    }

}
