import { Meter } from './../_models/meter';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Company } from '../_models/company';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import { Pagination } from '../_models/pagination';


@Injectable()
export class CompanyService {

  constructor(private http: HttpClient) { }

    getAll(pag: number, name: string, nr: any) {
        return this.http.get<Pagination<Company>>(environment.api_url + '/api/company/pagination/?pag=' + pag +
        '&name=' + name + '&nr=' + Number(nr));
    }

    getAllList() {
        return this.http.get<any>(environment.api_url + '/api/company/list/');
    }

    getMeters() {
        return this.http.get<Meter[]>(environment.api_url + '/api/company/meters/');
    }

    getMetersByCompany(id: number) {
        return this.http.get<Meter[]>(environment.api_url + '/api/company/meter/company/' + id + '/');
    }

    getMetersUploadByCompany(id: number) {
        return this.http.get<Meter[]>(environment.api_url + '/api/company/meter/company/' + id + '/?site=false');
    }

    getCompanyById(id: number) {
        return this.http.get<Company>(environment.api_url + '/api/company/id/' + id + '/');
    }

    createCompany(company: Company) {
        console.log(environment.api_url + '/api/company/list/', company);
        return this.http.post(environment.api_url + '/api/company/list/', company);
    }

    update(company: Company) {
        return this.http.put(environment.api_url + '/api/company/id/' + company.id + '/', company);
    }

    delete(id: number) {
        return this.http.delete(environment.api_url + '/api/company/id/' + id + '/');
    }

    getDistributionSME() {
        return this.http.get(environment.api_url + '/api/company/sme-emails/');
    }

    postDistributionSME(emails: any) {
        return this.http.post(environment.api_url + '/api/company/sme-emails/' , {'email': emails} );
    }
}





