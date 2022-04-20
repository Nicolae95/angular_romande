import { Risc } from './../../_models/risc';
import { User } from './../../_models/user';
import { Component, OnInit} from '@angular/core';
import { OfferService } from '../../_services/offer.service';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import 'rxjs/add/operator/switchMap';
import { CustomObservable } from '../../_services';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import { ReloadService } from '../../_services/reload.sevice';
import { Toast, ToastrService } from 'ngx-toastr';


@Component({
  selector: 'app-edit-offer',
  templateUrl: './edit-offer.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/animate.css',
    // '../../../assets/css/styles/theme.css'
  ]
})

export class EditOfferComponent implements OnInit {
  currentUser: User;
  offer: any;
  year: number;
  editOfferForm: FormGroup;
  type: FormControl;
  nomOffer: FormControl;
  yearList = [];
  selectedYears = [];
  yearSettings = {};

  majorsF: FormControl; majors = {}; majors1 = {};
  sur_goF: FormControl; sur_go = {}; sur_go1 = {};
  loading = false;
  energy_type: FormControl;
  parameters: any;
  selectedYearsLisage = [];
  yearsSplits = [];
  listEcos: any;
  currentPfc: any;
  // energiesF: FormControl;
   energies = {};
  // totalEcoF: FormControl;
   totalEco = {};


    constructor(private offerService: OfferService,
                private reloadService: ReloadService,
                private toastr: ToastrService,
                private customObservable: CustomObservable) {
                this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
     }

    ngOnInit() {
      this.year = new Date().getFullYear();
      for (let i = 0; i < 6; i++) {
        this.yearList.push({'id' : i, 'itemName' : this.year + i});
      }
      this.offer = null;
      this.customObservable.isEditOffer.subscribe(
        (data) => {
          this.offer = data;
          if (this.offer) {
            this.majors = {}; this.majors1 = {};
            this.sur_go = {}; this.sur_go1 = {};
            this.updateForm(this.offer);
            console.log('data', data);
            this.currentPfc = this.offer.pfc;
            this.getEcoEnergy(this.offer.energy_type);
            const y = String(this.offer.years);
            this.yearsSplits = y.split(',');
            // console.log('yearsSplits', this.yearsSplits);
            this.getParameters(this.offer.id);
          }
        },
        (err) => {}
      );
    }

    multiSelect(riscs: Array<Risc>) {
      this.selectedYears = [];
      this.yearSettings = {
          singleSelection: false,
          text: 'Choisir Annees',
          selectAllText: 'Select All',
          unSelectAllText: 'UnSelect All',
          classes: 'myclass custom-class '
      };
    }

    editOffre(offer: any) {
      this.loading = true;
      const majoration = [];
      const sur_go = [];
      for (const key in this.majors) {
        if (this.majors.hasOwnProperty(key)) {
         if (this.majors[key] === undefined) { majoration.push( {year: key, value: this.majors1[key]});
          } else { majoration.push( {year: key, value: this.majors[key]}); }
        }
      }

      for (const key in this.sur_go) {
        if (this.sur_go.hasOwnProperty(key)) {
         if (this.sur_go[key] === undefined) { sur_go.push( {year: key, value: this.sur_go1[key]});
          } else { sur_go.push( {year: key, value: this.sur_go[key]}); }
        }
      }

      // tslint:disable-next-line:max-line-length
      for (const key in majoration) { if (majoration.hasOwnProperty(key)) { const e = majoration[key]; if (e.value === undefined || e.value === null) {  e.value = 0; }}}
      // tslint:disable-next-line:max-line-length
      for (const key in sur_go) { if (sur_go.hasOwnProperty(key)) { const e = sur_go[key]; if (e.value === undefined || e.value === null) {  e.value = 0; }}}


      const obj_to_send = {
        'name': this.nomOffer.value,
        'energy_type': this.energy_type.value,
        'majors': majoration,
        'sur_go': sur_go,
      };
      this.submitEditoffer(obj_to_send);

    }

