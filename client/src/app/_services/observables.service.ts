import { Injectable } from '@angular/core';
import { Offer, Site, Company } from '../_models/index';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { HttpClient } from '@angular/common/http';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';



@Injectable()
export class CustomObservable {
    private site = new BehaviorSubject<any>(null);
    private year = new BehaviorSubject<any>(null);
    private volume = new BehaviorSubject<any>(null);
    private offerObesvable = new BehaviorSubject<Offer>(null);
    private editOffer = new BehaviorSubject<Offer>(null);
    private company = new BehaviorSubject<Company>(null);
    private offerAddMail = new BehaviorSubject<Offer>(null);
    private lissageManual = new BehaviorSubject<any>(null);
    private aneeProposWait = new BehaviorSubject<any>(null);
    private notification = new BehaviorSubject<boolean>(false);
    private cockpitB = new BehaviorSubject<any>(null);
    private showAdmins = new BehaviorSubject<boolean>(false);


    constructor(private http: HttpClient) { }

    get isSite() { return this.site.asObservable(); }
    changeSite(site: Site) { this.site.next(site); }

    get isYear() { return this.year.asObservable(); }
    changeYear(year: any) { this.year.next(year); }

    get isVolume() { return this.volume.asObservable(); }
    changeVolume(volume: any) { this.volume.next(volume); }

    get isEditOffer() { return this.editOffer.asObservable(); }
    changeEditOffer(editOffer: Offer) { this.editOffer.next(editOffer); }

    get isOffer() { return this.offerObesvable.asObservable(); }
     changeOffer(offer: Offer) { this.offerObesvable.next(offer); }

    get isCompany() { return this.company.asObservable(); }
    changeCompany(company: Company) { this.company.next(company); }

    get isAddMail() { return this.offerAddMail.asObservable(); }
    changeAddMail(offer: Offer) { this.offerAddMail.next(offer); }

    get isManualLissage() { return this.lissageManual.asObservable(); }
    changeManualLissage(liss: any) { this.lissageManual.next(liss); }

    get isAneeProposWait() { return this.aneeProposWait.asObservable(); }
    changeAneeProposWait(val: any) { this.aneeProposWait.next(val); }

    get isNotification() { return this.notification.asObservable(); }
    changeNotification(val: any) { this.notification.next(val); }

    get iscockpitB() { return this.cockpitB.asObservable(); }
    changecockpitB(val: any) { this.cockpitB.next(val); }

    get isShowAdmins() { return this.showAdmins.asObservable(); }
    changeShowAdmins(val: any) { this.showAdmins.next(val); }




}

