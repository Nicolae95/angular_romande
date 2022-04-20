import { Risc } from './../../_models/risc';
import { User } from './../../_models/user';
import { Company } from './../../_models/company';
import { Offer } from './../../_models/offer';
import { CcService } from './../../_services/cc.service';
import { Component, OnInit } from '@angular/core';
import { OfferService } from '../../_services/offer.service';
import { FormGroup, FormControl, Validators} from '@angular/forms';
import * as moment from 'moment';
import 'rxjs/add/operator/switchMap';
import { ToastrService } from 'ngx-toastr';
import { INgxMyDpOptions, IMyDateModel} from 'ngx-mydatepicker';
import { Site } from '../../_models/site';
import { PfcService, RiscService, SearchService, CustomObservable } from '../../_services';
import { Pfc } from '../../_models';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import { ReloadService } from '../../_services/reload.sevice';
const PADDING = '000000';

@Component({
  selector: 'app-offer',
  templateUrl: './offer.component.html',
  styleUrls: []
})

export class OfferComponent implements OnInit {
    year: number;
    IdClient: number;
    pfcType: string;
    OfferForm: FormGroup;
    clientId: FormControl;
    vandeurId: FormControl;
    typeOffer: FormControl;
    prixHpHc: FormControl;
    hphc: FormControl;
    nomOffer: FormControl;
    nomEntreprice: FormControl;
    nr_opportunite: FormControl;
    comment: FormControl;
    marche: FormControl;
    releve: FormControl;
    grd: FormControl;
    ccProfilHistorique: FormControl;
    volumeAnnuelTotal: FormControl;
    anneesProposees: FormControl;
    anneeIn: FormControl;
    anneeFin: FormControl;
    anneeInForce: FormControl;
    anneeFinForce: FormControl;
    parametres: FormControl;
    datePFC: FormControl;
    pfc: FormControl;
    companyf: FormControl;
    type: FormControl;
    validation_time: FormControl;
    unit: FormControl;
    lissage: FormControl;
    decote: FormControl;
    taux: FormControl;
    minim: FormControl;
    maxim: FormControl;
    max_volume_cc: FormControl;
    siteList: Array<Site>;
    yearList = [];
    yearListDoForce = [];
    yearListForce = [];
    selectedYears = [];
    selectedYearsForce = [];
    selectedYearsLisage = [];
    yearSettings = {};
    primesList = [];
    primesSettings = {};
    selectedPrimes = [];
    currentDate: any;
    currentFin: any;
    currentDebut: any;
    pfcRecordFirst: any;
    pfcRecordLast: any;
    pfcRecordFirstF: FormControl;
    pfcRecordLastF: FormControl;
    company: Company;
    currentUser: User;
    currentPfc: Pfc;
    units: any;
    existsPfc = false;
    existsLissage = false;
    existsLissageManual = false;
    loading = false;
    enmData = [];
    show = false;
    init = false;
    decotesF: FormControl;  decotes = {};
    effortsF: FormControl; efforts = {};
    energiesF: FormControl; energies = {};
    majorsF: FormControl; majors = {};
    ps1F: FormControl; ps1 = {};
    ps2F: FormControl; ps2 = {};
    sur_goF: FormControl; sur_go = {};
    totalEcoF: FormControl; totalEco = {};
    volumeId: number;
    myVolume: any;
    showhphc = true;
    lisages = {};
    percent = 20;
    volCond = false;
    yearsMore4 = false;
    betweenYears = false;
    anInFin = false;
    next4year = [];
    margesMin: number;
    margesMax: number;
    lisageMax: number;
    lisageMaxFormC: FormControl;
    energy_type: FormControl;
    marges: any;
    temporarMonth: any;
    mesajErros = false;  mesajErrosF: FormControl;
    date_debut: FormControl;
    heures_in: FormControl;
    date_fin: FormControl;
    heures_fin: FormControl;
    durre: FormControl;
    grds: any;
    dureeVaneurF: FormControl;
    dureeVaneur: number;
    maxVolumeCc: any;
    listdureeVaneur = [];
    curentTime: any;
    durreNmodel: any = '00:00:00';
    ms: any;
    durations: any;
    inMaxFin = false;
    dateDif: any;
    durataInZile: any;
    putCons = false;
    offer_status: FormControl;
    showDropDown = false;
    vendeures: any;
    vedeurName = '';
    vendeur: any;
    conseiller: FormControl;
    userToSend: number;
    initDisabTypeOffer = true;
    listEcos: any;
    dd: any;
    hh: any;
    mm: any;
    key: any;
    atentionPFC = false;
    hideModal = false;
    result: any;
    forces = false;
    curentSite: any;
    pfcs: any;
    aneeProposWait = false;
    loadPFC = false;
    majorationsVerify = false;
    maxVolume: any;
    disablisMan = false;
    one_veryfi_popup = true;
    pfcRecorder: any;
    invalidPeriod = false;

    myOptions: INgxMyDpOptions = {
      dateFormat: 'dd.mm.yyyy',
      disableWeekends: true,
      enableDates: this.enmData,
      disableDateRanges: [{begin: {year: 2008, month: 11, day: 14}, end: {year: 2028, month: 11, day: 20}}]
    };

    dateOptionsSME: INgxMyDpOptions = { dateFormat: 'dd.mm.yyyy', disableWeekends: false };
    datePfcsOptions: INgxMyDpOptions = { dateFormat: 'dd.mm.yyyy', disableWeekends: false };


    private DECIMAL_SEPARATOR: string;
    private THOUSANDS_SEPARATOR: string;

    transform(value: number | string, fractionSize: number = 2): string {
      let [ integer, fraction = '' ] = (value || '').toString()
        .split(this.DECIMAL_SEPARATOR);

      fraction = fractionSize > 0
        ? this.DECIMAL_SEPARATOR + (fraction + PADDING).substring(0, fractionSize)
        : '';
      integer = integer.replace(/\B(?=(\d{3})+(?!\d))/g, this.THOUSANDS_SEPARATOR);
      return integer + fraction;
    }

