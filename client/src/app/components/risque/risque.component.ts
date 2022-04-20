import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { INgxMyDpOptions, IMyDateModel } from 'ngx-mydatepicker';

@Component({
  selector: 'app-risque',
  templateUrl: './risque.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css'
  ]
})
export class RisqueComponent implements OnInit {
  risqueGroup: FormGroup;
  indetifiant: FormControl;
  nomloffre: FormControl;
  dateApp: FormControl;
  jusqu: FormControl;
  year: number;
  yearList: Array<number> = [];

  primesRisq1: FormControl; primesRisq2: FormControl; primesRisq3: FormControl; primesRisq4: FormControl; primesRisq5: FormControl;
  pwb1: FormControl; pwb2: FormControl; pwb3: FormControl; pwb4: FormControl; pwb5: FormControl;
  volumeRisq1: FormControl; volumeRisq2: FormControl; volumeRisq3: FormControl; volumeRisq4: FormControl; volumeRisq5: FormControl;
  prixRisq1: FormControl; prixRisq2: FormControl; prixRisq3: FormControl; prixRisq4: FormControl; prixRisq5: FormControl;
  desGo1: FormControl; desGo2: FormControl; desGo3: FormControl; desGo4: FormControl; desGo5: FormControl;
  prod1: FormControl; prod2: FormControl; prod3: FormControl; prod4: FormControl; prod5: FormControl;
  marges1: FormControl; marges2: FormControl; marges3: FormControl; marges4: FormControl; marges5: FormControl;
  lissage1: FormControl; lissage2: FormControl; lissage3: FormControl; lissage4: FormControl; lissage5: FormControl;



  myOptions: INgxMyDpOptions = {
    // other options...
    dateFormat: 'dd.mm.yyyy',
  };
  model: any = { date: { year: 2018, month: 10, day: 9 } };
  jusqumodel: any = { date: { year: 2028, month: 10, day: 9 } };

  constructor() { }

  ngOnInit() {
    this.year = new Date().getFullYear();
    let y: number;
    for (y = this.year; y < this.year + 5; y++) {
      this.yearList.push(y);
    }
    this.createFormControles();
    this.createForm();
  }

  createFormControles() {
    this.indetifiant = new FormControl('', Validators.required);
    this.nomloffre = new FormControl('', Validators.required);
    this.dateApp = new FormControl('', Validators.required);
    this.jusqu = new FormControl('', Validators.required);
    // primesRisq
    this.primesRisq1 = new FormControl('', Validators.required);
    this.primesRisq2 = new FormControl('', Validators.required);
    this.primesRisq3 = new FormControl('', Validators.required);
    this.primesRisq4 = new FormControl('', Validators.required);
    this.primesRisq5 = new FormControl('', Validators.required);
    // pwb
    this.pwb1 = new FormControl('', Validators.required);
    this.pwb2 = new FormControl('', Validators.required);
    this.pwb3 = new FormControl('', Validators.required);
    this.pwb4 = new FormControl('', Validators.required);
    this.pwb5 = new FormControl('', Validators.required);
    // volumeRisq
    this.volumeRisq1 = new FormControl('', Validators.required);
    this.volumeRisq2 = new FormControl('', Validators.required);
    this.volumeRisq3 = new FormControl('', Validators.required);
    this.volumeRisq4 = new FormControl('', Validators.required);
    this.volumeRisq5 = new FormControl('', Validators.required);
    // prixRisq
    this.prixRisq1 = new FormControl('', Validators.required);
    this.prixRisq2 = new FormControl('', Validators.required);
    this.prixRisq3 = new FormControl('', Validators.required);
    this.prixRisq4 = new FormControl('', Validators.required);
    this.prixRisq5 = new FormControl('', Validators.required);
    // desGo
    this.desGo1 = new FormControl('', Validators.required);
    this.desGo2 = new FormControl('', Validators.required);
    this.desGo3 = new FormControl('', Validators.required);
    this.desGo4 = new FormControl('', Validators.required);
    this.desGo5 = new FormControl('', Validators.required);
    // prod
    this.prod1 = new FormControl('', Validators.required);
    this.prod2 = new FormControl('', Validators.required);
    this.prod3 = new FormControl('', Validators.required);
    this.prod4 = new FormControl('', Validators.required);
    this.prod5 = new FormControl('', Validators.required);
    // marges
    this.marges1 = new FormControl('', Validators.required);
    this.marges2 = new FormControl('', Validators.required);
    this.marges3 = new FormControl('', Validators.required);
    this.marges4 = new FormControl('', Validators.required);
    this.marges5 = new FormControl('', Validators.required);
    // lissage
    this.lissage1 = new FormControl('', Validators.required);
    this.lissage2 = new FormControl('', Validators.required);
    this.lissage3 = new FormControl('', Validators.required);
    this.lissage4 = new FormControl('', Validators.required);
    this.lissage5 = new FormControl('', Validators.required);
  }

  createForm() {
    this.risqueGroup = new FormGroup({
      indetifiant: this.indetifiant,
      nomloffre: this.nomloffre,
      dateApp: this.dateApp,
      jusqu: this.jusqu,
      // primesRisq
      primesRisq1: this.primesRisq1,
      primesRisq2: this.primesRisq2,
      primesRisq3: this.primesRisq3,
      primesRisq4: this.primesRisq4,
      primesRisq5: this.primesRisq5,
      // pwb
      pwb1: this.pwb1,
      pwb2: this.pwb2,
      pwb3: this.pwb3,
      pwb4: this.pwb4,
      pwb5: this.pwb5,
      // volumeRisq
      volumeRisq1: this.volumeRisq1,
      volumeRisq2: this.volumeRisq2,
      volumeRisq3: this.volumeRisq3,
      volumeRisq4: this.volumeRisq4,
      volumeRisq5: this.volumeRisq5,
      // prixRisq
      prixRisq1: this.prixRisq1,
      prixRisq2: this.prixRisq2,
      prixRisq3: this.prixRisq3,
      prixRisq4: this.prixRisq4,
      prixRisq5: this.prixRisq5,
      // desGo
      desGo1: this.desGo1,
      desGo2: this.desGo2,
      desGo3: this.desGo3,
      desGo4: this.desGo4,
      desGo5: this.desGo5,
      // prod
      prod1: this.prod1,
      prod2: this.prod2,
      prod3: this.prod3,
      prod4: this.prod4,
      prod5: this.prod5,
      // marges
      marges1: this.marges1,
      marges2: this.marges2,
      marges3: this.marges3,
      marges4: this.marges4,
      marges5: this.marges5,
      // lissage
      lissage1: this.lissage1,
      lissage2: this.lissage2,
      lissage3: this.lissage3,
      lissage4: this.lissage4,
      lissage5: this.lissage5,

    });
  }

  setDate(): void {
    const date = new Date();
    this.risqueGroup.patchValue({myDate: {
    date: {
        year: date.getFullYear(),
        month: date.getMonth() + 1,
        day: date.getDate()}
    }});
  }

  clearDate(): void {
    this.risqueGroup.patchValue({myDate: null});
  }

  onDateChanged(event: IMyDateModel): void {
    // date selected
  }

  onSubmitRisque(data: any) {
    data['years'] = this.yearList;
    console.log(data);
    // const obj = {};
    // obj['risk'] = [data[''], ]
    // obj['risk'] = [data[], ]
    // obj['risk'] = [data[], ]
    // obj['risk'] = [data[], ]
    // consoel.log(obj);
  }
}
