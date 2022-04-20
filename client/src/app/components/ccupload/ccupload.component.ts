import { Meter } from './../../_models/meter';
import { CcService, CustomObservable, UserService, FileService } from '../../_services';
import { environment } from '../../../environments/environment';
import { Component, OnInit,  Pipe, PipeTransform} from '@angular/core';
import { CompanyService} from '../../_services/index';
import { Company, User, Admin } from '../../_models';
import { FormGroup, FormControl, Validators} from '@angular/forms';
import 'rxjs/add/operator/switchMap';
import {INgxMyDpOptions, IMyDateModel} from 'ngx-mydatepicker';
import { ToastrService } from 'ngx-toastr';
import { Site } from '../../_models/site';
import { OfferService } from '../../_services/offer.service';
import { SearchService } from '../../_services';
import { Pagination } from '../../_models/pagination';
import * as XLSX from 'ts-xlsx';
import { isNumber } from 'util';

const PADDING = '000000';


// @Pipe({ name: 'myCurrency' })


@Component({
  selector: 'app-ccupload',
  templateUrl: './ccupload.component.html',
  styleUrls: [
    //  '../../../assets/css/styles/nexus.css',
    //  '../../../assets/css/styles/layout.css',
    //   '../../../assets/css/styles/theme.css'
    ]
})
export class CcUploadComponent implements OnInit, PipeTransform {

  curentCompany: Company;
  myFile: Array<File>;
  myFileEx: Array<File>;
  meters: Array<Meter>;
  metersUpload: Array<Meter>;
  year: number;
  monthh: Date;
  show = true;
  mensue = false;
  hphc = false;
  onlyname = false;
  myform: FormGroup;
  yearf: FormControl;
  name: FormControl;
  volume: FormControl;
  year1: FormControl;  year2: FormControl; year3: FormControl;  year4: FormControl;  year5: FormControl;  year6: FormControl;
  data1: FormControl;  data2: FormControl;  data3: FormControl;  data4: FormControl;  data5: FormControl;  data6: FormControl;
  hpmonth1: FormControl; hpmonth2: FormControl; hpmonth3: FormControl; hpmonth4: FormControl; hpmonth5: FormControl;
  hpmonth7: FormControl; hpmonth8: FormControl; hpmonth9: FormControl; hpmonth10: FormControl; hpmonth11: FormControl;
  hpmonth6: FormControl; hpmonth12: FormControl;
  // hcmonth1: FormControl; hcmonth2: FormControl; hcmonth3: FormControl; hcmonth4: FormControl; hcmonth5: FormControl;
  // hcmonth7: FormControl; hcmonth8: FormControl; hcmonth9: FormControl; hcmonth10: FormControl; hcmonth11: FormControl;
  // hcmonth6: FormControl; hcmonth12: FormControl;
   multisite: FormControl;
  siteform: FormControl;
  pods: FormControl;
  company: FormControl;
  companies: Company;
  currentUser: User;
  loading = false;
  fileValid = false;
  fileValidEx = false;
  nameValid = false;
  primesSettings = {};
  yearList: Array<number> = [];
  monthList: Array<string> = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  uploadForm = new FormGroup ({
    file1: new FormControl(),
    name: new FormControl()
  });
  podsList = [];
  podsSettings = {};
  selectedpods = [];
  mensuef: FormControl;
  hphcf: FormControl;
  onlynamef: FormControl;
  message: string;
  myOptions: INgxMyDpOptions = {
    dateFormat: 'dd/mm/yyyy',
    showTodayBtn: false,
    satHighlight: true,
    sunHighlight: true,
    markCurrentDay: true,
    markCurrentMonth: true,
    markCurrentYear: true,
    monthSelector: false,
    yearSelector: true,
  };
  tabOfferForm: FormGroup;
  ccProfilHistorique: FormControl;
  nameOffer =  '';
  siteName: string;
  translate = false;
  tous = [];
  environment = environment.api_url + '/media/';
  site: Pagination<Site>;
  offert: any;
  pag = 1;
  nr: number;
  nameSearch = '';
  ccName = '';
  boxSite = false;
  boxMultiSite = false;
  curentClient: Admin;
  bifa1 = false;
  bifa2 = false;
  fBifa1: FormControl;
  fBifa2: FormControl;
  pkDelete: any;
  deleteCC: any;
  myEx: any;
  pattern = '\([0-9]*[\']*[0-9]*\)*?';
  file: File;
  fileReader: any;
  sumaMonths: any =  0;
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
  incomingfile(event) { this.file = event.target.files[0]; }