    parse(value: string, fractionSize: number = 2): string {
      let [ integer, fraction = '' ] = (value || '').split(this.DECIMAL_SEPARATOR);

      integer = integer.replace(new RegExp(this.THOUSANDS_SEPARATOR, 'g'), '');

      fraction = parseInt(fraction, 10) > 0 && fractionSize > 0
        ? this.DECIMAL_SEPARATOR + (fraction + PADDING).substring(0, fractionSize)
        : '';

      return integer + fraction;
    }

    constructor(private ccService: CcService,
                private pfcService: PfcService,
                private offerService: OfferService,
                private toastr: ToastrService,
                private reloadService: ReloadService,
                private searchService: SearchService,
                private customObservable: CustomObservable,
                private riscService: RiscService) {
                this.DECIMAL_SEPARATOR = '.';
                this.THOUSANDS_SEPARATOR = '\'';
                this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
     }

    ngOnInit() {
      const date =  new Date();
      this.currentFin = { date: { year: date.getFullYear(), month: date.getUTCMonth() + 1, day:  date.getUTCDate() } };
      this.currentDebut =  { date: { year: date.getFullYear(), month: date.getUTCMonth() + 1, day:  date.getUTCDate()} };
      const dates =  { year: date.getFullYear(), month: date.getUTCMonth(), day:  date.getUTCDate()};
      this.currentFin.formatted   =  moment(date).format('DD.MM.YYYY');
      this.currentDebut.formatted =  moment(dates).format('DD.MM.YYYY');

      this.pfcRecordFirst = '';
       this.pfcRecordLast = '';
      this.curentTime = new Date();
      this.year = new Date().getFullYear();

      this.createFormControles();
      this.createForm();
      // this.getUnits();
      this.getRiscs();
      this.onChangesTaux();
      this.onChangesMax_Volume_cc();
      this.onChangesPercent();
      this.getGrds();
      this.onChangesDureeVandior();

      this.ccService.isCompany.subscribe(
        (data) => { this.getCcByCompany(data); this.company = data; },
        (err) => {  this.getCcByCompany(null); this.company = null; }
      );
      this.setTypeOffer(null);
      this.getConstants();
      this.onChangesHeuresFin();
      this.onChangesHeureIn();
      this.onChangesVendeur();
      this.OfferForm.get('vandeurId').setValue( this.currentUser.lastName + ' ' + this.currentUser.firstName );
      this.vedeurName = this.currentUser.lastName + ' ' + this.currentUser.firstName;
      this.defaultValue();
      if ( this.currentUser.role === 1) { this.onChangesDateIn(); this.onChangesDateFin(); }


      this.customObservable.isAneeProposWait.subscribe(
        (data) => {
          if (data === true) {
            if ( Number(this.anneeFinForce.value) === this.yearList[this.yearList.length - 1] ) {
              this.OfferForm.get('anneeFin').setValue(this.yearList[this.yearList.length - 1]);
              this.observableAnneeFin(this.yearList[this.yearList.length - 1]);
             } else {
               const an = Number(this.anneeFinForce.value);
               this.yearList.forEach((element, index) => {
                          // console.log('anneeFin:', element, an , this.yearList[this.yearList.length - 1]);
                        if (element === an  && an !== this.yearList[this.yearList.length - 1] ) {
                              this.OfferForm.get('anneeFin').setValue( this.yearList[index + 2]);
                          }
                      });
                    }
                    this.getYearsBySite(this.ccProfilHistorique.value);
                    this.getVolume(this.ccProfilHistorique.value);
            this.OfferForm.get('anneeIn').setValue(this.anneeInForce.value);
            this.observableAnneeIn(this.anneeInForce.value);
            this.customObservable.changeAneeProposWait(false);
            this.aneeProposWait = true;

          }
        }
      );
    }


    getPfcInitialByday() {
      this.existsPfc = null;
      this.currentPfc = null;
      if ( this.pfcType === 'Standart' ) {
      this.OfferForm.get('offer_status').setValue('indicative');


      this.currentDate = { date: {
        year:  Number(this.pfcs[0].pfc_id.slice(6, 10)),
        month: Number(this.pfcs[0].pfc_id.slice(3, 5)),
        day:   Number(this.pfcs[0].pfc_id.slice(0, 2)) } };
          this.pfcService.getByDate(this.pfcs[0].pfc_id).subscribe(
            (data) => {
              this.currentPfc = data;
              this.existsPfc = true;
              this.initDisabTypeOffer = false;
              // this.OfferForm.get('datePFC').setValue(null);
              this.OfferForm.get('datePFC').setValue(this.currentPfc);
              // tslint:disable-next-line:no-unused-expression
              this.datePFC.valid === true;
              this.datePFC.markAsTouched();
              this.OfferForm.get('energy_type').setValue('energy3');
              this.getEcoEnergy('energy3');
              this.getPfcRecorder();
              },
            // tslint:disable-next-line:no-unused-expression
            (err) => {
              this.initDisabTypeOffer = false;
              this.existsPfc = false;
              // tslint:disable-next-line:no-unused-expression
              this.datePFC.valid === false;
              this.datePFC.markAsTouched();
            }
          );

        } else if (this.pfcType === 'SME') {
            this.OfferForm.get('datePFC').setValue('12.12.2040');
            this.currentDate =  { date: { year:  2040, month: 12 , day:  12 } };
            // tslint:disable-next-line:no-unused-expression
            this.datePFC.valid === true;
            this.datePFC.markAsTouched();
            this.OfferForm.get('validation_time').setValue(10);
            this.OfferForm.get('offer_status').setValue('');
        }
    }

    showSuccess(mesaj: string) { this.toastr.success(mesaj); }
    showError(mesaj: string) { this.toastr.error(mesaj); }

