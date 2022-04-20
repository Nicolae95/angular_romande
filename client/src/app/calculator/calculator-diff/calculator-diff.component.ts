import { Component, OnInit, Input, } from '@angular/core';
import { ReloadService } from '../../_services/reload.sevice';
import { CalculatorService } from '../../_services/calculator.service';
import { Pfc } from '../../_models';
import { FormGroup, FormControl, Validators} from '@angular/forms';
import 'rxjs/add/operator/switchMap';
import { ToastrService } from 'ngx-toastr';
import { Subject } from 'rxjs/Subject';
import { FileService } from '../../_services';

@Component({
  selector: 'app-calculator-diff',
  templateUrl: './calculator-diff.component.html',
  styleUrls: ['./calculator-diff.component.css',
  '../../../assets/css/animate.css',
  '../../../assets/css/bootstrap.min.css',
  '../../../assets/css/customize.css',
  '../../../assets/css/responsive.css',
  '../../../assets/css/theme_analytics.css',
  '../../../assets/css/theme_news.css'
]
})


export class CalculatorDiffComponent implements OnInit {
  pfc_market: boolean;
  myFile: File[];
  fileValid = false;
  uploadForm: FormGroup;
  date: FormControl;
  loading = false;
  pfcs: Pfc[] = [];
  filesize: string[];
  selectedMarketsList: any  = [];
  selectedMarketObj: any = {};
  selectedMarketsList2: any  = [];
  selectedMarketObj2: any = {};
  iterate: number;
  filename: string;
  uploaded = true;
  step: string ;
  ecount: string;
  filescounter: any = 0;
  filescounter2: any = 0;
  name = 'World';
  myTextVal: string;
  progressbar: any;
  downloaddata: any;
  fileexist: any;
  uplds: boolean;
  obj: any;
  resultsapi: any;
  ecount2: string;
  inputers: any;

  constructor(private pfcUpload: CalculatorService,
              private toastr: ToastrService,
              private reloadService:  ReloadService,
            ) {
             }

  ngOnInit() {
    this.createFormControles();
    this.createForm();
    this.ecount = 'upload-diff';
    this.fileexist = false;
    this.uplds = false;
    this.pfcUpload.stringSubject.subscribe(
      data2 => this.progressbar = data2
    );
  }

  @Input()
  set steps(steps: string) {
    this.ecount = steps;
    console.log(this.ecount);
  }

  @Input()
  set steps2(steps2: string) {
    this.ecount2 = steps2;
    console.log('qwerty', this.ecount2);
 }


  removeSelMarket(ind: number) {
    this.selectedMarketsList.splice(ind, 1);
    console.log(this.selectedMarketsList.length);
    this.filescounter = this.selectedMarketsList.length;
if (this.selectedMarketsList.length === 0) {
  this.fileexist = false;
  this.uploaded = true;
  this.fileValid = false;
}
  }


  removeSelMarket2(ind: number) {
    this.selectedMarketsList2.splice(ind, 1);
    console.log(this.selectedMarketsList2.length);
    this.filescounter2 = this.selectedMarketsList2.length;
if (this.selectedMarketsList2.length === 0) {
  this.fileexist = false;
  this.uploaded = true;
  this.fileValid = false;
}
  }


  fileEvent(files2: File[], typetab: string, typecalculator: string, whattypeis: string) {
    this.myFile = files2;

    console.log(this.uplds);
    if ( this.uplds === true ) {
    this.selectedMarketsList.length = 0;
    this.uplds = false;
    this.uploaded = true;
    }
        console.log('2', this.selectedMarketsList, this.selectedMarketsList.length);
        if (this.myFile == null) {
          this.fileValid = false;
        } else {
          this.fileValid = true;
        if (this.uplds === false && whattypeis === 'none') {
            console.log( 'asdasdasdasdvvvvvv', this.myFile.length );
            if ( (this.selectedMarketsList.length + this.myFile.length ) < 2 ) {
            [].forEach.call(this.myFile, file => { this.selectedMarketsList.push(file);
            console.log('abcd', file.name); });
            } else if ((this.selectedMarketsList.length + this.myFile.length) > 1 ) {
             this.showError('Erreur ! ne peut pas télécharger plus d un fichier');
            }

        } else {
         if ( (this.selectedMarketsList2.length + this.myFile.length) < 21) {
            [].forEach.call(this.myFile, file => { this.selectedMarketsList2.push(file);
            console.log('abcd', file.name); });
          } else if ( (this.selectedMarketsList2.length + this.myFile.length) > 20) {
           this.showError('Erreur ! ne peut pas télécharger plus de 20 fichiers');
         }

        }
        console.log( 'tfytfytfytfyt666' + this.myFile[0].name + this.myFile[0].type);
     console.log( (this.myFile[0].size / Math.pow(1024, 2)).toFixed(2));
          console.log(this.myFile.length);
          this.filescounter = this.selectedMarketsList.length;
          this.filescounter2 = this.selectedMarketsList2.length;
     console.log( console.log(this.myFile.length));
   }
}

  setType(ptype: boolean) {
    this.pfc_market = ptype;
  }

  downloadsubmit() {
  this.pfcUpload.downloadUrl(this.downloaddata, 'multisite_sum', 'xlsx');
}

downloadsubmitsite(string: string) {

  this.pfcUpload.getsFileHeader('vnd.ms-exce', this.obj.file).subscribe(
(data) => { console.log('media', data); this.pfcUpload.downloadUrl(data, string, 'vnd.ms-excel'); },
    (er) => { console.log('er', er); },
  );
}
  showSuccess(mesaj: string) { this.toastr.success( mesaj); this.uploaded = false; this.fileexist = true; }
  showError(mesaj: string) { this.toastr.error(mesaj); }

  onSubmit(data: any) {

    console.log(this.ecount);
    this.loading = true;
    const formDataPfc: any = new FormData();
    if (this.myFile) {
      formDataPfc.append('diff', this.selectedMarketsList[0], this.selectedMarketsList[0].name);
      for (let i = 0; i < this.myFile.length; i++) {
        formDataPfc.append('files', this.selectedMarketsList2[i], this.selectedMarketsList2[i].name);
        }
    } else { formDataPfc.append('files', ''); }

    this.pfcUpload.myMethod( this.ecount);
    console.log('saaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', this.ecount);
    console.log('eeeeeeeeeeerrrrrrrr', data);
    this.pfcUpload.myMethod(this.ecount);
    this.pfcUpload.passValue('cristuuuu');
    this.loading = true;
    this.pfcUpload.upload(formDataPfc, 'upload-diff')
    .then( res => { this.downloaddata = res; this.obj = JSON.parse(this.downloaddata);
        console.log('dwnldaaaaaa', this.obj.file); this.resultsapi = res;  }
    )
    .catch(
      er => { this.loading = false; console.log(this.loading); }
    )
    .then(
      () => { this.showSuccess('Le fichier a été téléchargé.');
              this.loading = false;
              this.uplds = true;
              $('#cancel-btn').click();
              $('body').click();
              // this.router.navigate(['/pfc']);
              this.reloadService.changePfc(true);
            }
    );
  }

  createFormControles() { this.date = new FormControl('', Validators.required); }
  createForm() { this.uploadForm = new FormGroup({ date: this.date }); }

}
