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
  selector: 'app-calculator-multisite',
  templateUrl: './calculator-multisite.component.html',
  styleUrls: ['./calculator-multisite.component.css',
  '../../../assets/css/animate.css',
  '../../../assets/css/bootstrap.min.css',
  '../../../assets/css/customize.css',
  '../../../assets/css/responsive.css',
  '../../../assets/css/theme_analytics.css',
  '../../../assets/css/theme_news.css'
]
})


export class CalculatorMultisiteComponent implements OnInit {
  yeaar: number;
  pfc_market: boolean;
  myFile: File[];
  fileValid = false;
  uploadForm: FormGroup;
  date: FormControl;
  loading = false;
  currentDate = {};
  pfcs: Pfc[] = [];
  disabData = [];
  dateS: String;
  filesize: string[];
  selectedMarketsList: any  = [];
  selectedMarketObj: any = {};
  iterate: number;
  filename: string;
uploaded = true;
step: string ;
ecount: string;
filescounter: any = 0;
name = 'World';
myTextVal: string;
progressbar: any;
downloaddata: any;
fileexist: any;
private data = new Subject<any>();
  constructor(private pfcUpload: CalculatorService,
              private toastr: ToastrService,
              private reloadService:  ReloadService,
              private FileDownload: FileService
            ) {
             }

  ngOnInit() {
    this.createFormControles();
    this.createForm();
    this.ecount = 'upload-convert';
    this.fileexist = false;
    this.pfcUpload.stringSubject.subscribe(
      data2 => this.progressbar = data2
    );
  }

  @Input()
  set steps(steps: string) {
    this.ecount = steps;
    console.log(this.ecount);
  }

  removeSelMarket(ind: number) {
    this.selectedMarketsList.splice(ind, 1);
console.log('1', this.selectedMarketsList);
this.filescounter = this.selectedMarketsList.length;
  }

  fileEvent(files2: File[]) {
    this.myFile = files2;

    console.log('2', this.selectedMarketsList, this.selectedMarketsList.length);
    if (this.myFile == null) {
      this.fileValid = false;
    } else {
      this.fileValid = true;
      console.log( 'tfytfytfytfyt666' + this.myFile[0].name + this.myFile[0].type);
      console.log( (this.myFile[0].size / Math.pow(1024, 2)).toFixed(2));
      console.log(this.myFile.length);
      if ((this.selectedMarketsList.length) < 1) {
      [].forEach.call(this.myFile, file => this.selectedMarketsList.push(file));
      this.filescounter = this.selectedMarketsList.length;
      } else { this.showError('Vous pouvez charger 1 fichier'); }
   for (let i = 0 ; i < this.myFile.length ; i++) {
    this.filename = this.myFile[i].name;
    this.iterate = i;

    if (this.myFile[i].size / Math.pow(1024, 2) > 1) {
      this.filesize[i] = (this.myFile[0].size / Math.pow(1024, 2)).toFixed(2) + ' MB';
    } else {
      this.filesize[i] = (this.myFile[0].size / Math.pow(1024, 1)).toFixed(0) + ' KB';
    }
    console.log(this.filesize[i]);
     }

     console.log( console.log(this.myFile.length));


    }

  }

  setType(ptype: boolean) {
    this.pfc_market = ptype;
  }

  downloadsubmit() {
  this.pfcUpload.downloadUrl(this.downloaddata, 'multisite_sum', 'xlsx');
}

  showSuccess(mesaj: string) { this.toastr.success( mesaj); this.uploaded = false; this.fileexist = true; }
  showError(mesaj: string) { this.toastr.error(mesaj); }

  onSubmit(data: any) {
    this.pfcUpload.myMethod( this.ecount);
    console.log('saaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', this.ecount);
    console.log('eeeeeeeeeeerrrrrrrr', data);
    this.pfcUpload.myMethod(this.ecount);
    this.pfcUpload.passValue('cristuuuu');
    this.loading = true;
    const formDataPfc: any = new FormData();
    formDataPfc.append('pfc_market', 'false');
    if (this.myFile) {
      for (let i = 0; i < this.myFile.length; i++) {
        formDataPfc.append('files', this.myFile[i], this.myFile[i].name);
        formDataPfc.append('multisite',  JSON.parse('true'));
        }
    } else { formDataPfc.append('files', ''); }
    console.log('formDataPfccccccccc', formDataPfc);
    this.pfcUpload.upload(formDataPfc, this.ecount)
    .then(
      res => this.downloaddata = res
    )
    .catch(
      er => { this.loading = false; console.log(this.loading); }
    )
    .then(
      () => { this.showSuccess('Le fichier a été téléchargé.');
              this.loading = false;
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
