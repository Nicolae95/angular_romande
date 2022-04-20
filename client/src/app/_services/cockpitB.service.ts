import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable()
export class CockpitBService {

    constructor(private http: HttpClient) { }

    getCockpitMarketById(id: number) {
        return this.http.get(environment.api_url + '/api/cockpit/cockpit-market/' + id + '/');
    }

    getChartsByCockpit(id: number) {
        return this.http.get(environment.api_url + '/api/cockpit/cockpit-chart/' + id + '/');
    }

    getForTables(cid: any) {
        return this.http.get(environment.api_url + '/api/datahub/tabel/?cid=' + cid);
    }
    getForCharts(cid: any, dfrom: any, dto: any) {
        // tslint:disable-next-line:max-line-length
        return this.http.get(environment.api_url + '/api/datahub/chart/?cid=' + cid + '&dfrom=' + dfrom + '&dto=' + dto);
    }

}