    getCcByCompany(cmp: Company) {
      if (cmp) {
        this.OfferForm.get('nomEntreprice').setValue(cmp.nom_entrepise);
        this.OfferForm.get('clientId').setValue(cmp.name + ' ' + cmp.surname );
        this.ccService.getCcByCompany(cmp.id).subscribe(
          (data) => { this.siteList = data;
            // default
            // this.getVolume(this.siteList[0].id);
            // this.getYearsBySite(this.siteList[0].id);
            // this.OfferForm.get('ccProfilHistorique').setValue(this.siteList[0].id);
          },
          (err) => {}
        );
      }
    }

    verifica_Volume_total() {
      // console.log('myVol', this.myVolume, 'max', this.maxVolumeCc);
      if (this.myVolume) {
          this.volCond = false;
          const volumes = this.myVolume.replace(/[^0-9.]/g, '');
          try {this.maxVolume = this.maxVolumeCc.replace(/[^0-9.]/g, '');
          } catch (e) {this.maxVolume = this.maxVolumeCc; }
          // console.log(Number(volumes), Number(this.maxVolume * 1000000));
          if (Number(volumes) >= Number(this.maxVolume * 1000000)) {
            if ( this.pfcType === 'Standart' ) {
              { this.volCond = true; this.OfferForm.get('volumeAnnuelTotal'); }} else { this.volCond = false; }
        }
      }
    }

    getVolume(id: number) {
      this.volumeId = id;
      if (id) {
        this.myVolume = null;
        this.ccService.getSiteVolume(id).subscribe(
          (data) => {
            this.myVolume = data['total_value'];
            this.OfferForm.get('volumeAnnuelTotal').setValue(data['total_value']);
            this.verifica_Volume_total();
        });
      }
      this.getLisage();
    }

    getLisage(onChangeTaux?: any) {
      if (this.volumeId && this.company.id &&  this.selectedYears) {
        this.ccService.getLissage(this.company.id, this.volumeId, this.percent, String(this.selectedYears) ).subscribe(
          (data) => {
            // console.log('lissage', data);
            this.existsLissage = false;
            this.existsLissageManual = false;
            if (data  !== null) {
              this.lisages = null;
              this.lisages = data;
              if (data['lissage_years'] !== undefined && data['lissage_years'].length > 0) {
                this.existsLissage = true;
                this.existsLissageManual = true;
              }
              this.OfferForm.get('lissage').setValue(data['lissage_years']);
              this.OfferForm.get('decote').setValue(data['years']);
              if (onChangeTaux !== true) {
                this.selectedYearsLisage.length = 0;
                this.lisages['lissage_years'].forEach(element => { this.selectedYearsLisage.push({year: element, type: 'lissage' }); });
                this.lisages['years'].forEach(element => { this.selectedYearsLisage.push({year: element, type: 'decote' }); });
              }
            }

            if (data === null) {
              this.lisages = null;
              this.existsLissage = true; // modify  of true becouse break error
              this.existsLissageManual = false;
              this.OfferForm.get('lissage').setValue('');
              this.OfferForm.get('decote').setValue(this.selectedYears);
              if (onChangeTaux !== true) {
                this.selectedYearsLisage.length = 0;
                for (let index = this.anneeIn.value; index <= this.anneeFin.value; index++) {
                  this.selectedYearsLisage.push({year: index, type: 'decote' }); }
              }
            }
            this.onChangesMarjes();
            this.observableMarjes('getLisage');
            this.getEcoEnergy(this.energy_type.value);
          },
          (err) => { }
        );
      }
    }

    getPfc(date: string) {
      this.pfcService.getByDate(date).subscribe((data) => { this.currentPfc = data;  this.getPfcRecorder(); });
    }

    // getUnits() {
    //   this.pfcService.getUnits().subscribe(
    //     (data) => {
    //       this.units = data['units'];
    //       this.OfferForm.get('unit').setValue('CHF');
    //       // tslint:disable-next-line:no-unused-expression
    //       this.unit.valid === true;
    //       this.unit.markAsTouched();
    //      },
    //   );
    // }

    setTypeOffer(ptype: string) {
      this.pfcType = '';
      this.pfcType = ptype;
      this.years();
      this.getVolume(this.volumeId);
      this.myOptions.enableDates.length = 0;
      this.enablesData();
      if (ptype === 'Standart') { this.OfferForm.get('unit').setValue('CHF'); }
    }

    getRiscs() { this.riscService.getAll().subscribe((data) => { this.multiSelect(data); }); }

    verificamMarje(data: any) {
      this.loading = true;
      if (this.one_veryfi_popup === false) { this.onSubmitOffer(data); }
      if (this.one_veryfi_popup === true) {
        for (const key in this.majors) {
          if (this.majors.hasOwnProperty(key)) {
            const val = this.majors[key];
            this.selectedYearsLisage.forEach(elem => {
              if (elem.year === Number(key) && elem.type === 'decote') {
                if (val <= 0 || val > 1 ) { this.majorationsVerify = true; }
              }

            });
          }
        }
      this.loading = false;
      if (this.majorationsVerify === false) { this.onSubmitOffer(data); }
      }
    }