  constructor(private ccService: CcService,
              private companyService: CompanyService,
              private offerService: OfferService,
              private fileService: FileService,
              private searchService: SearchService,
              private customObservable: CustomObservable,
              private toastr: ToastrService,
              private userService: UserService
            ) {
              this.DECIMAL_SEPARATOR = '.';
              this.THOUSANDS_SEPARATOR = '\'';
              this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
              this.nr = this.currentUser.nr;
  }


  ngOnInit() {
     this.year = new Date().getFullYear();
    let y: number;
    for (y = this.year; y < this.year + 6; y++) {
      this.yearList.push(y);
    }

    this.createFormControles();
    this.createForm();
    this.setDate();
    this.getCompany();
    this.onChanges();
    this.yearsList();
  }

  getCompany() {
    this.ccService.isCompany.subscribe(
      (data) => {
        this.podsList = [];
        this.getMetersByCompany(data);
        this.getCcByCompany(data);
        this.getMetersUploadByCompany(data);
        this.curentCompany = data;
      },
      (err) => {
        this.podsList = [];
        this.getMetersByCompany(null);
        this.getMetersUploadByCompany(null);
        this.curentCompany = null;
        this.getCcByCompany(null);
      }
    );
  }

  yearsList(): void {
    this.myform.get('yearf').valueChanges
    .debounceTime(100)
    .distinctUntilChanged()
    .subscribe(year => {
      if (year > 2000 && year < 3000 ) {
        this.yearList = [];
        for (let y = year + 1; y < year + 7; y++) {
          this.yearList.push(y);
        }
      }
    });
  }

  showSuccess(mesaj: string) { this.toastr.success(mesaj); }
  showError(mesaj: string) { this.toastr.error(mesaj); }

  onChanges(): void {
    this.tabOfferForm.get('ccProfilHistorique').valueChanges
    .debounceTime(100)
    .distinctUntilChanged()
    .subscribe(val => {
      this.observableSource(val);
    });
  }

  observableSource(name: string) {
    this.nameSearch = '';
    this.nameSearch = name;
      this.searchService.searchNameSite(this.curentCompany.id, name, String(this.year), this.pag, this.nr)
      .subscribe (
        (data) => {
          this.site = data;
          console.log('site', this.site);
        },
        (er) => { console.log('er', er.error),  this.nameOffer = null; },
      );
  }

  send(site: any) {
    if (site === null ) { this.customObservable.changeVolume(null); }
    this.site = null;
    this.site = site;
    this.customObservable.changeSite(null);
    this.customObservable.changeSite(site);
  }



  pags(pag) {
    this.pag = pag;
    this.observableSource(this.nameSearch);
  }

  setNumberperPag(nr: number) {
    this.nr = Number(nr);
    this.userService.chnageNrPerPag(this.currentUser, nr).subscribe((data) => { this.pags(1); });
  }

  getCcByCompany(cmp: Company) {
    if (cmp) {
      this.getOffer(cmp.id, this.ccName, this.nameOffer, this.year);
      this.onChanges();
    }
  }


