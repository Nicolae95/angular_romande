
import { User } from './../../_models/user';
import { Offer } from './../../_models/offer';
import { CcService } from './../../_services/cc.service';
import { CompanyService } from './../../_services/company.service';
import { Component, OnInit} from '@angular/core';
import { OfferService } from '../../_services/offer.service';
import { FormGroup, FormControl } from '@angular/forms';
import 'rxjs/add/operator/switchMap';
import { ToastrService } from 'ngx-toastr';
import { SearchService, CustomObservable, UserService, FileService } from '../../_services';
import { Pagination } from '../../_models/pagination';
import { Result } from '../../_models/result';
import { Alarm } from '../../_models/alarm';
import { ReloadService } from '../../_services/reload.sevice';
import { environment } from '../../../environments/environment';
import { Router } from '@angular/router';
import { CockpitService } from '../../_services/cockpit.service';


@Component({
  selector: 'app-offercockpit',
  templateUrl: './offercockpit.component.html',
  styleUrls: [
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css',
    // '../../../assets/css/styles/animate.css',
  ]
})

export class OffercockpitComponent implements OnInit {
  offerPagination: Pagination<any>;
  currentUser: User;
  OfferForm: FormGroup;
  nomOffer: FormControl;
  statutOffer: FormControl;
  cockpit: FormControl;
  year: number;
  yearList: number[] = [];
  offers: Array<Offer>;
  term: string;
  pag = 1;
  nr: number;
  show = [false];
  disab = false;
  nameTerm: any;
  ofId: number;
  tabOrInf = false;
  idOffer: any;
  edit = false;
  loadingPush = [false];
  cockpitTypes: any[];
  alarms: Result<Alarm>;
  isEditMode = false;
  selectedCockpitType: number;
  frequence: any;
  loadingSendingEmail = [false];
  loadingEligibilit = [false];
  myFile: File[];
  fileValid = false;
  environment = environment.api_url + '/media/';
  merciId: number;
  loading = false;
  voirYear = [false];
  addmails = false;
  loadingStatus = [false];
  multiple = false;
  days = [];
  primesSettings = {};
  podsSettings = {};
  selectedItems = [];
  selectedList = [];
  ob: any;
  cokOption = [false];
  stop = true;
  ofersOrCockpit = true;

  constructor(private offerService: OfferService,
              private ccService: CcService,
              private searchService: SearchService,
              private customObservable: CustomObservable,
              private reloadService: ReloadService,
              private companyService: CompanyService,
              private router: Router,
              private fileService: FileService,
              private userService: UserService,
              private toastr: ToastrService) {
              this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
              this.nr = this.currentUser.nr;
              this.stop = this.currentUser.alarm;
            }

  ngOnInit() {
    this.yearList.length = 0;
    this.year = new Date().getFullYear();
    for ( let y = 0; y < 4; y++) {this.yearList.push(this.year - y); }

    try {
      this.reloadService.isReloadEditOffer.subscribe((data) => {if (data === true) {
        this.observableSourcenom(this.term);
        this.reloadService.changeEditOffer(false);
      }});
    } catch (error) { console.log(error);
      this.reloadService.changeEditOffer(false);
      this.ngOnInit();
    }

    this.createFormControles();
    this.createForm();
    this.onChangesnom();
    this.getAlarm();

    this.ofId = null;
  }

  editAlarmsWindow(offer: Offer): void {
    this.isEditMode   = false;
    this.ofId         = offer.id;
    this.alarms       = null;
    this.offerService.getCockpitTypes().subscribe(
      (data: any) => {
        this.cockpitTypes = data;
        const hebdomadaire = [];
        hebdomadaire.length = 0;
        this.cockpitTypes.forEach((element) => {
          if (element.id >= 2 && element.id <= 6) {
            hebdomadaire.push(element);
          }
        });
        this.multiSelect(hebdomadaire);
        if (offer['cockpit_data']) {
          if (offer['cockpit_data'][0] === 'Envoi signalé') {
            this.changeCockpitType(this.cockpitTypes[0].id);
          } else  if (offer['cockpit_data'][0] === 'Mensuel (1er jour ouvré du mois)') {
            this.changeCockpitType(this.cockpitTypes[this.cockpitTypes.length - 1].id);
          } else {
            this.changeCockpitType(99);
           }
        } else { this.selectedCockpitType = null; }
       },
      (er) => { console.log(er); }
    );
  }

  editAlarms(): void { this.isEditMode = true; }
  cancelAlarms(): void { this.isEditMode = false; }