    onSubmitOffer(data: any) {
      this.loading = true;
      const offer: Offer = new Offer;
      offer.years = this.selectedYears;
      offer.date_debut = data['date_debut'];
      offer.heures_in = data['heures_in'];
      offer.date_fin = data['date_fin'];
      offer.heures_fin = data['heures_fin'];
      offer.durre = data['durre'];
      offer.energy_type = data['energy_type'];
      offer.nr_opportunite = data['nr_opportunite'];
      offer.comment = data['comment'];
      offer.grd = data['grd'];
      if (data['type'] === 'retention') { offer.marche = true; } else { offer.marche = data['marche']; }
      offer.releve = data['releve'];
      offer.second_type = data['type'];
      offer.name = data['nomOffer'];
      if (data['typeOffer'] !== 'SME') { offer.pfc = data['pfc'].id; } else { offer.pfc = null; }
      if (data['typeOffer'] === 'Standart') { offer.validation_time = data['validation_time']; } else { offer.validation_time = null; }
      offer.cc = Number(data['ccProfilHistorique']);
      offer.company = data['companyf'].id;
      offer.consumption = data['volumeAnnuelTotal'];
      offer.unit = data['unit'];
      offer.profile = null;
      offer.pfc_market = null;
      offer.employees = 'to_50';
      offer.offer_type = data.typeOffer;
      offer.offer_status = data.offer_status;
      offer.user = this.currentUser.id;
      if ( this.vendeur ) { offer.conseiller = this.vendeur.user.pk; } else { offer.conseiller =  null; }
      if (data['prixHpHc'] === 'unique') { offer.shedules = [3]; } else { offer.shedules = [1, 2]; }
      offer.riscs = [];
      if (this.existsLissage && this.lisages) {
        offer.lissage_years = {'lissage_years': this.lisages};
        offer.lissage = this.lisages['lissage_years'].length !== 0;
        this.existsLissage = false;
        offer.lis_years = data.decote;
        offer.percent = this.percent;
      } else {
        offer.lissage_years = {'lissage_years': []};
        offer.lissage = false;
        offer.lis_years = '';
        offer.percent = null;
      }

      offer.decotes = this.decotes;
      offer.efforts = this.efforts;
      offer.energies = this.energies;
      offer.sur_go = this.sur_go;
      offer.majors = this.majors;
      offer.ps1 = this.ps1;
      offer.ps2 = this.ps2;
      offer.pfc_date_first = data.pfcRecordFirstF;
      offer.pfc_date_last = data.pfcRecordLastF;




      console.log('createOffer', offer);
      this.offerService.create(offer).subscribe(
        (res) => {
          this.one_veryfi_popup = true;
          this.result = res;
          this.loading = false;
          if (this.typeOffer.value === 'Standart') {
            this.showSuccess('L\'offre a été créée.');
          } else { this.showSuccess('Une offre SME est en attente pour ' + this.company.name + ' ' + this.company.surname); }
          if (this.result.fonction === 3) { $('#UploadPfc').click();  $('body').click();  this.reloadService.changeOffer(true); }
          if (this.result.fonction !== 3) { this.hideModal = true; }
          this.resetOfferForm();
        },
        (err) => {
          this.loading = false;
          this.showError(err.name);
          $('#UploadPfc').click();
          $('body').click();
        }
      );
    }

    prix(prix: any) {
      if ( prix === 'hc/hp' ) {
        this.OfferForm.get('hphc').setValue(true);  this.showhphc = true;
      } else { this.OfferForm.get('hphc').setValue(3); this.showhphc = false; }
    }

    createFormControles() {
      this.clientId = new FormControl({value: '', disabled: true}, [Validators.required,  Validators.pattern('')]);
      this.vandeurId = new FormControl({value: '', disabled: true}, [Validators.required,  Validators.pattern('')]);
      this.conseiller = new FormControl('');
      this.typeOffer = new FormControl('', Validators.required);
      this.prixHpHc = new FormControl('', Validators.required);
      this.nomOffer = new FormControl('', Validators.required);
      this.nomEntreprice = new FormControl('', Validators.required);
      this.nr_opportunite = new FormControl('', Validators.required);
      this.comment = new FormControl('');
      this.marche = new FormControl(false);
      this.releve = new FormControl(false);
      this.grd = new FormControl('', Validators.required);
      // this.grd = new FormControl('');
      this.companyf = new FormControl('', Validators.required);
      this.hphc = new FormControl('', Validators.required);
      this.ccProfilHistorique = new FormControl('', Validators.required);
      this.volumeAnnuelTotal = new FormControl({value: '', disabled: true}, Validators.required);
      this.anneesProposees = new FormControl();
      this.anneeIn  = new FormControl('', [ Validators.required, Validators.maxLength(4), Validators.minLength(4) ]);
      this.anneeFin = new FormControl('', [ Validators.required, Validators.maxLength(4), Validators.minLength(2) ]);
      this.anneeInForce  = new FormControl('', [ Validators.required, Validators.maxLength(4), Validators.minLength(4) ]);
      this.anneeFinForce = new FormControl('', [ Validators.required, Validators.maxLength(4), Validators.minLength(2) ]);
      this.datePFC = new FormControl('');
      this.pfc = new FormControl(Validators.required);
      this.type = new FormControl('', Validators.required);
      if ( this.currentUser.role === 1 ) {
        this.validation_time = new FormControl(1, [Validators.required, Validators.pattern('^([1-9][0-9]?|)'), Validators.maxLength(2)]);
      } else {
        this.validation_time = new FormControl('', Validators.required);
      }
      this.offer_status = new FormControl('', Validators.required);
      this.unit = new FormControl('', Validators.required);
      this.lissage = new FormControl('');
      this.decote = new FormControl('', Validators.required);
      this.taux = new FormControl( Validators.required);
      this.minim = new FormControl('');
      this.maxim = new FormControl('');
      this.decotesF = new FormControl(0, Validators.required);
      this.effortsF = new FormControl(0, Validators.required);
      this.energiesF = new FormControl(Validators.required);
      this.majorsF = new FormControl(0, Validators.required);
      this.sur_goF = new FormControl(0, Validators.required);
      this.totalEcoF = new FormControl('');
      this.ps1F = new FormControl(0, Validators.required);
      this.ps2F = new FormControl(0, Validators.required);
      this.mesajErrosF = new FormControl('');
      this.lisageMaxFormC = new FormControl('');
      this.energy_type = new FormControl('');
      this.date_debut = new FormControl('');
      this.heures_in = new FormControl(moment(this.curentTime).format('HH:mm'));
      this.date_fin = new FormControl({disabled: true});
      this.heures_fin = new FormControl(moment(this.curentTime).format('HH:mm'));
      this.durre = new FormControl({value: '00:00', disabled: true});
      this.dureeVaneurF = new FormControl('');
      this.max_volume_cc = new FormControl();
      this.pfcRecordFirstF = new FormControl('');
      this.pfcRecordLastF = new FormControl('');
     }