  getOffer(id: number, cc: any, siteName: any, year: any ) {
    this.ccName = cc;
    this.nameOffer = siteName;
    this.year = year;
    this.siteName = siteName;
    this.offerService.getByCompany(id, cc, siteName, year, this.pag, this.nr).subscribe(
      (data) => {
        this.offert = data;
      },
      (err) => { console.log(err); }
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
    this.addValueOfTable();
    this.myform.get('volume').setValue('0');
  }

  getMetersByCompany(cmp: Company) {
    if (cmp) {
      this.meters = [];
      this.companyService.getMetersByCompany(cmp.id).subscribe(
        (data) => { this.meters = data; }
      );
    }
  }

  getMetersUploadByCompany(cmp: Company) {
    if (cmp) {
      this.meters = [];
      this.companyService.getMetersUploadByCompany(cmp.id).subscribe(
        (data) => {
          this.metersUpload = data;
          this.multiSelect(data);
        }
      );
    }
  }

  onSubmit(data: any) {
    this.loading = true;
    let formData: any = new FormData();
    formData = this.createFormData(data);

    this.ccService.upload(formData)
      .then(
        res => {this.loading = false;
                $('#Update').click();
                $('body').click();
                this.resetCcUpload();
                this.getCompany();
                this.observableSource(this.nameSearch);

        }
      )
      .catch(
        er => {  this.loading = false;
                 this.showError(er.name);
                $('#Update').click();
                $('body').click();
                this.resetCcUpload();
                this.getCompany();
                this.observableSource(this.nameSearch);

              }
      )
      .then(
        () => { this.showSuccess('La nouvelle CC a été ajoutée.');
                this.loading = false;
                $('#Update').click();
                $('body').click();
                this.resetCcUpload();
                this.getCompany();
                this.observableSource(this.nameSearch);
              }
      );
  }

  resetCcUpload() {
    this.myform.get('name').reset();
    this.myform.get('data1').setValue(0);
    this.myform.get('data2').setValue(0);
    this.myform.get('data3').setValue(0);
    this.myform.get('data4').setValue(0);
    this.myform.get('data5').setValue(0);
    this.myform.get('data6').setValue(0);
    this.bifa1 = false;
    this.bifa2 = false;
    this.mensue = false;
    this.hphc = false;
    this.onlyname = false;
    this.boxMultiSite = false;
    this.boxSite = false;
    this.myform.get('siteform').setValue('');
    this.myform.get('multisite').setValue('');
    console.log('podsList', this.podsList);
    this.podsList.length = 0;
    this.podsList = [];
    console.log('podsList', this.podsList);

  }

  createFormData(data: any): FormData {
    const formData: any = new FormData();
    if (this.myFile) {
      for (let i = 0; i < this.myFile.length; i++) {
        formData.append('files', this.myFile[i], this.myFile[i].name);
      }
    } else { formData.append('files', ''); }

    const meters = [];
    data.pods.forEach(element => {
      meters.push(element['id']);
    });

    formData.append('year', data['yearf']);
    formData.append('sum_exists', this.myFile.length === 1);
    formData.append('site', data['name']);
    formData.append('meters', meters);
    formData.append('multisite', data['multisite']);
    formData.append('company', data['company']['id']);
    formData.append('years', this.yearList);
    formData.append('mensue', this.mensue);
    formData.append('hphc', this.hphc);
    formData.append('onlyname', this.onlyname);
    formData.append('dates', [data.data1, data.data2, data.data3, data.data4, data.data5, data.data6]);

    if (this.mensue || this.hphc) {
      // console.log('ura',   data.hpmonth1,  data.hpmonth2,  data.hpmonth3,
      // data.hpmonth4,  data.hpmonth5,  data.hpmonth6,
      // data.hpmonth7,  data.hpmonth8,  data.hpmonth9,
      // data.hpmonth10, data.hpmonth11, data.hpmonth12);
      try {
        formData.append('months', [
          data.hpmonth1  =  Number(this.hpmonth1.value.replace('\'', '')),
          data.hpmonth2  =  Number(this.hpmonth2.value.replace('\'', '')),
          data.hpmonth3  =  Number(this.hpmonth3.value.replace('\'', '')),
          data.hpmonth4  =  Number(this.hpmonth4.value.replace('\'', '')),
          data.hpmonth5  =  Number(this.hpmonth5.value.replace('\'', '')),
          data.hpmonth6  =  Number(this.hpmonth6.value.replace('\'', '')),
          data.hpmonth7  =  Number(this.hpmonth7.value.replace('\'', '')),
          data.hpmonth8  =  Number(this.hpmonth8.value.replace('\'', '')),
          data.hpmonth9  =  Number(this.hpmonth9.value.replace('\'', '')),
          data.hpmonth10 =  Number(this.hpmonth10.value.replace('\'', '')),
          data.hpmonth11 =  Number(this.hpmonth11.value.replace('\'', '')),
          data.hpmonth12 =  Number(this.hpmonth12.value.replace('\'', '')),
        ]);
      } catch (error) {}


    } else { formData.append('months', ''); }


    if (this.onlyname) { formData.append('volume', data.volume); } else { formData.append('volume', ''); }


    return formData;
  }

  multiSelect(meters: Array<Meter>) {
    this.podsList.length = 0;
    this.podsList = [];
    meters.forEach(meter => {
      this.podsList.push({'id' : meter['id'], 'itemName' : meter['meter_id'] + ' - ' + meter['address']});
    });

    this.selectedpods = [];

    this.podsSettings = {
      singleSelection: false,
      text: 'Choisir risque',
      selectAllText: 'Tout sélectionner',
      unSelectAllText: 'Tout désélectionner',
      classes: 'myclass custom-class '
    };

    this.primesSettings = {
      singleSelection: false,
      text: 'Choisir pods',
      selectAllText: 'Tout sélectionner',
      unSelectAllText: 'Tout désélectionner',
      // enableSearchFilter: true,
      classes: 'myclass custom-class '
    };

  }

  changeBoxM(mensue: boolean) {
    this.mensue = mensue;
    this.hphc = false;
    this.onlyname = !mensue;
    this.fileValid = mensue;
    this.clearValueOfTable();
    this.myform.get('volume').setValue(0);
    this.myFile = [];
    // this.onChangeshpmonth();
  }

  changeBoxH(hphc: boolean) {
    this.mensue = false;
    this.hphc = hphc;
    this.onlyname = false;
    this.fileValid = hphc;
    this.myform.get('volume').setValue(0);
    this.myFile = [];
    this.clearValueOfTable();
  }

  changeBoxO(onlyname: boolean) {
    this.mensue = !onlyname;
    this.hphc = false;
    this.onlyname = onlyname;
    this.fileValid = onlyname;
    this.addValueOfTable();
    this.myform.get('volume').setValue(null);
    this.myFile = [];
  }


  valid () {
    if (name == null) {
      this.nameValid = false;
    } else {
      this.nameValid = true;
    }
  }



  sfile(site: any) {
    // sfile/' +  id + '/'
    this.fileService.getsFileHeader('sfile/' +  site.id + '/', 'vnd.ms-exce').subscribe(
      (data) => { console.log('sfile', data); this.fileService.downloadUrl(data, site.sfile, 'vnd.ms-excel'); },
      (er) => { console.log('er', er); },
    );
  }


  media(fileName: string) {
    if (fileName) {
      this.fileService.getsFileHeader('demo/' + fileName + '/', 'vnd.ms-exce').subscribe(
        (data) => { console.log('media', data); this.fileService.downloadUrl(data, fileName + '.xlsx', 'vnd.ms-excel'); },
        (er) => { console.log('er', er); },
      );
    }
  }



  onItemSelect(item: any) {}
  OnItemDeSelect(item: any) {}
  onSelectAll(items: any) {}
  onDeSelectAll(items: any) {}


  clearValueOfTable() {
    this.myform.get('hpmonth1').setValue(null);
    this.myform.get('hpmonth2').setValue(null);
    this.myform.get('hpmonth3').setValue(null);
    this.myform.get('hpmonth4').setValue(null);
    this.myform.get('hpmonth5').setValue(null);
    this.myform.get('hpmonth6').setValue(null);
    this.myform.get('hpmonth7').setValue(null);
    this.myform.get('hpmonth8').setValue(null);
    this.myform.get('hpmonth9').setValue(null);
    this.myform.get('hpmonth10').setValue(null);
    this.myform.get('hpmonth11').setValue(null);
    this.myform.get('hpmonth12').setValue(null);
  }

  addValueOfTable() {
    this.myform.get('hpmonth1').setValue('0');
    this.myform.get('hpmonth2').setValue('0');
    this.myform.get('hpmonth3').setValue('0');
    this.myform.get('hpmonth4').setValue('0');
    this.myform.get('hpmonth5').setValue('0');
    this.myform.get('hpmonth6').setValue('0');
    this.myform.get('hpmonth7').setValue('0');
    this.myform.get('hpmonth8').setValue('0');
    this.myform.get('hpmonth9').setValue('0');
    this.myform.get('hpmonth10').setValue('0');
    this.myform.get('hpmonth11').setValue('0');
    this.myform.get('hpmonth12').setValue('0');
  }

  onDateChanged(event: IMyDateModel): void {}

  setDate(): void {
    const date = new Date();
    this.myform.patchValue({myDate: {
    date: {
        year: date.getFullYear(),
        month: date.getMonth() + 1,
        day: date.getDate()}
    }});
  }

  clearDate(): void {
    // Clear the date using the patchValue function
    this.myform.patchValue({myDate: null});
  }


  createFormControles() {
    this.yearf = new FormControl(this.year - 1, Validators.required);
    this.name = new FormControl('', [Validators.required , Validators.minLength(3), Validators.maxLength(100)]);
    this.volume = new FormControl(0, Validators.required);
    this.multisite = new FormControl();
    this.siteform = new FormControl();
    this.fBifa1 = new FormControl();
    this.fBifa2 = new FormControl();
    this.company = new FormControl();
    this.year1 = new FormControl(this.yearList[0], Validators.required);  this.data1 = new FormControl(0, Validators.required);
    this.year2 = new FormControl(this.yearList[1], Validators.required);  this.data2 = new FormControl(0, Validators.required);
    this.year3 = new FormControl(this.yearList[2], Validators.required);  this.data3 = new FormControl(0, Validators.required);
    this.year4 = new FormControl(this.yearList[3], Validators.required);  this.data4 = new FormControl(0, Validators.required);
    this.year5 = new FormControl(this.yearList[4], Validators.required);  this.data5 = new FormControl(0, Validators.required);
    this.year6 = new FormControl(this.yearList[5], Validators.required);  this.data6 = new FormControl(0, Validators.required);
    this.hpmonth1  = new FormControl('', [Validators.required ]);
    this.hpmonth2  = new FormControl('', [Validators.required ]);
    this.hpmonth3  = new FormControl('', [Validators.required ]);
    this.hpmonth4  = new FormControl('', [Validators.required ]);
    this.hpmonth5  = new FormControl('', [Validators.required ]);
    this.hpmonth6  = new FormControl('', [Validators.required ]);
    this.hpmonth7  = new FormControl('', [Validators.required ]);
    this.hpmonth8  = new FormControl('', [Validators.required ]);
    this.hpmonth9  = new FormControl('', [Validators.required ]);
    this.hpmonth10 = new FormControl('', [Validators.required ]);
    this.hpmonth11 = new FormControl('', [Validators.required ]);
    this.hpmonth12 = new FormControl('', [Validators.required ]);
    // this.hcmonth1 = new FormControl(0, Validators.required);   this.hcmonth2 = new FormControl(0, Validators.required);
    // this.hcmonth3 = new FormControl(0, Validators.required);   this.hcmonth4 = new FormControl(0, Validators.required);
    // this.hcmonth5 = new FormControl(0, Validators.required);   this.hcmonth6 = new FormControl(0, Validators.required);
    // this.hcmonth7 = new FormControl(0, Validators.required);   this.hcmonth8 = new FormControl(0, Validators.required);
    // this.hcmonth9 = new FormControl(0, Validators.required);   this.hcmonth10 = new FormControl(0, Validators.required);
    // this.hcmonth11 = new FormControl(0, Validators.required);  this.hcmonth12 = new FormControl(0, Validators.required);
    this.hphcf = new FormControl(false, Validators.required);  this.onlynamef = new FormControl(false, Validators.required);
    this.pods = new FormControl(Validators.required); this.mensuef = new FormControl(false, Validators.required);
    this.ccProfilHistorique = new FormControl();
  }

  createForm() {
    this.tabOfferForm = new FormGroup({
      ccProfilHistorique: this.ccProfilHistorique,
    });

    this.myform = new FormGroup({
      yearf: this.yearf,
      name: this.name,
      volume: this.volume,
      company: this.company,
      multisite: this.multisite,
      siteform: this.siteform,
      fBifa1: this.fBifa1,
      fBifa2: this.fBifa2,
      data1: this.data1, year1: this.year1,
      data2: this.data2, year2: this.year2,
      data3: this.data3, year3: this.year3,
      data4: this.data4, year4: this.year4,
      data5: this.data5, year5: this.year5,
      data6: this.data6, year6: this.year6,
      hpmonth1: this.hpmonth1,  hpmonth2: this.hpmonth2,    hpmonth3: this.hpmonth3,    hpmonth4: this.hpmonth4,
      hpmonth5: this.hpmonth5,  hpmonth6: this.hpmonth6,    hpmonth7: this.hpmonth7,    hpmonth8: this.hpmonth8,
      hpmonth9: this.hpmonth9,  hpmonth10: this.hpmonth10,  hpmonth11: this.hpmonth11,  hpmonth12: this.hpmonth12,
      // hcmonth1: this.hcmonth1,  hcmonth2: this.hcmonth2,    hcmonth3: this.hcmonth3,    hcmonth4: this.hcmonth4,
      // hcmonth5: this.hcmonth5,  hcmonth6: this.hcmonth6,    hcmonth7: this.hcmonth7,    hcmonth8: this.hcmonth8,
      // hcmonth9: this.hcmonth9,  hcmonth10: this.hcmonth10,  hcmonth11: this.hcmonth11,  hcmonth12: this.hcmonth12,
      pods: this.pods,
      mensuef: this.mensuef,
      hphcf: this.hphcf,
      onlynamef: this.onlynamef,
    });
    this.onChangeshpmonth();
  }

  // exempleFile(fileName: string) {
  //     if (fileName) {
  //       window.open(this.environment + 'demo/' + fileName);
  //       this.showSuccess('Fichier a été téléchargé');
  //     }
  // }

  deleteConfirm(site: any) {
    this.deleteCC = true;
    this.pkDelete = site;
  }

  delete(site: any) {
    this.loading = true;
     this.ccService.deleteSite(site.id).subscribe(
       (data) => {
        this.showSuccess('CC profil historique a été supprimé');
        this.loading = false;
        this.observableSource(this.nameSearch);
        $('#dels').click();
        $('body').click();
      },
      (e) => {
        this.showSuccess('CC profil historique a été supprimé');
        this.loading = false;
        this.observableSource(this.nameSearch);
        $('#dels').click();
        $('body').click();
      });
  }


    Upload() {
      this.fileReader = null;
      this.fileReader = new FileReader();
        this.fileReader.onload = (e) => {
            const arrayBuffer = this.fileReader.result;
            const data = new Uint8Array(arrayBuffer);
            const arr = new Array();
            for (let i = 0; i !== data.length; ++i) { arr[i] = String.fromCharCode(data[i]); }
            const bstr = arr.join('');
            const workbook = XLSX.read(bstr, {type: 'binary'});
            const first_sheet_name = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[first_sheet_name];
            this.myEx = XLSX.utils.sheet_to_json(worksheet, {raw: true});
            console.log('this.myEx[0]', this.myEx);
            for (const key in this.myEx[0]) {
              if ( this.myEx[0].hasOwnProperty(key)) {
                const element =  this.myEx[0][key];
                if ( key === 'Jan' ) {
                  const finis = this.transform(this.onlyNumbers(String(element)).list, 0);
                  this.myform.get('hpmonth1').setValue(finis);
                 }
                if ( key === 'Fev' ) {
                  const finis = this.transform(this.onlyNumbers(String(element)).list, 0);
                  this.myform.get('hpmonth2').setValue(finis);
                 }
                if ( key === 'Mar' ) {
                  const finis = this.transform(this.onlyNumbers(String(element)).list, 0);
                  this.myform.get('hpmonth3').setValue(finis);
                 }
                if ( key === 'Avr' ) {
                  const finis = this.transform(this.onlyNumbers(String(element)).list, 0);
                  this.myform.get('hpmonth4').setValue(finis);
                 }
                if ( key === 'Mai' ) {
                  const finis = this.transform(this.onlyNumbers(String(element)).list, 0);
                  this.myform.get('hpmonth5').setValue(finis);
                 }
                if ( key === 'Jun' ) {
                  const finis = this.transform(this.onlyNumbers(String(element)).list, 0);
                  this.myform.get('hpmonth6').setValue(finis);
                 }
                if ( key === 'Jul' ) {
                  const finis = this.transform(this.onlyNumbers(String(element)).list, 0);
                  this.myform.get('hpmonth7').setValue(finis);
                 }
                if ( key === 'Aug' ) {
                  const finis = this.transform(this.onlyNumbers(String(element)).list, 0);
                  this.myform.get('hpmonth8').setValue(finis);
                 }
                if ( key === 'Sep' ) {
                  const finis = this.transform(this.onlyNumbers(String(element)).list, 0);
                  this.myform.get('hpmonth9').setValue(finis);
                 }
                if ( key === 'Oct' ) {
                  const finis = this.transform(this.onlyNumbers(String(element)).list, 0);
                  this.myform.get('hpmonth10').setValue(finis);
                 }
                if ( key === 'Nov' ) {
                  const finis = this.transform(this.onlyNumbers(String(element)).list, 0);
                  this.myform.get('hpmonth11').setValue(finis);
                 }
                if ( key === 'Dec' ) {
                  const finis = this.transform(this.onlyNumbers(String(element)).list, 0);
                  this.myform.get('hpmonth12').setValue(finis);
                 }
                  // this.myform.get('hpmonth1').setValue(finis); this.sum();
                this.sum();
              }
            }
            // const hp1  = Number(this.hpmonth1.value);
            // const hp2  = Number(this.hpmonth2.value);
            // const hp3  = Number(this.hpmonth3.value);
            // const hp4  = Number(this.hpmonth4.value);
            // const hp5  = Number(this.hpmonth5.value);
            // const hp6  = Number(this.hpmonth6.value);
            // const hp7  = Number(this.hpmonth7.value);
            // const hp8  = Number(this.hpmonth8.value);
            // const hp9  = Number(this.hpmonth9.value);
            // const hp10 = Number(this.hpmonth10.value);
            // const hp11 = Number(this.hpmonth11.value);
            // const hp12 = Number(this.hpmonth12.value);
            // const toatal = hp1 + hp2 + hp3 + hp4 + hp5 + hp6 + hp7 + hp8 + hp9 + hp10 + hp11 + hp12;
            // this.sumaMonths = String(toatal).replace(/[^0-9.]/g, '');
            // this.sumaMonths = this.transform(this.sumaMonths, 0);
        };
        this.fileReader.readAsArrayBuffer(this.file);
    }


    onlyNumbers(arr: any) {
      if (arr) {
        let list = '';
        let count = null;
        for (let i = 0; i < arr.length; i++) {
          if (i === 0) {
            if (arr[i].charCodeAt(0) !== '-'.charCodeAt(0)) {
                const str = (<any>arr)[i].replace(/\D+/g, ''); if (str !== '')  {list += str; }
            } else { list += '-'; }
          } else {
             if (arr[i] !== '.') {
              const str = (<any>arr)[i].replace(/\D+/g, ''); if (str !== '')  {list += str; }
              if (count !== null) { count = count + 1; }
            } else { list += '.'; count = 0; }
          }
        }
        if (count === null) { count = 0; }
        if (list === null || undefined) { list = ''; }
        const retur = {'list': list, 'count': count};
        setTimeout(() => { this.sum(); }, 2000);
        return retur;
        // return list;
      }
    }

    onChangeshpmonth(): void {
      this.myform.get('hpmonth1').valueChanges.debounceTime(1500).distinctUntilChanged().subscribe(val => { if (val !== '') {
        try {
          const finis = this.transform(this.onlyNumbers(val).list, this.onlyNumbers(val).count);
          this.myform.get('hpmonth1').setValue(finis); this.sum();
        } catch (error) { }
      } });

      this.myform.get('hpmonth2').valueChanges.debounceTime(1500).distinctUntilChanged().subscribe(val => { if (val !== '') {
        try {
          const finis = this.transform(this.onlyNumbers(val).list, this.onlyNumbers(val).count);
          this.myform.get('hpmonth2').setValue(finis); this.sum();
        } catch (error) {}
      } });

      this.myform.get('hpmonth3').valueChanges.debounceTime(1500).distinctUntilChanged().subscribe(val => { if (val !== '') {
        try {
        const finis = this.transform(this.onlyNumbers(val).list, this.onlyNumbers(val).count);
        this.myform.get('hpmonth3').setValue(finis); this.sum();
     } catch (error) {}

      } });

      this.myform.get('hpmonth4').valueChanges.debounceTime(1500).distinctUntilChanged().subscribe(val => { if (val !== '') {
        try {
          const finis = this.transform(this.onlyNumbers(val).list, this.onlyNumbers(val).count);
          this.myform.get('hpmonth4').setValue(finis); this.sum();
      } catch (error) {}
      }});

      this.myform.get('hpmonth5').valueChanges.debounceTime(1500).distinctUntilChanged().subscribe(val => { if (val !== '') {
        try {
        const finis = this.transform(this.onlyNumbers(val).list, this.onlyNumbers(val).count);
        this.myform.get('hpmonth5').setValue(finis); this.sum();
     } catch (error) {}
      }});

      this.myform.get('hpmonth6').valueChanges.debounceTime(1500).distinctUntilChanged().subscribe(val => { if (val !== '') {
        try {
        const finis = this.transform(this.onlyNumbers(val).list, this.onlyNumbers(val).count);
        this.myform.get('hpmonth6').setValue(finis); this.sum();
     } catch (error) {}
      }});

      this.myform.get('hpmonth7').valueChanges.debounceTime(1500).distinctUntilChanged().subscribe(val => { if (val !== '') {
        try {
        const finis = this.transform(this.onlyNumbers(val).list, this.onlyNumbers(val).count);
        this.myform.get('hpmonth7').setValue(finis); this.sum();
     } catch (error) {}
      }});

      this.myform.get('hpmonth8').valueChanges.debounceTime(1500).distinctUntilChanged().subscribe(val => { if (val !== '') {
        try {
        const finis = this.transform(this.onlyNumbers(val).list, this.onlyNumbers(val).count);
        this.myform.get('hpmonth8').setValue(finis); this.sum();
     } catch (error) {}
      }});

      this.myform.get('hpmonth9').valueChanges.debounceTime(1500).distinctUntilChanged().subscribe(val => { if (val !== '') {
        try {
        const finis = this.transform(this.onlyNumbers(val).list, this.onlyNumbers(val).count);
        this.myform.get('hpmonth9').setValue(finis); this.sum();
     } catch (error) {}
      }});

      this.myform.get('hpmonth10').valueChanges.debounceTime(1500).distinctUntilChanged().subscribe(val => { if (val !== '') {
        try {
        const finis = this.transform(this.onlyNumbers(val).list, this.onlyNumbers(val).count);
        this.myform.get('hpmonth10').setValue(finis); this.sum();
     } catch (error) {}
      }});

      this.myform.get('hpmonth11').valueChanges.debounceTime(1500).distinctUntilChanged().subscribe(val => { if (val !== '') {
        try {
        const finis = this.transform(this.onlyNumbers(val).list, this.onlyNumbers(val).count);
        this.myform.get('hpmonth11').setValue(finis); this.sum();
     } catch (error) {}
      }});

      this.myform.get('hpmonth12').valueChanges.debounceTime(1500).distinctUntilChanged().subscribe(val => { if (val !== '') {
        try {
        const finis = this.transform(this.onlyNumbers(val).list, this.onlyNumbers(val).count);
        this.myform.get('hpmonth12').setValue(finis); this.sum();
       } catch (error) {}
       }});

    }

    sum() {
      if (this.hpmonth1.valid  === true &&
          this.hpmonth2.valid  === true &&
          this.hpmonth3.valid  === true &&
          this.hpmonth4.valid  === true &&
          this.hpmonth5.valid  === true &&
          this.hpmonth6.valid  === true &&
          this.hpmonth7.valid  === true &&
          this.hpmonth8.valid  === true &&
          this.hpmonth9.valid  === true &&
          this.hpmonth10.valid === true &&
          this.hpmonth11.valid === true &&
          this.hpmonth12.valid === true ) {

          try {
            const hp1  = Number(this.hpmonth1.value.replace(/[^0-9.]/g,  ''));
            const hp2  = Number(this.hpmonth2.value.replace(/[^0-9.]/g,  ''));
            const hp3  = Number(this.hpmonth3.value.replace(/[^0-9.]/g,  ''));
            const hp4  = Number(this.hpmonth4.value.replace(/[^0-9.]/g,  ''));
            const hp5  = Number(this.hpmonth5.value.replace(/[^0-9.]/g,  ''));
            const hp6  = Number(this.hpmonth6.value.replace(/[^0-9.]/g,  ''));
            const hp7  = Number(this.hpmonth7.value.replace(/[^0-9.]/g,  ''));
            const hp8  = Number(this.hpmonth8.value.replace(/[^0-9.]/g,  ''));
            const hp9  = Number(this.hpmonth9.value.replace(/[^0-9.]/g,  ''));
            const hp10 = Number(this.hpmonth10.value.replace(/[^0-9.]/g,  ''));
            const hp11 = Number(this.hpmonth11.value.replace(/[^0-9.]/g,  ''));
            const hp12 = Number(this.hpmonth12.value.replace(/[^0-9.]/g,  ''));

            const toatal = hp1 + hp2 + hp3 + hp4 + hp5 + hp6 + hp7 + hp8 + hp9 + hp10 + hp11 + hp12;
            this.sumaMonths = String(toatal).replace(/[^0-9.]/g, '');
            this.sumaMonths = this.transform(toatal, 0);
          } catch (error) { }
        }
    }


}