  changeCockpitType(tip: any): void {
    this.loading = true;
    this.multiple = false;
    this.selectedCockpitType = tip;
    if (this.selectedCockpitType === 1) {
        this.offerService.getAlarms(this.ofId).subscribe(
          (data) => { this.alarms = data;
            this.alarms.result.forEach(element => {
            if (!element.email) { element.email = this.currentUser.email; }
            });
            this.loading = false;
          },
          (er) => { this.loading = false; this.showError(er.statusText); }
        );
    }
    if (this.selectedCockpitType === 99) { this.multiple = true; }
  }

  saveAlarms(): void {
    if (this.ofId) {

      const arr =  this.selectedCockpitType === 1 ? this.alarms.result : [];
      if (this.selectedCockpitType === 1 || this.selectedCockpitType === 9) {
        this.ob = {
          offer: this.ofId,
          cockpit: [this.selectedCockpitType],
          result: arr
        };
      } else {
        this.selectedList.length = 0;
        this.selectedItems.forEach(element => {
          this.selectedList.push(element.id);
        });
        this.ob = {
          offer: this.ofId,
          cockpit: this.selectedList,
          result: arr
        };
      }

      this.offerService.createAlarms(this.ob, this.ofId).subscribe(
        (data) => { this.alarms = null;
          $('#modalAlarms').click();
          $('body').click();
          this.isEditMode = false;
          this.showSuccess('Les alertes ont été définies.');
          this.observableSourcenom(this.term);
          // setTimeout(() => { here my cod to execut }, 7000);
         },
        (er) => { this.alarms = null; this.showError(er); }
      );

    }
  }

  showSuccess(mesaj: string) { this.toastr.success( mesaj); }
  showError(mesaj: string) { this.toastr.error(mesaj); }

  onChangesnom(): void {
    this.OfferForm.get('nomOffer').valueChanges
    .debounceTime(200)
    .distinctUntilChanged()
    .subscribe(val => {
      this.pag = 1;
      this.observableSourcenom(val);
    });
  }

  observableSourcenom(keyword: string) {
    try {
      this.term = keyword;
      this.searchService.searchNamePagCock(this.term, this.statutOffer.value, this.pag , this.year, this.nr)
      .subscribe (
        (data) => {
          this.offerPagination = data;
          this.returnSplitedYears();
        },
        (er) => { console.log('er', er.error),  this.term = null; },
    );
    } catch (error) {console.log('error', this.term, this.statutOffer.value, this.pag , this.year, this.nr); }

  }


  pags(pag: number) {
    if (pag !== 1) { this.offerPagination = null; }
    this.pag = pag; this.observableSourcenom(this.term);
  }

  setNumberperPag(nr: number) {
    this.nr = Number(nr);
    this.userService.chnageNrPerPag(this.currentUser, nr).subscribe((data) => { this.pags(1); });
  }

  setyear(year) {
    if (this.year === year) {
      this.year = null;
    } else { this.year = year; }
    this.observableSourcenom(this.term);
  }


  createFormControles() {
    this.nomOffer = new FormControl('');
    this.statutOffer = new FormControl('');
    this.cockpit = new FormControl();
  }

  createForm() {
    this.OfferForm = new FormGroup({
      nomOffer: this.nomOffer,
      statutOffer: this.statutOffer,
      cockpit: this.cockpit
    });
  }

  cock(id: number, cock: any) {
    this.disab = true;
    this.offerService.updateCockpit(id, cock).subscribe(
      (data) => { this.disab = false, this.observableSourcenom(this.term); },
      (er) => this.disab = false
    );
  }

  // changeStatus(offer: any, status: string) {
  //   this.offerService.updateStatus(offer.id, status).subscribe(
  //     (data) => { this.observableSourcenom(this.term); },
  //     (er) => {}
  //   );
  // }
  changeStatus(offer: any, status: string, index: number) {
    this.loadingStatus[index] = true;
    this.offerService.updateStatus(offer.id, status, offer.offer_status, this.currentUser.fonction, this.currentUser.id).subscribe(
      (data) => { this.observableSourcenom(this.term);  this.loadingStatus[index] = false; },
      (er) => { this.loadingStatus[index] = false; }
    );
  }


  sendMail(id: number , offer_status: string, y: number) {
    this.loadingPush[y] = true;
    this.offerService.mail(id, offer_status, this.currentUser.id).subscribe(
      (data) => { this.showSuccess('L\'offre a été envoyée'); this.loadingPush[y] = false; this.observableSourcenom(this.term);  },
      (er) => { this.showError('Une erreur est survenue et l\'offre n\'a pas été envoyée.');
                this.loadingPush[y] = false; this.observableSourcenom(this.term); }
    );
  }

  send(offer: Offer) { if (offer) { this.idOffer = offer.id; }}

  editOffer(offer: Offer) {
    this.customObservable.changeEditOffer(null);
    this.customObservable.changeEditOffer(offer);
  }