    createForm() {
      this.OfferForm = new FormGroup({
        clientId: this.clientId,
        vandeurId: this.vandeurId,
        typeOffer: this.typeOffer,
        prixHpHc: this.prixHpHc,
        nomOffer: this.nomOffer,
        nomEntreprice: this.nomEntreprice,
        nr_opportunite: this.nr_opportunite,
        comment: this.comment,
        marche: this.marche,
        releve: this.releve,
        grd: this.grd,
        companyf: this.companyf,
        hphc: this.hphc,
        ccProfilHistorique: this.ccProfilHistorique,
        volumeAnnuelTotal: this.volumeAnnuelTotal,
        anneesProposees: this.anneesProposees,
        anneeIn: this.anneeIn,
        anneeFin: this.anneeFin,
        anneeInForce: this.anneeInForce,
        anneeFinForce: this.anneeFinForce,
        datePFC: this.datePFC,
        pfc: this.pfc,
        type: this.type,
        validation_time: this.validation_time,
        unit: this.unit,
        lissage: this.lissage,
        decote: this.decote,
        taux: this.taux,
        minim: this.minim,
        maxim: this.maxim,
        decotesF: this.decotesF,
        effortsF: this.effortsF,
        energiesF: this.energiesF,
        majorsF: this.majorsF,
        ps1F: this.ps1F,
        ps2F: this.ps2F,
        sur_goF: this.sur_goF,
        totalEcoF: this.totalEcoF,
        mesajErrosF: this.mesajErrosF,
        lisageMaxFormC: this.lisageMaxFormC,
        energy_type: this.energy_type,
        date_debut: this.date_debut,
        heures_in:  this.heures_in,
        date_fin: this.date_fin,
        heures_fin: this.heures_fin,
        durre: this.durre,
        dureeVaneurF: this.dureeVaneurF,
        offer_status: this.offer_status,
        conseiller: this.conseiller,
        max_volume_cc: this.max_volume_cc,
        pfcRecordFirstF: this.pfcRecordFirstF,
        pfcRecordLastF: this.pfcRecordLastF,
     });
    }

    resetOfferForm () {
      this.selectedYears = [];
      this.OfferForm.get('nomOffer').reset();
      this.OfferForm.get('nr_opportunite').reset();
      this.OfferForm.get('type').reset();
      this.OfferForm.get('ccProfilHistorique').reset();
      this.OfferForm.get('volumeAnnuelTotal').reset();
      this.forces = false;
      this.existsLissageManual = false;
      this.aneeProposWait = false;
      this.yearList = [];
      this.selectedYearsLisage = [];
    }

    multiSelect(riscs: Array<Risc>) {
      this.selectedYears = [];
      this.yearSettings = {
          singleSelection: false,
          text: 'Choisir Annees',
          selectAllText: 'Tout sélectionner',
          unSelectAllText: 'Tout désélectionner',
          classes: 'myclass custom-class '
      };



      this.selectedPrimes = [ ];
      this.primesSettings = {
        singleSelection: false,
        text: 'Choisir risque',
        selectAllText: 'Tout sélectionner',
        unSelectAllText: 'Tout désélectionner',
        classes: 'myclass custom-class '
      };
    }


      onDateChanged(event: IMyDateModel): void {
       if ( this.pfcType === 'Standart') {
          this.currentDate = event;
          this.pfcService.getByDate(event['formatted']).subscribe(
            (data) => {
              this.currentPfc = data;
              this.existsPfc = true;
              this.OfferForm.get('energy_type').setValue('energy3');
              this.getEcoEnergy('energy3');
              this.getPfcRecorder();
             },
            (err) => { this.existsPfc = false; }
          );
        }
      }



      enablesData() {
        if ( this.pfcType === 'Standart') {
          this.loadPFC = true;
          this.pfcService.getAll().subscribe(
            (data) => {
              this.pfcs = data;
              this.getPfcInitialByday();
              data.forEach((element, index ) => {
                if (this.currentUser.role !== 1) {
                  if (index === 0) {
                    if (element.pfc_id.length === 10) {
                      this.enmData.push({
                        'day': Number(element['pfc_id'].slice(0, 2)),
                        'month': Number(element['pfc_id'].slice(3, 5)),
                        'year': Number(element['pfc_id'].slice(6, 10))
                      });
                    } else {
                    this.enmData.push({
                      'day': Number(element['pfc_id'].slice(0, 1)),
                      'month': Number(element['pfc_id'].slice(2, 4)),
                      'year': Number(element['pfc_id'].slice(5, 9))
                    });
                  }
                }
              } else {
                      if (element.pfc_id.length === 10) {
                      this.enmData.push({
                        'day': Number(element['pfc_id'].slice(0, 2)),
                        'month': Number(element['pfc_id'].slice(3, 5)),
                        'year': Number(element['pfc_id'].slice(6, 10))
                      });
                    } else {
                    this.enmData.push({
                      'day': Number(element['pfc_id'].slice(0, 1)),
                      'month': Number(element['pfc_id'].slice(2, 4)),
                      'year': Number(element['pfc_id'].slice(5, 9))
                    });
                  }
                }
              });
              this.loadPFC = false;
            },
          );
        }
      }

      onlyNumbers(arr: any) {
        if (arr) {
          let list = '';
          for (let i = 0; i < arr.length; i++) {
            if (i === 0) {
              if (arr[i].charCodeAt(0) !== '-'.charCodeAt(0)) {
                 const str = (<any>arr)[i].replace(/\D+/g, ''); if (str !== '')  {list += str; }
              } else {  list += '-'; }
            } else { const str = (<any>arr)[i].replace(/\D+/g, ''); if (str !== '')  {list += str; } }
          }
          return list;
        }
      }

      onChangesMax_Volume_cc(): void {
        this.OfferForm.get('max_volume_cc').valueChanges
        .debounceTime(100)
        .distinctUntilChanged()
        .subscribe(val => { if (val) {
          this.putConstants();
          this.verifica_Volume_total();
          const finis = this.transform(this.onlyNumbers(val), 0);  this.OfferForm.get('max_volume_cc').setValue(finis);
        }});
      }

