import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Admin } from '../_models/index';
import { Pagination } from '../_models/pagination';
import { CockpitNews } from '../_models/cockpitNews';

@Injectable()
export class CockpitService {

    constructor(private http: HttpClient) { }

    getCockpitNews() {
        return this.http.get<CockpitNews>(environment.api_url + '/api/cockpit/cockpit-news/');
    }

    postCockpitNews(cockpit: any) {
        // console.log('1', environment.api_url + '/api/cockpit/cockpit-news/', cockpit);
        return this.http.post(environment.api_url + '/api/cockpit/cockpit-news/', cockpit);
    }
    putCockpitNewsOffer(id: number, offers: any) {
        // console.log('2', environment.api_url + '/api/cockpit/cockpit-offer-news/' + id + '/', {'offers': offers});
        return this.http.put(environment.api_url + '/api/cockpit/cockpit-offer-news/' + id + '/', {'offers': offers});
    }

    getCockpitNewsById(id: number) {
        return this.http.get(environment.api_url + '/api/cockpit/cockpit-news/' + id + '/');
    }

    deleteCockpitNewsById(id: number) {
        return this.http.delete(environment.api_url + '/api/cockpit/cockpit-news/' + id + '/');
    }

    putCockpitNewsById(id: number, cockpit: any) {
        // console.log('3', environment.api_url + '/api/cockpit/cockpit-news/' + id + '/', cockpit);
        return this.http.put(environment.api_url + '/api/cockpit/cockpit-news/' + id + '/', cockpit );
    }
    editCockpitNewsById(id: number, cockpit: any) {
        return this.http.put(environment.api_url + '/api/cockpit/cockpit-client/' + id + '/', cockpit );
    }

    getCockpitsById(id: number) {
        return this.http.get(environment.api_url + '/api/cockpit/cockpit-chart/' + id + '/');
    }

    getNewsByCockpit(id: number) {
        return this.http.get(environment.api_url + '/api/cockpit/news/cockpit/' + id + '/');
    }

    getNewsById(id: number) {
        return this.http.get(environment.api_url + '/api/cockpit/news/' + id + '/');
    }

    getNewsCategory() {
        return this.http.get(environment.api_url + '/api/cockpit/category-news/');
    }

    getCategoryName(name: String) {
        return this.http.get(environment.api_url + '/api/cockpit/category-name/?name=' + name);
    }

    putCockpitMarket(cockpitMarket: object) {
        // console.log(environment.api_url + '/api/cockpit/cockpit-market/all/', cockpitMarket);
        return this.http.post(environment.api_url + '/api/cockpit/cockpit-market/all/', cockpitMarket);
    }

    deleteCockpitMarket(id: number) {
        return this.http.delete(environment.api_url + '/api/cockpit/cockpit-market/' + id + '/');

    }

    add_New_ChartMarket(markets: any) {
        return this.http.post(environment.api_url + '/api/cockpit/cockpit-charts/', markets);
    }

    add_to_existent_ChartMarket(id: any, market) {
        console.log(environment.api_url + '/api/cockpit/market-chart/add/' + id + '/', market);
        return this.http.put(environment.api_url + '/api/cockpit/market-chart/add/' + id + '/', market);
    }

    sendNow(id: any) {
        return this.http.put(environment.api_url + '/api/cockpit/cockpit-mail/' + id + '/', {id: id});
    }


    editCockpit(id: any, object: any) {
        return this.http.put(environment.api_url + '/api/cockpit/cockpit-news/' + id + '/', object);
    }

}