  getFrecvence() {
    this.offerPagination.result.forEach(element => {
      this.offerService.getFrecvenceByOfert(element.id).subscribe((data) => {
        // console.log(data);
        if (data !== null) {
          if (data.offer = element.id && data.cockpit.name === 'Mensuel') {
              element.frequence = data.cockpit.name;
            }
          if (data.offer = element.id && data.cockpit.name === 'Hebdomadaire') {
            if (data.weekday === 1)  {  element.frequence = 'Lundi';    }
            if (data.weekday === 2)  {  element.frequence = 'Mardi';    }
            if (data.weekday === 3)  {  element.frequence = 'Mercredi'; }
            if (data.weekday === 4)  {  element.frequence = 'Jeudi';    }
            if (data.weekday === 5)  {  element.frequence = 'Vendredi'; }
          }
        }
      },
     (err) => {});
    });

  }

  returnSplitedYears() {
    this.offerPagination.result.forEach(element => {
     const y = String(element.years);
     element.yearsSplits = y.split(',');
    });
  }

  fileEvent(files: File[]) {
    const reader = new FileReader();
    this.myFile = files;

    if (this.myFile == null) { this.fileValid = false;
    } else {  this.fileValid = true;  }
  }
  onSubmit(ofId: number, ind: number) {
    this.merciId = ofId;
    this.loadingSendingEmail[ind] = true;
    const formDataPfc: any = new FormData();
    formDataPfc.append('offerId', ofId);

    if (this.myFile) {
        formDataPfc.append('files', this.myFile[0], this.myFile[0].name);
    } else {
        formDataPfc.append('files', '');
    }

    this.ccService.uploadFileOffer(formDataPfc, 'signed')
    .then(
      res => console.log(res)
    )
    .catch(
      er => {
        // this.loadingSendingEmail[ind] = false;
        this.fileValid = false;
        this.observableSourcenom(this.term);
      }
    )
    .then(
      () => {
              this.loadingSendingEmail[ind] = false;
              this.showSuccess('Le fichier a été téléchargé.');
              this.fileValid = false;
              this.observableSourcenom(this.term);
            }
    );
  }

  onSubmitEligibilit(offerId: number, index: number) {
    this.loadingEligibilit[index] = true;
    const formDataE: any = new FormData();
    formDataE.append('offerId', offerId);

    if (this.myFile) {
        formDataE.append('files', this.myFile[0], this.myFile[0].name);
    } else {
        formDataE.append('files', '');
    }

    this.ccService.uploadFileOffer(formDataE, 'eligibilite')
    .then(
      res => console.log(res)
    )
    .catch(
      er => {
        this.fileValid = false;
        this.observableSourcenom(this.term);
      }
    )
    .then(
      () => {
              this.loadingEligibilit[index] = false;
              this.showSuccess('Le fichier a été téléchargé.');
              this.fileValid = false;
              this.observableSourcenom(this.term);
            }
    );
  }



  getPdf(folder: string, offer: any, nameFile: any) {
    this.fileService.getsFileHeader(folder + '/' + offer.id + '/', 'pdf').subscribe(
      (data) => {this.fileService.downloadUrl(data, nameFile, 'pdf'); },
      (er) => { console.log('er', er); },
    );
  }

  merciBocu() {
    this.loading = true;
    this.offerService.thanksMail(this.merciId).subscribe(
      (data) => { this.showSuccess('L\'email a été envoyé.');  $('#thanksMail').click(); $('body').click();    this.loading = false; }
    );
  }

  goCompany(idCmp: number) {
    this.companyService.getCompanyById(idCmp).subscribe(
      (data) => {
        this.customObservable.changeCompany(data);
        this.router.navigate(['account/offers/', data.id]);
      }
    );
  }

  addMoreMails(offer: Offer) { this.customObservable.changeAddMail(offer); }

  multiSelect(list: any) {
    this.days.length = 0;
    list.forEach(unu => {
      this.days.push({'id' : unu['id'], 'itemName' : unu['name']});
    });

    this.podsSettings = {
      singleSelection: false,
      text: 'Choisir risque',
      selectAllText: 'Tout sélectionner',
      unSelectAllText: 'Tout désélectionner',
      classes: 'myclass custom-class '
    };

    this.primesSettings = {
      singleSelection: false,
      text: 'Veuillez choisir le(s) jour(s) souhaité(s)',
      selectAllText: 'Tout sélectionner',
      unSelectAllText: 'Tout désélectionner',
      classes: 'myclass custom-class '
    };

  }

  cockpitB() {
    this.customObservable.changecockpitB(null);
  }

  getAlarm() { this.offerService.get_alarm_Stop_Star().subscribe((data) => {this.stop = data[0].stop; }); }


}
