import { User } from './../../_models/user';
import { Offer } from './../../_models/offer';
import { CcService } from './../../_services/cc.service';
import { CompanyService } from './../../_services/company.service';
import { Component, OnInit, Compiler} from '@angular/core';
import { OfferService } from '../../_services/offer.service';
import { FormGroup, FormControl, Validators} from '@angular/forms';
import 'rxjs/add/operator/switchMap';
import { ToastrService } from 'ngx-toastr';
import { SearchService, CustomObservable, UserService, FileService } from '../../_services';
import { Pagination } from '../../_models/pagination';
import { ReloadService } from '../../_services/reload.sevice';
import { environment } from '../../../environments/environment';
import { Router } from '@angular/router';
import { HttpHeaders, HttpClient } from '@angular/common/http';



@Component({
  selector: 'app-paginationoffer',
  templateUrl: './paginationOffer.component.html',
  styleUrls: []
})

export class PaginationOfferComponent implements OnInit {
  offerPagination: Pagination<any>;
  currentUser: User;
  OfferForm: FormGroup;
  nomOffer: FormControl;
  statutOffer: FormControl;
  cockpit: FormControl;
  cockpitDisabled: FormControl;
  year: number;
  yearList: number[] = [];
  showDropDown = false;
  offers: Array<Offer>;
  term: string;
  termName: string;
  pag = 1;
  show = [false];
  disab = false;
  nameTerm: any;
  tabOrInf = false;
  edit = false;
  idOffer: any;
  showSt = [false];
  loadingPush = [false];
  loadingSendingEmail = [false];
  loadingEligibilit = [false];
  loading = false;
  myFile: File[];
  fileValid = false;
  environment = environment.api_url + '/media/';
  merciId: number;
  loadingStatus = [false];
  voirYear = [false];
  addmails = false;
  smeOffer: Offer;
  loadingSm = false;
  delOff: any;
  nr: number;
  stop = true;
  fileUrl;
  blob;


  constructor(private offerService: OfferService,
              private reloadService: ReloadService,
              private ccService: CcService,
              private customObservable: CustomObservable,
              private toastr: ToastrService,
              private router: Router,
              private fileService: FileService,
              private userService: UserService,
              private searchService: SearchService,
              private companyService: CompanyService,
              private http: HttpClient) {
              this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
              this.nr = this.currentUser.nr;
              this.stop = this.currentUser.alarm;
            }

  ngOnInit() {
    this.getOfferList();
    this.createFormControles();
    this.createForm();
    this.onChangesnom();
    this.getAlarm();

    this.year = new Date().getFullYear();
    for ( let y = 0; y < 4; y++) {  this.yearList.push(this.year - y); }

    this.reloadService.isReloadEditOffer.subscribe(
      (data) => { if (data === true) { this.observableSourcenom(this.term); this.reloadService.changeEditOffer(false); }}
    );
  }