      onChangesDureeVandior(): void {
        this.OfferForm.get('dureeVaneurF').valueChanges
        .debounceTime(100)
        .distinctUntilChanged()
        .subscribe(val => {
          this.observableDureeVandior(val);
        });
      }
      observableDureeVandior(val: number) {
          this.dureeVaneur = val;
          this.putConstants();
          this.observableMarjes('');
      }


      onChangesTaux(): void {
        this.OfferForm.get('taux').valueChanges
        .debounceTime(100)
        .distinctUntilChanged()
        .subscribe(val => { if (val) { this.getLisage(true); } });
      }


    onChangesPercent(): void {
      this.OfferForm.get('lisageMaxFormC').valueChanges
      .debounceTime(100)
      .distinctUntilChanged()
      .subscribe(val => {
        this.observablePercent(val);
      });
    }

    observablePercent(val: any) {
      if (val <= 0 ) { this.lisageMax = null;  } else {
        this.lisageMax = val;
        this.putConstants();
        this.observableMarjes('');
      }

    }

    onChangesMax(): void {
      this.OfferForm.get('maxim').valueChanges
      .debounceTime(100)
      .distinctUntilChanged()
      .subscribe(mx => {
        this.margesMax = mx;
        this.putConstants();
        this.observableMarjes('');
      });
    }

    onChangesMin(): void {
      this.OfferForm.get('minim').valueChanges
      .debounceTime(100)
      .distinctUntilChanged()
      .subscribe(mn => {
        this.margesMin = mn;
        this.putConstants();
        this.observableMarjes('');
      });
    }


  getConstants() {
    this.listdureeVaneur = [];
    this.offerService.getConstants().subscribe(
      (data) => { this.marges = data;
        data.forEach(element => {
          if (element.name === 'Lissage')       { this.lisageMax   = element.value; }
          if (element.name === 'Marges Min')    { this.margesMin   = element.value; }
          if (element.name === 'Marges Max')    { this.margesMax   = element.value; }
          if (element.name === 'Duree')         { this.dureeVaneur = element.value; }
          if (element.name === 'max_volume_cc') { this.maxVolumeCc = element.value; }
        });
        for (let index = 1; index <= this.dureeVaneur; index++) { this.listdureeVaneur.push( index ); }
        this.OfferForm.get('max_volume_cc').setValue(this.transform(this.maxVolumeCc, 0));
          },
      (e) => {}
    );
    this.onChangesMax();
    this.onChangesMin();
    this.onChangesMarjes();
  }

  putConstants() {
    if (this.marges) {
      this.putCons = false;
      this.marges.forEach(em => {
        if (em.name === 'Lissage'       && em.value !== this.lisageMax)   { em.value = this.lisageMax;   this.putCons = true; }
        if (em.name === 'Marges Min'    && em.value !== this.margesMin)   { em.value = this.margesMin;   this.putCons = true; }
        if (em.name === 'Marges Max'    && em.value !== this.margesMax)   { em.value = this.margesMax;   this.putCons = true; }
        if (em.name === 'Duree'         && em.value !== this.dureeVaneur) { em.value = this.dureeVaneur; this.putCons = true; }
        if (em.name === 'max_volume_cc' && em.value !== this.maxVolumeCc) { em.value = this.maxVolumeCc; this.putCons = true; }
    });
      if (this.putCons) { this.offerService.putConstants(this.marges).subscribe((data) => {}, (e) => {} ); }
    }
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
    this.mesajErros = false;
    if (this.selectedYearsLisage) {
      for (const key in this.majors) {
        if (this.majors.hasOwnProperty(key)) {
          const element = this.majors[key];
          this.selectedYearsLisage.forEach(item => {
            // console.log(val, item.year, key, '......', item.type, item.year === Number(key) , item.type === 'decote');
            if (item.year === Number(key) && item.type === 'decote') {
              // console.log(item.year, Number(key) , item.type);
              if (element > this.margesMax || element < this.margesMin || this.margesMin > this.margesMax) {
                this.mesajErros = true;
              }
            }
          });
        }
      }
    }
  }

  getYearsBySite(id: number) {
    this.yearList = [];
    this.yearListForce = [];
    // console.log(id);
    if (id) {
      this.offerService.getYearBySite(id).subscribe(
        (data) => {
          // console.log('data[years]', data['years']);
          if (this.typeOffer.value === 'Standart') {
            const date = new Date();
            const year = date.getFullYear() + 4;
            data['years'].forEach(element => {
              // console.log(year, element);
              if (year >= element) {
                this.yearList.push(element);
                this.yearListForce.push(element);
              }
            });
          } else {
            this.yearList = data['years'];
            this.yearListForce = data['years'];
            // console.log('yearList', this.yearList);
            // console.log('yearListForce', this.yearListForce);
          }

          this.OfferForm.get('anneeIn').setValue(data['years'][0]);
          this.OfferForm.get('anneeFin').setValue(data['years'][0]);
          this.observableAnneeIn(data['years'][0]);
          if (!this.aneeProposWait) {
            this.OfferForm.get('anneeInForce').setValue(data['years'][0]);
            this.OfferForm.get('anneeFinForce').setValue(data['years'][0]);
            this.observableAnneeInForce(data['years'][0]);
            if (this.forces === true ) { this.forces = false; }
          }
          this.getEcoEnergy(this.energy_type.value);
      });
    }
  }


  getEcoEnergy(energy: string) {
    this.atentionPFC = false;   if (!this.currentPfc) { this.atentionPFC = true; }
    this.onChangesSurGo();
    if (this.currentPfc) {
      this.listEcos = null;
      this.offerService.getEcoEnergy(this.currentPfc.id, energy).subscribe(
        (data) => {  this.listEcos = data; this.calculateTotal(this.listEcos); },
      );
    }
  }

