import { Component, OnInit, Input, } from '@angular/core';
import { ReloadService } from '../../_services/reload.sevice';
import { CalculatorService } from '../../_services/calculator.service';
import { Pfc } from '../../_models';
import { FormGroup, FormControl, Validators} from '@angular/forms';
import 'rxjs/add/operator/switchMap';
import { ToastrService } from 'ngx-toastr';
import { Subject } from 'rxjs/Subject';
import { FileService } from '../../_services';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-calculator',
  templateUrl: './calculator.component.html',
  styleUrls: ['./calculator.component.css',
  '../../../assets/css/animate.css',
  '../../../assets/css/bootstrap.min.css',
  '../../../assets/css/customize.css',
  '../../../assets/css/hamburgher.css',
  '../../../assets/css/layout_analytics.css',
  '../../../assets/css/responsive.css',
  '../../../assets/css/theme_analytics.css',
  '../../../assets/css/theme_news.css'

]
})


export class CalculatorComponent implements OnInit {

  myFile: File[];
  fileValid = false;
  uploadForm: FormGroup;
  date: FormControl;
  loading = false;
  currentDate = {};
  pfcs: Pfc[] = [];
  filesize: string[];
  selectedMarketsList: any  = [];
  selectedMarketObj: any = {};
  iterate: number;
  filename: string;
  uploaded = true;
  step: string ;
  step2: string;
  step3: string;
  ecount: string;
  filescounter: any = 0;
  name = 'World';
  myTextVal: string;
  progressbar: any;
  downloaddata: any;
  obj: any;
  obj2: any;
  fileexist: any;
  uplds: boolean;
  message: string;
  download: boolean;
  inputers: any;
  ecount2: string;
  listdownldifles: any = [];
  resultsapi: any;
  typeconvert: any;
  fg: number;
  downloadfilesss: any;
  ecount3: any[];
  private data = new Subject<any>();
  translateyearr: any;

  constructor(private pfcUpload: CalculatorService,
              private toastr: ToastrService,
              private reloadService:  ReloadService,
              private FileDownload: FileService,
              private httpClient: HttpClient
            ) {
             }

  ngOnInit() {
    this.createFormControles();
    this.createForm();
    this.fg = 0;
    this.fileexist = false;
    this.uplds = false;
    this.downloadfilesss = false;
    this.pfcUpload.stringSubject.subscribe(
      data2 => this.progressbar = data2 );
      this.pfcUpload.currentMessage.subscribe(message => this.message = message);
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
    if ( this.ecount2 === 'site' ) { this.inputers = true; }
  }


  @Input()
  set steps3(steps3: any[]) {
    this.ecount3 = steps3;
 console.log('qwerty1231232', this.ecount3);
  }

  @Input()
  set translateyearapp(translateyear: any) {
    this.translateyearr = translateyear;
    console.log('qwerty1231swde232', this.translateyearr);
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
  fileEvent(files2: File[]) {
    this.listdownldifles = [];
    this.progressbar = 0;
    console.log('messageтуццццц', this.message);
    this.myFile = files2;
    console.log('asdadasdqwqwwwwqqqwwwwww', this.selectedMarketsList);
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
      if (this.uplds === false) {

       console.log( 'asdasdasdasdvvvvvv', this.myFile.length );
        if ( this.message === 'true' && (this.selectedMarketsList.length + this.myFile.length ) < 2 ) {

        [].forEach.call(this.myFile, file => { this.selectedMarketsList.push(file);
        console.log('abcd', file.name); });
        } else if ( this.message === 'true' && (this.selectedMarketsList.length + this.myFile.length) > 1 ) {
         this.showError('Erreur ! ne peut pas télécharger plus d un fichier');
        } else if ( this.message === 'false' && (
          this.selectedMarketsList.length + this.myFile.length) < 21 && this. ecount !== 'upload-diff'  ) {
          [].forEach.call(this.myFile, file => { this.selectedMarketsList.push(file);
          console.log('abcd', file.name); });
        } else if (  this.message === 'false' && (
          this.selectedMarketsList.length + this.myFile.length) > 20 && this. ecount !== 'upload-diff' ) {
          this.showError('Erreur ! ne peut pas télécharger plus de 20 fichiers');
        }
      }
      console.log( 'tfytfytfytfyt666' + this.myFile[0].name + this.myFile[0].type);
      console.log( (this.myFile[0].size / Math.pow(1024, 2)).toFixed(2));
      console.log(this.myFile.length);
      this.filescounter = this.selectedMarketsList.length;
        console.log( console.log(this.myFile.length));
    }
  }
  downloadsubmit(ind: number) {
    console.log('assssssss', this.message, this.ecount);
    console.log('indicativex', ind);
    this.pfcUpload.getsFileHeader('vnd.ms-exce', this.obj2).subscribe(
    (data) => { console.log('media', data); this.pfcUpload.downloadUrl(data, this.listdownldifles[ind], 'vnd.ms-excel'); },
    (er) => { console.log('er', er); },
    );
  }