    submitEditoffer(obj: any) {
      this.offerService.editOffer(this.offer.id, obj).subscribe(
        (data) => {
          this.reloadService.changeEditOffer(true);
          this.toastr.success('Les détails de l\'offre ont été modifiés');
          $('#cancelEditform').click();
          $('body').click();
          this.loading = false;
          this.editOfferForm.reset();

        },
        (er) => { this.loading = false; }
      );
    }


    updateForm(offer: any) {
      this.nomOffer = new FormControl(this.offer.name, Validators.required);
      this.type = new FormControl(this.offer.second_type , Validators.required);
      this.majorsF = new FormControl(0, Validators.required);
      this.sur_goF = new FormControl(0, Validators.required);
      this.energy_type = new FormControl(this.offer.energy_type, Validators.required);
      this.upForm();
     }

     upForm() {
      this.editOfferForm = new FormGroup({
        nomOffer: this.nomOffer,
        majorsF: this.majorsF,
        sur_goF: this.sur_goF,
        energy_type: this.energy_type


     });
    }

    createFormControles() {
      this.energy_type = new FormControl('');
      this.nomOffer = new FormControl('', Validators.required);
      this.majorsF = new FormControl(0, Validators.required);
      this.sur_goF = new FormControl(0, Validators.required);
    }

    createForm() {
      this.editOfferForm = new FormGroup({
        nomOffer: this.nomOffer,
        majorsF: this.majorsF,
        sur_goF: this.sur_goF,
        energy_type: this.energy_type,
     });
    }


    getParameters(id: number) {
      this.offerService.getParameters(id).subscribe((data) => {
         this.parameters = data;
         this.yeasrLisagedecot();
        } );
    }

    yeasrLisagedecot() {
      this.selectedYearsLisage.length = 0;
      if (this.offer.lissage === false) {
        this.yearsSplits.forEach(ofersY => { this.selectedYearsLisage.push({year: Number(ofersY), type: 'decote' }); });
      } else {
        this.yearsSplits.forEach(ofersY => { this.selectedYearsLisage.push({year: Number(ofersY), type: 'lissage' }); });
        // tslint:disable-next-line:max-line-length
        this.selectedYearsLisage.forEach(yearD => { this.offer.years_liss_list.forEach(lissY => { if (Number(yearD.year) === Number(lissY)) { yearD.type = 'decote'; } });
      });
      }
      this.setParam();
    }


    setParam() {
     if (this.majors && this.parameters) {
     setTimeout(() => {
              this.parameters.parameters.forEach(param => {
                if (param.parameter__code === 'majors') { this.majors1[param.year] = param.value; }
                if (param.parameter__code === 'sur_go') { this.sur_go1[param.year] = param.value; }
              });

      });
    }
    }


  getEcoEnergy(energy: string) {
    this.onChangesSurGo();
    if (this.currentPfc) {
      this.listEcos = null;
      this.offerService.getEcoEnergy(this.currentPfc, energy).subscribe(
        (data) => {  this.listEcos = data; this.calculateTotal(this.listEcos); },
      );
    }
  }

  onChangesSurGo(): void {
    this.editOfferForm.get('sur_goF').valueChanges
    .debounceTime(100)
    .distinctUntilChanged()
    .subscribe(val => {
      this.calculateTotal(this.listEcos);
    });
  }

  calculateTotal(datacalculate: any) {
    if (datacalculate && this.selectedYearsLisage.length !== 0) {
        for (const key in this.sur_go) {
          if (this.sur_go.hasOwnProperty(key)) {
              datacalculate.forEach(y => {
                if ( Number(key) === y.year) {
                  console.log('0', y.value, '+', this.sur_go[key], '=', y.value + this.sur_go[key]);
                  console.log('1', y.value, '+', this.sur_go1[key], '=', y.value + this.sur_go[key]);

                  this.energies[key] = y.value;
                  if ( this.sur_go[key] === undefined) {
                    this.totalEco[key] =  Number(y.value) + Number(this.sur_go1[key]);
                  } else {
                    this.totalEco[key] =  Number(y.value) + Number(this.sur_go[key]);
                  }
                }
              });
          }
        }
        console.log(this.totalEco);
      }
    }


}