  calculateTotal(datacalculate: any) {
  if (datacalculate && this.selectedYears.length !== 0) {
      for (const key in this.sur_go) {
        if (this.sur_go.hasOwnProperty(key)) {
          datacalculate.forEach(y => {
            if ( Number(key) === y.year) {
              this.energies[key] = y.value;
              this.totalEco[key] = y.value + this.sur_go[key];
            }
          });
        }
      }
    }
  }


  getGrds() { this.offerService.getGrds().subscribe( (data) => {
    this.grds = data;
    if (data) { this.OfferForm.get('grd').setValue(this.grds[0].id); }
  } ); }

  onChangesHeureIn(): void {
    this.OfferForm.get('heures_in').valueChanges
    .debounceTime(100)
    .distinctUntilChanged()
    .subscribe(val => {
       this.diference();
    });
  }
  onChangesHeuresFin(): void {
    this.OfferForm.get('heures_fin').valueChanges
    .debounceTime(100)
    .distinctUntilChanged()
    .subscribe(val => {
      this.diference();
    });
  }

  onChangesDateIn(): void {
    this.OfferForm.get('date_debut').valueChanges
    .debounceTime(100)
    .distinctUntilChanged()
    .subscribe(val => {
      this.diference();
    });
  }
  onChangesDateFin(): void {
    this.OfferForm.get('date_fin').valueChanges
    .debounceTime(100)
    .distinctUntilChanged()
    .subscribe(val => {
      this.diference();
    });
  }

  diference() {
    this.dateDif = false;
    this.durreNmodel = null;
    let unu = 0;
    let doi = 0;
    console.log(this.currentDebut);
    try {
      unu = moment(this.currentDebut.formatted + ' ' + this.heures_in.value, 'DD.MM.YYYY HH:mm').valueOf();
      doi = moment(this.currentFin.formatted + ' ' + this.heures_fin.value, 'DD.MM.YYYY HH:mm').valueOf();
    } catch (error) { }
    console.log('unu', unu, 'doi', doi, unu > doi);
    if (unu > doi) { this.dateDif = true; this.durreNmodel =  '00' + ' '  + '00' + ':' +  '00';
    } else {
          const dif =  moment.duration(moment(doi).diff(unu));
          try {
            if ( dif['_data'].hours <= 9) { this.hh = '0' + dif['_data'].hours; } else { this.hh = dif['_data'].hours; }
            if ( dif['_data'].minutes <= 9) { this.mm = '0' + dif['_data'].minutes; } else { this.mm = dif['_data'].minutes; }
          } catch (error) {  this.hh = '00';  this.mm = '00'; }

          try {
            if ( dif['_data'].days <= 9) { this.dd = '0' +  dif['_data'].days; } else { this.dd =  dif['_data'].days; }
          } catch (error) { this.dd = '00'; }
          this.durreNmodel =  this.dd + ' '  + this.hh + ':' +  this.mm;
      }
  }

  defaultValue() {
    this.OfferForm.get('unit').setValue('CHF');
    // tslint:disable-next-line:no-unused-expression
    this.unit.valid === true;
    this.unit.markAsTouched();

    this.OfferForm.get('typeOffer').setValue('Standart');
    this.setTypeOffer('Standart');

    // tslint:disable-next-line:no-unused-expression
    this.typeOffer.valid === true;
    this.typeOffer.markAsTouched();

    this.OfferForm.get('prixHpHc').setValue('hc/hp');
    this.prix('hc/hp');
    // tslint:disable-next-line:no-unused-expression
    this.prixHpHc.valid === true;
    this.prixHpHc.markAsTouched();
  }

  closeDropDown() {this.showDropDown = false; }
  openDropDown() {this.showDropDown = true;
    if (this.vedeurName === this.currentUser.lastName + ' ' + this.currentUser.firstName) {
      this.vedeurName = ''; this.observableVendeur(''); }}

  onChangesVendeur(): void {
    this.OfferForm.get('conseiller').valueChanges
    .debounceTime(100)
    .distinctUntilChanged()
    .subscribe(val => {
      this.observableVendeur(val);
    });
  }

  observableVendeur(val: any) {
      this.vendeures = null;
      this.vedeurName = val;
      this.searchService.searchVedeor(val).subscribe(
        (data) => { this.vendeures = data; }
      );
  }

  saveVadeur(van: any) {
    this.vedeurName = van.user.first_name + ' ' + van.user.last_name ;
    this.vendeur = van;
    this.vendeures = null;
  }

  onChangesSurGo(): void {
    this.OfferForm.get('sur_goF').valueChanges
    .debounceTime(100)
    .distinctUntilChanged()
    .subscribe(val => {
      this.calculateTotal(this.listEcos);
    });
  }


  observableAnneeFin(val: number) {
    if (this.anneeFin.value < this.anneeIn.value ) {this.OfferForm.get('anneeIn').setValue(this.anneeFin.value); }
    this.betweenYears = false;
    this.anInFin = false;
    if (this.anneeIn.value > this.anneeFin.value || this.anneeFin.value < this.anneeIn.value) { this.betweenYears = true; }
    this.selectedYears.length = 0;
    if (val >= this.yearList[0] && val <= this.yearList[this.yearList.length - 1]) {
      for (let y = this.anneeIn.value; y <= this.anneeFin.value; y++) { this.selectedYears.push(y); }
     } else  { this.betweenYears = true; }
    this.years();
  }



  observableAnneeIn(val: number) {
    if (this.anneeIn.value > this.anneeFin.value ) {this.OfferForm.get('anneeFin').setValue(this.anneeIn.value); }
    this.betweenYears = false;
    if (this.anneeIn.value > this.anneeFin.value || this.anneeFin.value < this.anneeIn.value) { this.betweenYears = true; }
    this.selectedYears.length = 0;
    if (val >= this.yearList[0] && val <= this.yearList[this.yearList.length - 1]) {
      for (let y = this.anneeIn.value; y <= this.anneeFin.value; y++) { this.selectedYears.push(y); }
     } else  { this.betweenYears = true; }
    this.years();
  }



