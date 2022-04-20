import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Offer, Constants, User } from '../_models/index';
import { Pagination } from '../_models/pagination';
import { Result } from '../_models/result';
import { Alarm } from '../_models/alarm';


@Injectable()
export class OfferService {
    constructor(private http: HttpClient) {  }


    getAll() {
        return this.http.get<Pagination<Offer>>(environment.api_url + '/api/offer/list/');
    }

    getById(id: number) {
        return this.http.get<Offer>(environment.api_url + '/api/offer/id/' + id + '/');
    }

    getByCompany(id: number, cc: number, name: string, year: string, pag: number, nr: any) {
        if (cc) {
            return this.http.get<Pagination<Offer>>(environment.api_url + '/api/offer/company/' + id +
            '/?cc=' + cc + '&name=' + name + '&year=' + year + '&pag=' + pag + '&nr=' + Number(nr));
        } else {
            return this.http.get<Pagination<Offer>>(environment.api_url + '/api/offer/company/' + id +
            '/?name=' + name + '&year=' + year + '&pag=' + pag + '&nr=' + Number(nr));
        }
    }

    getOfferList(id: number, cockpit: string) {
        return this.http.get<Offer[]>(environment.api_url + '/api/offer/company-list/' + id + '/?cockpit=' + cockpit);
    }

    getPods(offerId: number) {
        return this.http.get<Offer>(environment.api_url + '/api/pods/site/' + 262 + '/');
    }

    updateCockpit(id: number, cockpit: boolean) {
        return this.http.put(environment.api_url + '/api/offer/cockpit/' + id + '/', {'cockpit': cockpit});
    }

    updateStatus(id: number, status: string, statusDo: any, userFunc: any, userId: number) {
        return this.http.put(environment.api_url + '/api/offer/status/' + id + '/',
        {'offer_status': status, 'fonction': userFunc, 'id': userId, 'statusDo': statusDo});
    }

    mail(id: number, status: string, userId: number) {
        if (status === 'signer') {
            return this.http.post(environment.api_url +
                '/api/offer/mail-pdf/' + id + '/', {'id': id, 'status': status, 'userId': userId});
        } else {
            return this.http.post(environment.api_url +
                '/api/offer/mail/' + id + '/', {'id': id, 'status': status, 'userId': userId});
        }
    }

    update(offer: Offer) {
        return this.http.put(environment.api_url + '/api/offer/id/' + offer.id + '/', offer);
    }

    create(offer: Offer) {
        return this.http.post(environment.api_url + '/api/offer/list/', offer);
    }

    getBudget(id: number) {
        return this.http.get<any>(environment.api_url + '/api/budget/data/' + id + '/');
    }

    getAllCockpit() {
        return this.http.get<Pagination<Offer>>(environment.api_url + '/api/offer/cockpit/list/');
    }

    editOffer(id: number, obj: any) {
        console.log(environment.api_url + '/api/offer/id/' + id + '/', obj);
        return this.http.put(environment.api_url + '/api/offer/id/' + id + '/', obj);
    }

    editSMEOffer(id: number, of: Offer) {
        return this.http.put(environment.api_url + '/api/offer/id/' + id + '/', of);
    }

    getAlarms(id: number) {
        return this.http.get<Result<Alarm>>(environment.api_url + '/api/offer/pfcs/' + id + '/');
    }

    getCockpitTypes() {
        return this.http.get(environment.api_url + '/api/cockpit/list/');
    }

    createAlarms(offer: any, id: number) {
        return this.http.post(environment.api_url + '/api/offer/pfcs/' + id + '/', offer);
    }

    getConstants() {
        return this.http.get<Constants[]>(environment.api_url + '/api/offer/constants/');
    }

    putConstants(marjes: any) {
        return this.http.put(environment.api_url + '/api/offer/constants/', marjes);
    }


    getYearBySite(id: number) {
        return this.http.get(environment.api_url + '/api/company/years/' +  id + '/');
    }

    getFrecvenceByOfert(id: number) {
        return this.http.get<any>(environment.api_url + '/api/cockpit/offer/' + id + '/');
    }

    thanksMail(id: number) {
        return this.http.post(environment.api_url + '/api/offer/mail-thanks/' + id + '/' , {'id': id});
    }

    getBudgetHistory(id: number) {
        return this.http.get<any>(environment.api_url + '/api/budget/history/' + id + '/');
    }

    getEcoEnergy(pfc_id: number, energy: string) {
        return this.http.get<any>(environment.api_url + '/api/offer/energy/?pfc=' + pfc_id + '&code=' + energy + '&market=' + false);
    }

    getEcoEnergyMarket(pfc_id: number, energy: string) {
        return this.http.get<any>(environment.api_url + '/api/offer/energy/?pfc=' + pfc_id + '&code=' + energy + '&market=' + true);
    }
    getGrds() {
        return this.http.get<any>(environment.api_url + '/api/offer/grds/');
    }

    get_alarm_Stop_Star() {
        return this.http.get<any>(environment.api_url + '/api/offer/stop/');
    }

    put_alarm_Stop_Star(user: User, alarm: boolean) {
        const toStory = {
            'id': user.id,
            'username': user.username,
            'firstName': user.firstName,
            'lastName':  user.lastName,
            'email': user.email,
            'role': user.role,
            'fonction': user.fonction,
            'alarm': alarm,
            'nr': user.nr,
          };
        localStorage.removeItem('currentUser');
        localStorage.setItem('currentUser', JSON.stringify(toStory));
        return this.http.put<any>(environment.api_url + '/api/offer/stop/', { id: 1, stop: alarm});
    }

    insertMails(emails: any, id: number) {
        return this.http.post(environment.api_url + '/api/offer/emails/' , {'email': emails, 'id': id} );
    }

    getVolumes(id: number) {
        return this.http.get<any>(environment.api_url + '/api/cc/volumes/' + id + '/');
    }

    Mailfunction(id: number) {
        return this.http.post<any>(environment.api_url + '/api/offer/mail-function/' + id + '/' , {'id': id});
    }

    manualOffer(offerManual: any) {
        return this.http.post(environment.api_url + '/api/budget/lissage/' , {'offer': offerManual} );
    }

    deleteOfferSupprimer(id: number) {
        return this.http.delete(environment.api_url + '/api/offer/id/' + id + '/');
    }

    getParameters(id: number) {
        return this.http.get<any>(environment.api_url + '/api/offer/parameters/' + id + '/');
    }

    postOfferSendSmeMail(id: number) {
        return this.http.post(environment.api_url + '/api/offer/mail-sme/' + id + '/', {'id': id});
    }

}

