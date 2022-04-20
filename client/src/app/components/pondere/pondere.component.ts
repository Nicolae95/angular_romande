import { ReloadService } from './../../_services/reload.sevice';
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Pfc } from '../../_models';
import { FormGroup, FormControl, Validators} from '@angular/forms';
import {Router } from '@angular/router';
import 'rxjs/add/operator/switchMap';
import { ToastrService } from 'ngx-toastr';
import {INgxMyDpOptions, IMyDateModel} from 'ngx-mydatepicker';
import { PondereService } from '../../_services/pondere.service';

@Component({
  selector: 'app-pondere',
  templateUrl: './pondere.component.html',
  styleUrls: [
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/animate.css',
    // '../../../assets/css/styles/theme.css'
  ]
})
export class PondereComponent implements OnInit {
  year: number;
  pfc_market: boolean;
  myFile: File[];
  fileValid = false;
  uploadForm: FormGroup;
  date: FormControl;
  name: FormControl;
  poderFrom: FormControl;
  porderGgroup: FormGroup;
  loading = false;
  currentDate = {};
  pfcs: Pfc[] = [];
  disabData = [];
  dateS: String;
  ponderes: any;
  chart: any;
  yearList: any;


  myOptions: INgxMyDpOptions = {
    dateFormat: 'dd.mm.yyyy',
    disableWeekends: true,
    disableDates: this.disabData,
  };

  constructor(private httpClient: HttpClient,
              private pondereService: PondereService,
              private toastr: ToastrService,
              private router: Router,
              private reloadService: ReloadService) { }

  ngOnInit() {
    const date  =  new Date();
    this.currentDate = { date: { year: date.getFullYear(), month: date.getUTCMonth() + 1, day:  date.getUTCDate() } };
    this.createFormControles();
    this.createForm();
    this.getPoderes();
  }

  getPoderes() {
    this.ponderes = null;
    this.pondereService.getAll().subscribe((data) => {
      this.ponderes  = data;
    this.getPoderes1(data);
    }, );
  }

  getPoderes1(p: any) {
    this.ponderes = p;
    this.getPonderById(this.ponderes[this.ponderes.length - 1]['id']);
  }

  getPonderById(id: number) {
    this.loading = true;
    this.chart = null;
    this.pondereService.getByYear(this.currentDate['date'].year - 1, id).subscribe((data) => {
      this.chart = data; this.loading = false; });
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

  setType(name: boolean) {
    this.pfc_market = name;
  }

  showSuccess(mesaj: string) { this.toastr.success(mesaj); }
  showError(mesaj: string) {   this.toastr.error(mesaj);
  }

  onSubmit(data: any) {
    console.log('data', data);
    this.loading = true;
    const dataPondere: any = new FormData();
    dataPondere.append('name', data['name']);
    if (this.myFile) {
      for (let i = 0; i < this.myFile.length; i++) {
        dataPondere.append('files', this.myFile[i], this.myFile[i].name);
        }
    } else { dataPondere.append('files', ''); }
    dataPondere.append('year', 2017);
    console.log('dataPondere', dataPondere);

    this.pondereService.upload(dataPondere)
    .then(
      res => console.log(res)
    )
    .catch(
      er => { this.loading = false; }
    )
    .then(
      () => { this.showSuccess('Le fichier a été téléchargé.');
              this.loading = false;
              $('#cancel-btn').click();
              $('body').click();
              // this.uploadForm.reset();
              // this.router.navigate(['/pfc']);
              // this.reloadService.change('true');
            }
    );
  }

  createFormControles() {
      this.date = new FormControl('2017', Validators.required);
      this.name = new FormControl('', Validators.required);
      this.poderFrom = new  FormControl();
  }


  createForm() {
    this.uploadForm = new FormGroup({
      date: this.date,
      name: this.name
    });
    this.porderGgroup = new FormGroup({
      poderFrom: this.poderFrom
    });
  }

  onDateChanged(event: IMyDateModel): void {
    this.currentDate = event;
  }

}

