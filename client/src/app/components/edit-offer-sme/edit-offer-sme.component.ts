import { Component, OnInit, Input, OnChanges } from '@angular/core';
import { PfcService, CcService } from '../../_services';
import { ToastrService } from 'ngx-toastr';
import { Offer, User, Pfc } from '../../_models';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { OfferService } from '../../_services/offer.service';
import { ReloadService } from '../../_services/reload.sevice';
import * as moment from 'moment';
import { environment } from '../../../environments/environment';


@Component({
  selector: 'app-edit-offer-sme',
  templateUrl: './edit-offer-sme.component.html',
  styleUrls: [
  //   '../../../assets/css/styles/nexus.css',
  // '../../../assets/css/styles/layout.css',
  // '../../../assets/css/styles/theme.css',
  // '../../../assets/css/styles/animate.css'
]
})

export class EditOfferSmeComponent implements OnInit, OnChanges {
  @Input() offer: Offer;
  myFile: File[];
  fileValid = false;
  loading = false;
  showBottomTable = false;
  btnName = 'Choisir le fichier';
  currentUser: User;
  selectedYears: string[];
  listdureeVaneur = [];

  OfferForm: FormGroup;
  effortsF: FormControl; //  efforts = {};
  energy_type: FormControl;
  sur_goF: FormControl; // sur_go = {};
  totalEcoF: FormControl;  totalEco = [];
  ps1F: FormControl; // ps1 = {};
  ps2F: FormControl; //  ps2 = {};
  majorsF: FormControl;   majors = {};
  minim: FormControl;
  maxim: FormControl;
  energies = {};
  listEcos: any;
  currentPfc: any;
  duree: any;
  mesajErros = false;  mesajErrosF: FormControl;
  margesMin: number;
  margesMax: number;
  lisageMax: number;
  lisageMaxFormC: FormControl;
  marges: any;
  dureeVaneurF: FormControl;
  dureeVaneur: number;
  putCons = false;
  sitevolume: number;
  sitename: string;
  grd: string;
  currentDate: any;
  loadingUP = false;
  hideModal = false;
  result: any;
  parameters: any;
  environment = environment.api_url + '/media/';
  loadingMail = false;

  constructor(private pfcService: PfcService,
              private toastr: ToastrService,
              private reloadService: ReloadService,
              private offerService: OfferService,
              private ccService: CcService) {
              this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
  }

  ngOnChanges() {
    console.log('edit-offer-sme', this.offer.id);
    const yrs = String(this.offer.years);
    this.selectedYears = yrs.split(',');
    // this.getDatesDiff();
    this.duree = moment.duration(this.offer.duree, 'seconds');
    this.getVolume(this.offer.cc);
    this.getGRD(this.offer.grd);
    this.getParameters(this.offer.id);
    this.createForm();
    // this.showBottomTable = true;
  }

  ngOnInit() {
    const date = new Date();
    this.currentDate = { date: { year: date.getFullYear(), month: date.getUTCMonth() + 1, day: date.getUTCDate() } };
  }


  createForm() {
    this.effortsF = new FormControl(0, Validators.required);
    this.majorsF = new FormControl(0, Validators.required);
    this.sur_goF = new FormControl(0, Validators.required);
    this.totalEcoF = new FormControl('');
    this.ps1F = new FormControl(0, Validators.required);
    this.ps2F = new FormControl(0, Validators.required);
    this.minim = new FormControl(''); //  ''
    this.maxim = new FormControl(''); //  ''
    this.energy_type = new FormControl({value: '', disabled: true});

    this.OfferForm = new FormGroup({
      minim: this.minim,
      maxim: this.maxim,
      effortsF: this.effortsF,
      majorsF: this.majorsF,
      ps1F: this.ps1F,
      ps2F: this.ps2F,
      sur_goF: this.sur_goF,
      totalEcoF: this.totalEcoF,
      energy_type: this.energy_type
   });
  }