  downloadsubmitsite(string: string) {
    this.pfcUpload.getsFileHeader('vnd.ms-exce', this.obj2).subscribe(
    (data) => { console.log('media', data); this.pfcUpload.downloadUrl(data, string, 'vnd.ms-excel'); },
    (er) => { console.log('er', er); },
    );
  }

  showSuccess(mesaj: string) { this.toastr.success( mesaj); this.uploaded = false; this.fileexist = true; }
  showError(mesaj: string) { this.toastr.error(mesaj); }

  onSubmit(data: any) {
    const formDataPfc: any = new FormData();

    switch ( this.ecount ) {

    case 'upload-convert':
    this.upload_convert(this.message, formDataPfc);
    break;
    case 'upload-sum':
    this.upload_sum(this.message, formDataPfc);
    break;
    case 'upload-translate':
    this.upload_translate(this.message, formDataPfc);
    break;
  }

    this.pfcUpload.myMethod( this.ecount);
    this.pfcUpload.passValue('cristuuuu');
    this.loading = true;
  }

  createFormControles() { this.date = new FormControl('', Validators.required); }
  createForm() { this.uploadForm = new FormGroup({ date: this.date }); }

  upload_convert (multisite: string, file2: any) {
    console.log('gdgdfgdf', this.selectedMarketsList);
this.typeconvert = true;
 this.download = true;
    if (this.myFile) {
      for ( let i = 0; i < this.selectedMarketsList.length; i++ ) {
        const Fterty = new FormData();
        console.log('iiiiiiiiiiiiiiiiiiiiyes', i);
        console.log('length', this.selectedMarketsList.length);
          Fterty.append('files', this.selectedMarketsList[i], this.selectedMarketsList[i].name);
          Fterty.append('multisite',  JSON.parse(multisite));
          this.fg = this.fg + 1 ;
          console.log('fileeeee2', Fterty);
          console.log('gdgdfgdfmultisite', multisite);
          this.uploadfiles(Fterty);
      }
  }}

  upload_sum (multisite: string, file: any) {
    this.typeconvert = false;
    this.download = true;
    console.log('iiiiiiiiiiiiiiiiiiiiyes', typeof  JSON.parse(multisite));
    if (this.myFile) {
      for (let i = 0; i < this.myFile.length; i++) {
      file.append('files', this.myFile[i], this.myFile[i].name);
        file.append('multisite',  JSON.parse(multisite)); }
        this.uploadfiles(file);
    } else { file.append('files', ''); }
  }

  upload_translate (multisite: string, file: any) {
    this.typeconvert = false;
    this.download = true;
    console.log('multisetvalue', typeof  JSON.parse(multisite));
    console.log(this.ecount3);
    console.log(this.translateyearr);
    if (this.myFile) {
      for (let i = 0; i < this.myFile.length; i++) {
      file.append('files', this.myFile[i], this.myFile[i].name);
        file.append('year',  this.ecount3 );
        file.append('years_value',  this.translateyearr );
      }
    this.uploadfiles(file);
    } else { file.append('files', ''); }
  }

uploadfiles (uploadfirm: any) {
  this.pfcUpload.upload(uploadfirm, this.ecount)
  .then(
    res => { this.downloaddata = res; this.obj = JSON.parse(this.downloaddata);
      console.log('dwnldaaaaaa', this.obj.file); this.resultsapi = res;  console.log('dwnldaaaaaa', res);
     if (this.ecount === 'upload-convert') { this.obj2 = this.obj.files; this.listdownldifles.push(this.obj2); } else {
        this.obj2 = this.obj.file; this.listdownldifles.push(this.obj2); }
    }
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
            console.log('dwnldaaaaaa',  this.listdownldifles);
            if ( this.ecount === 'upload-convert' && this.message === 'false') {
              this.downloadfilesss = true ;
            } else { this.downloadfilesss  = false; }
          }
  );
}

}
