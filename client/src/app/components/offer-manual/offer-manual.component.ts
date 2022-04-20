import { Component, OnInit, Input } from '@angular/core';
import { CcService, CustomObservable } from '../../_services';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { OfferService } from '../../_services/offer.service';
import { Company } from '../../_models';

@Component({
  selector: 'app-offer-manual',
  templateUrl: './offer-manual.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/animate.css',
    // '../../../assets/css/styles/theme.css'
  ]
})
export class OfferManualComponent implements OnInit {
  siteList = [];
  yearList = [];
  offerManual: FormGroup;
  ccHisto: FormControl;
  anneeInForce:  FormControl;
  anneeFinForce: FormControl;
  site: any;
  // first
  e_hp:     FormControl; oe_hp = {};
  e_hc:     FormControl; oe_hc = {};
  h_hp:     FormControl; oh_hp = {};
  h_hc:     FormControl; oh_hc = {};
  money_i:  FormControl; omoney_i = {};
  // final
  fin_e_hp:     FormControl; o_fin_e_hp = {};
  fin_e_hc:     FormControl; o_fin_e_hc = {};
  fin_h_hp:     FormControl; o_fin_h_hp = {};
  fin_h_hc:     FormControl; o_fin_h_hc = {};
  fin_money_i:  FormControl; o_fin_money_i = {};

  selectedYears = [];
  prix = [];
  prix_f = [];
  nomOffer: string;
  loading = false;
  company: Company;
  prixHpHc: any;


  constructor( private ccService: CcService,
               private offerService: OfferService,
               private customObservable: CustomObservable) { }

  ngOnInit() {
    this.createFormControles();
    this.ccreateForm();
    this.customObservable.isManualLissage.subscribe((data) => {
       if (data) {
        this.nomOffer = data.nom;
        this.selectedYears = data.years;
        this.site = data.site;
        this.company = data.company;
        this.offerManual.get('ccHisto').setValue(data.site.name);
        this.offerManual.get('anneeInForce').setValue(data.years[0]);
        this.offerManual.get('anneeFinForce').setValue(data.years[data.years.length - 1]);
        this.prixHpHc = data.prixHpHc;
       }
      } );

  }


  createFormControles() {
    this.ccHisto       = new FormControl({value: '', disabled: true}, Validators.required);
    this.anneeInForce  = new FormControl({value: '', disabled: true}, Validators.required);
    this.anneeFinForce = new FormControl({value: '', disabled: true}, Validators.required);
    this.e_hc          = new FormControl('', Validators.required);
    this.e_hp          = new FormControl('', Validators.required);
    this.h_hc          = new FormControl('', Validators.required);
    this.h_hp          = new FormControl('', Validators.required);
    this.money_i       = new FormControl('', Validators.required);

    this.fin_e_hc     = new FormControl('', Validators.required);
    this.fin_e_hp     = new FormControl('', Validators.required);
    this.fin_h_hc     = new FormControl('', Validators.required);
    this.fin_h_hp     = new FormControl('', Validators.required);
    this.fin_money_i  = new FormControl('', Validators.required);

  }
  ccreateForm() {
    this.offerManual = new FormGroup({
      ccHisto: this.ccHisto,
      anneeInForce: this.anneeInForce,
      anneeFinForce: this.anneeFinForce,
      e_hc: this.e_hc,
      e_hp: this.e_hp,
      h_hc: this.h_hc,
      h_hp: this.h_hp,

      fin_e_hc: this.fin_e_hc,
      fin_e_hp: this.fin_e_hp,
      fin_h_hc: this.fin_h_hc,
      fin_h_hp: this.fin_h_hp,

      money_i: this.money_i,
      fin_money_i: this.fin_money_i,
    });
  }

  // getYearsBySite(id: number) {
  //   // this.yearList = [];
  //   // this.offerService.getYearBySite(id).subscribe(
  //   //   (data) => {
  //   //     this.yearList = data['years'];
  //   //     this.offerManual.get('anneeInForce').setValue(data['years'][0]);
  //   //     this.offerManual.get('anneeFinForce').setValue(data['years'][1]);
  //   //     this.observableAnneeIn(data['years'][0]);


  //   //       // default
  //   //     // this.offerManual.get('anneeInForce').setValue(data['years'][1]);
  //   //     // this.offerManual.get('anneeFinForce').setValue(data['years'][4]);
  //   //     // this.observableAnneeIn(data['years'][1]);

  //   //   });
  // }

  observableAnneeFin(val: number) {

    if (this.anneeFinForce.value < this.anneeInForce.value ) {
        this.offerManual.get('anneeInForce').setValue(Number(this.anneeFinForce.value)); }
    if (this.anneeInForce.value > this.anneeFinForce.value || this.anneeFinForce.value < this.anneeInForce.value) { }
    this.selectedYears.length = 0;
    if (val >= this.yearList[0] && val <= this.yearList[this.yearList.length - 1]) {
      for (let y = this.anneeInForce.value; y <= this.anneeFinForce.value; y++) { this.selectedYears.push(Number(y)); }
     }
  }



  observableAnneeIn(val: number) {
    if (this.anneeInForce.value > this.anneeFinForce.value ) {
        this.offerManual.get('anneeFinForce').setValue(Number(this.anneeInForce.value)); }
    if (this.anneeInForce.value > this.anneeFinForce.value || this.anneeFinForce.value < this.anneeInForce.value) { }
    this.selectedYears.length = 0;
    if (val >= this.yearList[0] && val <= this.yearList[this.yearList.length - 1]) {
      for (let y = this.anneeInForce.value; y <= this.anneeFinForce.value; y++) { this.selectedYears.push(Number(y)); }
     }
  }

  getCcByCompany(cmp: any) {
    this.ccService .getCcByCompany(cmp).subscribe( (data) => {
    this.siteList = data;
    // default
    // this.getYearsBySite(this.siteList[2].id);
    this.offerManual.get('ccHisto').setValue(this.siteList[2].id);
  } ); }


  onSubmitOffer (data: any) {
    this.loading = true;
    this.prix.length = 0;
    this.prix_f.length = 0;
    this.prix.push(  {ete_hp: this.oe_hp},      {ete_hc: this.oe_hc},      {hiver_hp: this.oh_hp },      {hiver_hc: this.oh_hc});
    this.prix_f.push({ete_hp: this.o_fin_e_hp}, {ete_hc: this.o_fin_e_hc}, {hiver_hp: this.o_fin_h_hp }, {hiver_hc: this.o_fin_h_hc});

    //   console.log(
    //   'name', this.nomOffer,
    //   'site', this.site.id,
    //   'anii', this.selectedYears,
    //   'prix', this.prix,
    //   'prix_f', this.prix_f,
    //   'omoney_i', this.omoney_i,
    //   'o_fin_money_i', this.o_fin_money_i
    // );

    const offerManual = {
      'name': this.nomOffer,
      'site': this.site.id,
      'anii': this.selectedYears,
      'prix': this.prix,
      'prix_f': this.prix_f,
      'omoney_i': this.omoney_i,
      'o_fin_money_i': this.o_fin_money_i,
      'company': this.company,
      'prixHpHc': this.prixHpHc,

    };
    this.offerService.manualOffer(offerManual).subscribe(
      (dataa) => { this.loading = false;  this.close(); },
      (er) => {  this.loading = false; },
    );
  }

  close() { $('#manuals').click(); }
  aneeProposWait () { this.customObservable.changeAneeProposWait(true); }
}