  fileEvent(files: File[]) {
    this.myFile   = files;
    if (this.myFile == null) { this.fileValid = false; } else { this.fileValid = true; }
  }

  onSubmit() {
    this.loading = true;
    const formDataExcel: any = new FormData();
    formDataExcel.append('pfc_market', true);

    if (this.myFile) { formDataExcel.append('files', this.myFile[0], this.myFile[0].name);
    } else { formDataExcel.append('files', ''); }
      // formDataExcel.append('date', 'this.currentDate');

    this.pfcService.uploadPFC(formDataExcel).then(
      (res: string) => {
        this.currentPfc = JSON.parse(res);
        this.OfferForm.get('energy_type').setValue(this.offer.energy_type);
        this.getEcoEnergy(this.offer.energy_type);
        this.showBottomTable = true;
        this.loading = false;
        this.getConstants();
      }
    ).catch(
      er => {this.fileValid = false; }
    );
  }

  getEcoEnergy(energy: string) {
    // this.onChangesSurGo();

    if (this.currentPfc.pfc) {
      this.listEcos = null;
      this.offerService.getEcoEnergyMarket(this.currentPfc.pfc, energy).subscribe(
        (data) => {
          this.listEcos = data;
          this.calculateTotal(this.listEcos);
        },
      );
    }
  }

  offerSendSmeMail () {
    this.loadingMail = true;
    this.offerService.postOfferSendSmeMail(this.offer.id).subscribe(data => {
      this.toastr.success('L\'email a été envoyé.'); this.loadingMail = false; });
  }


  calculateTotal(datacalculate: any) {
      if (datacalculate && this.selectedYears.length !== 0) {
          this.parameters.parameters.forEach(element => {
              datacalculate.forEach(y => {
                if ( element.parameter__code === 'sur_go' && Number(element.year) === Number(y.year)) {
                  // this.energies[element] = y.value;
                  this.totalEco.push( {year: element.year , value: element.value + y.value});
                }
                // console.log('totalEco.', this.totalEco);
              });
           });
        }
  }

  onSubmitOffer(data: any) {
    this.loadingUP = true;
    const offer: Offer = new Offer;
    // offer.energy_type = data['energy_type'];

    // offer.pfc_market = this.currentPfc.pfc;
    offer.pfc_market = null;
    offer.pfc = null;
    offer.user = this.currentUser.id;
    // offer.efforts = this.efforts;
    // offer.sur_go = this.sur_go;
    // offer.majors = this.majors;
    // offer.ps1 = this.ps1;
    // offer.ps2 = this.ps2;


    this.offerService.editSMEOffer(this.offer.id, offer).subscribe(
      (res) => {
        this.loadingUP = false;
         this.result = res;
        this.showSuccess('Une offre SME pour ' + this.offer.entreprise + ' ' +  this.offer.contact + ' a été créée');
        if (this.result.fonction === 3) { $('#editSME').click();  $('body').click(); this.reloadService.changeEditOffer(true); }
        if (this.result.fonction !== 3) { this.hideModal = true; }
      },
      (err) => {
        this.loadingUP = false;
        this.toastr.error(err.name);
        $('#editSME').click();
        $('body').click();
      }
    );
  }

  showSuccess(mesaj: string) { this.toastr.success(mesaj); }

  getDatesDiff(): void {
    const dateF = this.offer.date_fin;
    const dateD = this.offer.date_debut;
    const diff = moment.duration(moment(dateF).diff(moment(dateD)));
    const days = Math.floor(diff.asDays());
    let hours = Math.floor(diff.asHours());
    hours = hours - days * 24;
    let minutes = Math.floor(diff.asMinutes());
    minutes = minutes - (days * 24 * 60 + hours * 60);
    this.duree = days + 'd ' + minutes + 'm';
  }


