
import { User } from './../../_models/user';
import { Company } from './../../_models/company';
import { Offer } from './../../_models/offer';
import { CcService } from './../../_services/cc.service';
import { CompanyService } from './../../_services/company.service';
import { Component, OnInit} from '@angular/core';
import { OfferService } from '../../_services/offer.service';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import 'rxjs/add/operator/switchMap';
import { ToastrService } from 'ngx-toastr';
import { Site } from '../../_models/site';
import { CustomObservable, UserService, FileService } from '../../_services';
import { ReloadService } from '../../_services/reload.sevice';
import { Pagination } from '../../_models/pagination';
import 'rxjs/add/operator/switchMap';
import { environment } from '../../../environments/environment';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-tableoffer',
  templateUrl: './tableoffer.component.html',
  styleUrls: [
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css',
    // '../../../assets/css/styles/animate.css',
  ]
})
export class TableofferComponent implements OnInit {
  currentUser: User;
  siteList: Array<Site>;
  tabOfferForm: FormGroup;
  company: Company;
  ccProfilHistorique: FormControl;
  nameO: FormControl;
  pfc_market: boolean;
  offerPagination: Pagination<any>;
  year: number;
  yearList: number[] = [];
  siteName: string;
  cc: number;
  pods: Offer;
  showDropDown = false;
  nameOf: Offer;
  nameOffer: any;
  offers: Offer[] = [];
  show = [];
  keyword: string;
  // tabOrInf = false;
  idOffer: any;
  pag = 1;
  editOfferId = false;
  cockpit: FormControl;
  cockpitDisabled: FormControl;
  disab = false;
  loadingPush = [false];
  loadingSendingEmail = [false];
  loadingEligibilit = [false];
  myFile: File[];
  fileValid = false;
  environment = environment.api_url + '/media/';
  merciId: number;
  loading = false;
  loadingStatus = [false];
  companyId: number;
  edit = false;
  editSME = false;
  createNewOffer = false;
  addemail = false;
  voirYear = [false];
  goOffert = false;
  stop = true;
  addmails = false;
  smeOffer: Offer;
  nr: number;
  loadingSm = false;
  delOff: any;

  constructor(private ccService: CcService,
              private toastr: ToastrService,
              private offerService: OfferService,
              private reloadService: ReloadService,
              private fileService: FileService,
              private customObservable: CustomObservable,
              private activatedRoute: ActivatedRoute,
              private userService: UserService,
              private companyService: CompanyService) {
              this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
              this.nr = this.currentUser.nr;
              this.stop = this.currentUser.alarm;
              this.activatedRoute.params.subscribe( params =>  { this.companyId = params.id; });
  }

  ngOnInit() {
    this.getAlarm();
    this.createFormControles();
    this.createForm();
    this.setTypeOffer(null);
    this.onChanges();
    this.smeOffer = null;

    if (this.companyId) { this.year = new Date().getFullYear(); for ( let y = 0; y < 4; y++) { this.yearList.push(this.year - y); }

    this.companyService.getCompanyById(this.companyId).subscribe(
      (data) => {
        this.siteList = [];
        this.getCcByCompany(data);
        this.company = data;
      },
      (err) => {
        this.siteList = [];
        this.getCcByCompany(null);
        this.company = null;
      }
    );


    this.reloadService.isReloadEditOffer.subscribe(
      (data) => {
        if (data === true) {
          this.getOffer(this.company.id , '', this.keyword, this.year, this.pag);
          this.getCcByCompany(this.company);
          this.reloadService.changeCC(false);
        }
      }
    );

      this.reloadService.isReloadOffer.subscribe(
          (data) => {
          if (data === true) {
            this.getOffer(this.company.id , '', this.keyword, this.year, this.pag);
            this.getCcByCompany(this.company);
            this.reloadService.changeOffer(false);
            }
          },
          (err) => {}
      );
    }
  }

  onChanges(): void {
    this.tabOfferForm.get('nameO').valueChanges
    .debounceTime(200)
    .distinctUntilChanged()
    .subscribe(val => {
      this.observableSource(val);
    });
  }

  observableSource(keyword: string) {
    this.keyword = keyword;
    this.idOffer = null;
    // this.tabOrInf = false;
    this.send(null);
    this.getOffer(this.company.id , this.cc, keyword, this.year, this.pag);
  }

  voir(id: any) {
    this.idOffer = null;
    this.offerService.getById(id).subscribe(
      (data) => { this.send(data); }
    );
  }
  send(offer: Offer) {
    if (offer) {
      this.idOffer = offer.id;
      this.customObservable.changeOffer(offer);
    } else { this.customObservable.changeOffer(null); }
  }

  editOffer(offer: Offer) {
    this.customObservable.changeEditOffer(null);
    this.customObservable.changeEditOffer(offer);
  }

  getCcByCompany(cmp: Company) {
    if (cmp) {
      this.getOffer(cmp.id, '', '', this.year, this.pag);
      this.ccService.getCcByCompany(cmp.id).subscribe(
        (data) => {
          this.siteList = data;
        },
        (err) => {
          console.log(err);
        }
      );
    }
  }

  setyear(offer: any) { this.year = Number( offer.years.slice(0, 4)); }

