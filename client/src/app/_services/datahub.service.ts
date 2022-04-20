import { Pondere } from './../_models/pondere';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import { Commodity } from '../_models/commodity';
import { Country } from '../_models/country';
import { BasePeak } from '../_models/basepeak';
import { CommodityMarkets } from '../_models/commodityMarkets';


@Injectable()
export class DataHubService {
    constructor(private http: HttpClient) { }

    getAllEnergies() {
        return this.http.get<Commodity[]>(environment.api_url + '/api/datahub/units/');
    }

    getCountriesByCommodityId(CommodityId: number) {
        return this.http.get<Country[]>(environment.api_url + '/api/datahub/units/?unitenergy=' + CommodityId);
    }

    getTimePeriodsByCommodityIdCountryId(CommodityId: number, CountryId: number) {
        return this.http.get<Commodity[]>(environment.api_url + '/api/datahub/units/?unitenergy=' + CommodityId + '&resource=' + CountryId);
    }

    getBasePeakByCommodityIdCountryIdPeriodId(CommodityId: number, CountryId: number, periodId: number) {
        return this.http.get<BasePeak[]>(environment.api_url + '/api/datahub/units/?unitenergy='
        + CommodityId + '&resource=' + CountryId + '&type=' + periodId);
    }

    getMarketsByCommodityIdCountryIdPeriodId(CommodityId: number, CountryId: number, periodId: number, subType: number) {
        return this.http.get<CommodityMarkets[]>(environment.api_url + '/api/datahub/units/?unitenergy='
        + CommodityId + '&resource=' + CountryId + '&type=' + periodId + '&subtype=' + subType);
    }

    getChartData(ob: any) {
        return this.http.post<any[]>(environment.api_url + '/api/datahub/market/', ob);
    }

}