  getConstants() {
    this.listdureeVaneur = [];
    this.offerService.getConstants().subscribe(
      (data) => { this.marges = data;
        data.forEach(element => {
          if (element.name === 'Lissage')    { this.lisageMax = element.value;   }
          if (element.name === 'Marges Min') { this.margesMin = element.value; }
          if (element.name === 'Marges Max') { this.margesMax = element.value; }
          if (element.name === 'Duree')      { this.dureeVaneur = element.value; }
        });
        for (let index = 1; index <= this.dureeVaneur; index++) {
          this.listdureeVaneur.push( index );
        }
          },
      (e) => {}
    );
    this.onChangesMax();
    this.onChangesMin();
    this.onChangesMarjes();
  }

  onChangesMax(): void {
    this.OfferForm.get('maxim').valueChanges
    .debounceTime(100)
    .distinctUntilChanged()
    .subscribe(mx => {
      this.observableMax(mx);
    });
  }
  observableMax(mx: number) {
    this.margesMax = mx;
    this.putConstants();
    this.observableMarjes('');
  }

  onChangesMin(): void {
    this.OfferForm.get('minim').valueChanges
    .debounceTime(100)
    .distinctUntilChanged()
    .subscribe(mn => {
      this.observableMin(mn);
    });
  }
  observableMin(mn: number) {
    this.margesMin = mn;
    this.putConstants();
    this.observableMarjes('');
  }

  onChangesMarjes(): void {
    this.OfferForm.get('majorsF').valueChanges
    .debounceTime(100)
    .distinctUntilChanged()
    .subscribe(val => {
      this.observableMarjes(val);
    });
  }

  observableMarjes(val: any) {
    if (this.mesajErros = true) { this.mesajErros = false; }
    if (this.selectedYears) {
      for (const key in this.majors) {
        if (this.majors.hasOwnProperty(key)) {
          const element = this.majors[key];
          if (element > this.margesMax || element < this.margesMin || this.margesMin > this.margesMax) {
            this.mesajErros = true;
          }
        }
      }
    }
  }

putConstants() {
    if (this.marges) {
      this.putCons = false;
      this.marges.forEach(element => {
        if (element.name === 'Lissage'    && element.value !== this.lisageMax)   { element.value = this.lisageMax;   this.putCons = true; }
        if (element.name === 'Marges Min' && element.value !== this.margesMin)   { element.value = this.margesMin;   this.putCons = true; }
        if (element.name === 'Marges Max' && element.value !== this.margesMax)   { element.value = this.margesMax;   this.putCons = true; }
        if (element.name === 'Duree'      && element.value !== this.dureeVaneur) { element.value = this.dureeVaneur; this.putCons = true; }
    });
      if (this.putCons) { this.offerService.putConstants(this.marges).subscribe((data) => {}, (e) => {} ); }
    }
  }

  getVolume(id: number) {
    // this.volumeId = id;
    if (id) {
      this.ccService.getSiteData(id).subscribe(
        (data) => {
          this.sitevolume = data['total_value'];
          this.sitename = data['site'];
      });
    }
  }

  getGRD(id: number) {
    // this.volumeId = id;
    if (id) {
      this.ccService.getGRD(id).subscribe(
        (data) => {
          this.grd = data['name'];
      });
    }
  }

  close() {  $('#editSME').click();  $('body').click(); }

  mailfunction() {
    this.loading = true;
    this.offerService.Mailfunction(this.result.id).subscribe(
      (data) => {
          this.close();
          this.toastr.success('L\'email a été envoyé.');
          this.loading = false;
          this.hideModal = false;
          this.reloadService.changeCC(false);
          this.reloadService.changeEditOffer(true);
      },
        (er) => { this.hideModal = false; this.loading = false; this.toastr.error(er.name);
          this.reloadService.changeEditOffer(true); this.reloadService.changeOffer(true); },
    );
  }

  getParameters(id: number) {
    this.offerService.getParameters(id).subscribe((data) => { this.parameters = data; } );
  }
  exempleFile(fileName: string) {
    if (fileName) {
      window.open(this.environment + 'demo/' + fileName);
      this.showSuccess('Fichier a été téléchargé');
    }
}
}