  showSuccess(mesaj: string) { this.toastr.success(mesaj); }
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
    this.term = keyword;
      this.searchService.searchNamePag(keyword, this.statutOffer.value, this.pag , this.year , this.nr)
      .subscribe (
        (data) => {
          this.show = [false];
          this.offerPagination = data;
          this.returnSplitedYears();
          console.log(this.offerPagination);
        },
        (er) => { this.term = null; },
    );
  }

  send(offer: any) { if (offer) {this.idOffer = offer.id; } }
  editOffer(offer: Offer) {  this.customObservable.changeEditOffer(offer); }

  pags(pag: number) {
    if (pag !== 1) {this.offerPagination = null; }
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

  getOfferList() {
    this.offerService.getAll().subscribe((data) => { this.offerPagination = data; });
  }

  createFormControles() {
    this.nomOffer = new FormControl('', Validators.required);
    this.statutOffer = new FormControl('');
    this.cockpit = new FormControl();
    this.cockpitDisabled = new FormControl( {value: '', disabled: true}, Validators.required);
  }

  createForm() {
    this.OfferForm = new FormGroup({
      nomOffer: this.nomOffer,
      statutOffer: this.statutOffer,
      cockpitDisabled: this.cockpitDisabled,
      cockpit: this.cockpit,
    });
  }

  cock(id: number, cock: any) {
    this.disab = true;
    this.offerService.updateCockpit(id, cock).subscribe(
      (data) => this.disab = false,
      (er) => this.disab = false
    );
  }

  changeStatus(offer: any, status: string, index: number) {
    this.loadingStatus[index] = true;
    this.offerService.updateStatus(offer.id, status, offer.offer_status, this.currentUser.fonction, this.currentUser.id).subscribe(
      (data) => {
        this.observableSourcenom(this.term);
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
        this.showSuccess('L\'offre a été envoyée.');
        this.loadingPush[y] = false;
        this.observableSourcenom(this.term);
      },
      (er) => { this.showError('Une erreur est survenue et l\'offre n\'a pas été envoyée.');
                this.loadingPush[y] = false; this.observableSourcenom(this.term); }
    );
  }

  fileEvent(files: File[]) {
    const reader = new FileReader();
    this.myFile = files;
    if (this.myFile == null) {
      this.fileValid = false;
    } else {
      this.fileValid = true;
    }
  }


  onSubmit(ofId: number, ind: number) {
    this.merciId = ofId;
    this.loadingSendingEmail[ind] = true;
    const formDataPdf: any = new FormData();
    formDataPdf.append('offerId', ofId);

    if (this.myFile) {
        formDataPdf.append('files', this.myFile[0], this.myFile[0].name);
    } else {
        formDataPdf.append('files', '');
    }

    this.ccService.uploadFileOffer(formDataPdf, 'signed')
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


  returnSplitedYears() {
    this.offerPagination.result.forEach(element => {
     const y = String(element.years);
     element.yearsSplits = y.split(',');
    });
  }



  getsFileHeader(url: any, headers: any) {
    console.log(environment.api_url + '/api/' + url, { headers: headers, responseType: 'arraybuffer' });
    return this.http.get(environment.api_url + '/api/' + url, { headers: headers, responseType: 'arraybuffer' });
  }

  getPdf(url: string, offer: any, nameFile: any) {
    let headers = new HttpHeaders();
    headers = headers.set('Accept', 'application/' + 'pdf');
    this.getsFileHeader(url + '/' + offer.id + '/?file=' + nameFile.split('/')[1], headers).subscribe(
      (data) => { this.downloadUrl(data, nameFile, 'pdf'); },
      (er) => {  },
    );
  }

  downloadUrl(data: any, filename: string, type: any): void {
    const file = new Blob([data], {type: 'application/' + type });
    const url = URL.createObjectURL(file);
    const hiddenAnchor = document.createElement('a');
    hiddenAnchor.setAttribute('id', filename);
    hiddenAnchor.href = url;
    hiddenAnchor.target = '_blank';
    hiddenAnchor.style.display = 'none';
    if (filename) { (<any>hiddenAnchor).download = filename; }
    document.body.appendChild(hiddenAnchor);
    hiddenAnchor.click();

    setTimeout(function() {
      document.body.removeChild(hiddenAnchor);
      window.URL.revokeObjectURL(url);
      }, 200);
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
        this.router.navigate(['account/offers/', data.id ]);
       },
      (e) => { }
    );
  }

  addMoreMails(offer: Offer) {
    this.customObservable.changeAddMail(offer);
  }

  selSMEOffer(of: Offer) { this.smeOffer = null; this.smeOffer = of; }

  delOf() {
    this.loadingSm = true;
    if (this.delOff.offer_status === 'supprimer') {
      this.offerService.deleteOfferSupprimer(this.delOff.id).subscribe(
        (data) => {
          this.observableSourcenom(this.term);
          $('#delsOff').click(); $('body').click();
          this.toastr.success('L\'offre a été supprimée.');
          this.loadingSm = false; }
      );
    }
  }
  getAlarm() {
    this.offerService.get_alarm_Stop_Star().subscribe((data) => {
      // console.log('data', data);
      this.stop = data[0].stop;

    }); }

}
