import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { HttpClient } from '@angular/common/http';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';



@Injectable()
export class ReloadService {
    private reloadOffer = new BehaviorSubject<boolean>(false);
    private reloadCC = new BehaviorSubject<boolean>(false);
    private reloadPfc = new BehaviorSubject<boolean>(false);
    private reloadEditOffer = new BehaviorSubject<boolean>(false);
    private reloadClient = new BehaviorSubject<boolean>(false);
    private reloadEditCurentUser = new BehaviorSubject<boolean>(false);
    private reloadCockpits = new BehaviorSubject<boolean>(false);

    constructor(private http: HttpClient) { }

    get isReloadOffer() { return this.reloadOffer.asObservable(); }
    changeOffer(reload: any) { this.reloadOffer.next(reload); }

    get isReloadCC() { return this.reloadCC.asObservable(); }
    changeCC(reload: any) { this.reloadCC.next(reload); }

    get isReloadPfc() { return this.reloadPfc.asObservable(); }
    changePfc(reload: any) { this.reloadPfc.next(reload); }

    get isReloadEditOffer() { return this.reloadEditOffer.asObservable(); }
    changeEditOffer(reload: any) { this.reloadEditOffer.next(reload); }

    get isReloadClient() { return this.reloadClient.asObservable(); }
    changeReloadClient(reload: any) { this.reloadClient.next(reload); }

    get isReloadEditCurentUser() { return this.reloadEditCurentUser.asObservable(); }
    changeEditCurentUser(reload: any) { this.reloadEditCurentUser.next(reload); }

    get isReloadreloadCockpits() { return this.reloadCockpits.asObservable(); }
    changereloadCockpits(reload: any) { this.reloadCockpits.next(reload); }






}