  getOffer(id: number, cc: any, siteName: any, year: any, pag: number) {
    this.pag = pag;
    this.nameOffer = siteName;
    // console.log('idOff:', id, 'cc:', cc, 'Name:', siteName, 'year:', year);
    this.year = year;
    this.siteName = siteName;
    this.cc = cc;
    this.offerService.getByCompany(id, cc, siteName, year,  pag, this.nr).subscribe(
      (data) => {
        this.offerPagination = data;
        // this.returnSplitedYears();
      },
      (err) => { console.log(err); }
    );
  }

  setTypeOffer(ptype: boolean) {
    this.pfc_market = ptype;
  }

  createFormControles() {
    this.ccProfilHistorique = new FormControl('');
    this.nameO = new FormControl('');
    this.cockpit = new FormControl('');
    this.cockpitDisabled = new FormControl( {value: '', disabled: true}, Validators.required);

  }

  createForm() {
    this.tabOfferForm = new FormGroup({
      ccProfilHistorique: this.ccProfilHistorique,
      nameO: this.nameO,
      cockpit: this.cockpit,
      cockpitDisabled: this.cockpitDisabled

    });
  }
  closeDropDown() { this.showDropDown = false; }
  openDropDown() { this.showDropDown = true; }

  changeStatus(offer: any, status: string, index: number) {
    this.loadingStatus[index] = true;
    this.offerService.updateStatus(offer.id, status, offer.offer_status, this.currentUser.fonction, this.currentUser.id).subscribe(
      (data) => {
        this.observableSource(this.keyword);
        this.loadingStatus[index] = false;
        if (offer.offer_status === 'confirmer') {
          this.toastr.success('L\'offre pour ' + offer.entreprise + ' a été confirmée par ' +
           this.currentUser.firstName + ' ' + this.currentUser.lastName);
          }
      },
      (er) => { this.loadingStatus[index] = false; }
    );
  }

  sendMail(id: number , offer_status: string, y: number) {
    this.loadingPush[y] = true;
    this.offerService.mail(id, offer_status, this.currentUser.id).subscribe(
      (data) => {
        this.showSuccess();
        this.loadingPush[y] = false;
        this.observableSource(this.keyword);
      },
      (er) => { this.showError(); this.loadingPush[y] = false; this.observableSource(this.keyword); }
    );

  }

  pags(pag) {
    if (pag !== 1) { this.offerPagination = null; }
    this.pag = pag;
    this.observableSource(this.keyword);
  }

  setNumberperPag(nr: number) {
    this.nr = Number(nr);
    this.userService.chnageNrPerPag(this.currentUser, nr).subscribe((data) => { this.pags(1); });
  }


  cock(id: number, cock: any) {
    this.disab = true;
    this.offerService.updateCockpit(id, cock).subscribe(
      (data) => this.disab = false,
      (er) => this.disab = false
    );
  }

  showSuccess() { this.toastr.success('L\'offre a été envoyée'); }
  showError() {this.toastr.error('Une erreur est survenue et l\'offre n\'a pas été envoyée.'); }

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
      res => {},
    )
    .catch(
      er => {
        // this.loadingSendingEmail[ind] = false;
        this.fileValid = false;
        this.observableSource(this.keyword);
      }
    )
    .then(
      () => {
              this.loadingSendingEmail[ind] = false;
              this.toastr.success('Le fichier a été téléchargé.');
              this.fileValid = false;
              this.observableSource(this.keyword);
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
      res => {},
    )
    .catch(
      er => {
        this.fileValid = false;
        this.observableSource(this.keyword);
      }
    )
    .then(
      () => {
              this.loadingEligibilit[index] = false;
              this.toastr.success('Le fichier a été téléchargé.');
              this.fileValid = false;
              this.observableSource(this.keyword);
            }
    );
  }


  // returnSplitedYears() {
  //   this.offerPagination.result.forEach(element => {
  //    const y = String(element.years);
  //    element.yearsSplits = y.split(',');
  //   });
  // }

  fileEvent(files: File[]) {
    this.myFile = files;
    if (this.myFile == null) {
      this.fileValid = false;
    } else {
      this.fileValid = true;
    }
  }


  getPdf(folder: string, offer: any, nameFile: any) {
    this.fileService.getsFileHeader(folder + '/' + offer.id + '/', 'pdf').subscribe(
      (data) => {this.fileService.downloadUrl(data, nameFile, 'pdf'); },
      (er) => { },
    );
  }

  merciBocu() {
    this.loading = true;
    this.offerService.thanksMail(this.merciId).subscribe(
      (data) => {  this.toastr.success('L\'email a été envoyé.');  $('#thanksMail').click(); $('body').click();    this.loading = false; },
      (e) => { }
    );
  }


  addMoreMails(offer: Offer) {
    this.customObservable.changeAddMail(offer);
  }

  selSMEOffer(of: Offer) {
    this.smeOffer = null;
    this.smeOffer = of;
  }

  delOf() {
    this.loadingSm = true;
    if (this.delOff.offer_status === 'supprimer') {
      this.offerService.deleteOfferSupprimer(this.delOff.id).subscribe(
        (data) => {
          this.observableSource(this.keyword);
          $('#delsOff').click(); $('body').click();
          this.toastr.success('L\'offre a été supprimée.');
          this.loadingSm = false; }
      );
    }
  }
  getAlarm() { this.offerService.get_alarm_Stop_Star().subscribe((data) => {
    this.stop = data[0].stop;
    console.log(data[0].stop);
  }); }

}