  observableAnneeFinForce(val: number) {
    if (this.anneeFinForce.value < this.anneeInForce.value ) {this.OfferForm.get('anneeInForce').setValue(this.anneeFinForce.value); }
    this.selectedYearsForce.length = 0;
    if (val >= this.yearListForce[0] && val <= this.yearListForce[this.yearListForce.length - 1]) {
      for (let y = this.anneeInForce.value; y <= this.anneeFinForce.value; y++) { this.selectedYearsForce.push(Number(y)); }
     }
  }



  observableAnneeInForce(val: number) {
    if (this.anneeInForce.value > this.anneeFinForce.value ) {this.OfferForm.get('anneeFinForce').setValue(this.anneeInForce.value); }
    this.selectedYearsForce.length = 0;
    if (val >= this.yearListForce[0] && val <= this.yearListForce[this.yearListForce.length - 1]) {
      for (let y = this.anneeInForce.value; y <= this.anneeFinForce.value; y++) { this.selectedYearsForce.push(Number(y)); }
     }
  }


  years() {
    this.yearsMore4 = false;
    this.getLisage();
    if ( this.pfcType === 'Standart' ) {
      if (this.selectedYears.length <= 4) {
        this.yearsMore4 = false;
      } else { this.yearsMore4 = true; }
    } else { this.yearsMore4 = false; }
    this.getPfcRecorder();
  }

  typeOf(type: any) {
     if (type === 'prolongation') {
      this.OfferForm.get('grd').setValue(this.grds[0].id);
      // tslint:disable-next-line:no-unused-expression
      this.OfferForm.get('grd').valid === true;
    }
    // else { this.OfferForm.get('grd').setValue(null); }
  }


  go_manual() {
    this.curentSite = null;
    this.siteList.forEach(element => { if (Number(this.ccProfilHistorique.value) === Number(element.id)) {this.curentSite = element; } });
    this.customObservable.changeManualLissage(
      {site: this.curentSite,
       years: this.selectedYearsForce,
       yearIn:  this.anneeInForce.value,
       yearFin: this.anneeFinForce.value,
       nom: this.nomOffer.value,
       company: this.company,
       prixHpHc: this.prixHpHc.value
      });
  }


  mailfunction() {
    this.close();
    this.loading = true;
    this.offerService.Mailfunction(this.result.id).subscribe(
      (data) => {
          this.showSuccess('L\'email a été envoyé.');
          this.loading = false;
          this.hideModal = false;
      },
        (er) => { this.hideModal = false; this.loading = false; this.showError(er.name); },
    );
    this.reloadService.changeOffer(true);
  }

  close() {  $('#UploadPfc').click();  $('body').click(); }

  forcces() { this.disablisMan = true; this.forces = !this.forces; this.disablisMan = false; }

  getPfcRecorder() {
    if (this.currentPfc && this.selectedYears.length !== 0) {
      this.pfcService.getPfcFirstRecorder(this.currentPfc.id, this.selectedYears).subscribe(
        (data) => {
          // tslint:disable-next-line:max-line-length
          const first = {date: {year: Number(data['first'].slice(0, 4)), month: Number(data['first'].slice(5, 7)), day: Number(data['first'].slice(8, 10))}};
          // tslint:disable-next-line:max-line-length
          const last =  {date: {year: Number(data['last'].slice(0, 4)), month: Number(data['last'].slice(5, 7)), day: Number(data['last'].slice(8, 10))}};
          this.pfcRecorder = {};
          this.pfcRecorder = {first: first.date.year, last: last.date.year};
          this.pfcRecordFirst = first;
      console.log('getPfcRecorder STD');
      this.pfcRecordLast  = last;
        }
      );
    } else {
      // for SME !curentpfc
      const first = {date: {year: Number(this.anneeIn.value), month: 1, day: 1}};
      const last =  {date: {year: Number(this.anneeFin.value), month: 12,  day: 31}};
      this.pfcRecorder = {};
      this.pfcRecorder = {first: first.date.year, last: last.date.year};
      this.pfcRecordFirst = first;
      this.pfcRecordLast  = last;
    }
    this.onChangespfcRecordLast();
    this.onChangespfcRecordFirst();
  }

  onChangespfcRecordFirst(): void {
    this.OfferForm.get('pfcRecordFirstF').valueChanges.debounceTime(100).distinctUntilChanged()
    .subscribe(val => { if (val) { this.veryficaPerioadaPfcRecorder(); } });
  }

  onChangespfcRecordLast(): void {
    this.OfferForm.get('pfcRecordLastF').valueChanges.debounceTime(100).distinctUntilChanged()
    .subscribe(val => { if (val) { this.veryficaPerioadaPfcRecorder(); } });
  }


  veryficaPerioadaPfcRecorder() {
    if (this.pfcRecordFirst && this.pfcRecordLast) {
      this.invalidPeriod = false;
      // console.log('data', data);
      // console.log('veryfica', this.pfcRecordFirst, this.pfcRecordLast);
      // tslint:disable-next-line:max-line-length
      // console.log('if', this.pfcRecorder.first, '>',  this.pfcRecordFirst.date.year, '||', this.pfcRecordFirst.date.year, '>', this.pfcRecorder.last);
      // tslint:disable-next-line:max-line-length
      if (this.pfcRecorder.first > this.pfcRecordFirst.date.year || this.pfcRecordFirst.date.year > this.pfcRecorder.last) { this.invalidPeriod = true; }
      // tslint:disable-next-line:max-line-length
      if (this.pfcRecorder.first > this.pfcRecordLast.date.year || this.pfcRecordLast.date.year > this.pfcRecorder.last) { this.invalidPeriod = true; }
      // tslint:disable-next-line:max-line-length
      // tslint:disable-next-line:max-line-length
      if (moment.duration(this.pfcRecordFirst.date).valueOf() > moment.duration(this.pfcRecordLast.date).valueOf()) { this.invalidPeriod = true; }


    }
  }



}

