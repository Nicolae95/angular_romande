import { Risc } from './../_models/risc';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';


@Injectable()
export class RiscService {
    constructor(private http: HttpClient) { }

    getAll() {
        return this.http.get<Risc[]>(environment.api_url + '/api/offer/riscs/');
    }

    getPfcRisqs(year: number, market: boolean) {
        // console.log(environment.api_url + '/api/pfc/riscs/?year=' + year + '&market=' + market);
        return this.http.get<Risc[]>(environment.api_url + '/api/pfc/riscs/?year=' + year + '&market=' + market);
    }

    // getById(pk: number) {
    //     return this.http.get<Admin>(environment.api_url + '/api/user/client/id/' + pk + '/');
    // }

    // create(client: Admin) {
    //     return this.http.post(environment.api_url + '/api/user/client/list/', client);
    // }

    // update(client: Admin) {
    //     return this.http.put(environment.api_url + '/api/user/client/id/' + client.pk + '/', client);
    // }

    // delete(pk: number) {
    //     return this.http.delete(environment.api_url + '/api/user/client/id/' + pk + '/');
    // }
}
