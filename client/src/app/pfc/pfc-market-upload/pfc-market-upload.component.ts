import { ReloadService } from './../../_services/reload.sevice';
import { PfcService } from '../../_services';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { Pfc } from '../../_models';
import { FormGroup, FormControl, Validators} from '@angular/forms';
import { Router } from '@angular/router';
import 'rxjs/add/operator/switchMap';
import { ToastrService } from 'ngx-toastr';
import {INgxMyDpOptions, IMyDateModel} from 'ngx-mydatepicker';

@Component({
  selector: 'app-pfc-market-upload',
  templateUrl: './pfc-market-upload.component.html',
  styleUrls: [
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    //  '../../../assets/css/styles/theme.css'
   ]
})

export class PfcMarketUploadComponent implements OnInit {
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

  myOptions: INgxMyDpOptions = {
    dateFormat: 'dd.mm.yyyy',
    disableWeekends: true,
    disableDates: this.disabData,
  };

  constructor(private httpClient: HttpClient,
              private pfcUpload: PfcService,
              private toastr: ToastrService,
              private router: Router,
              private reloadService:  ReloadService
            ) { }

  ngOnInit() {
    const date =  new Date();
    this.currentDate = { date: { year: date.getFullYear(), month: date.getUTCMonth() + 1, day:  date.getUTCDate() } };
    this.createFormControles();
    this.createForm();
    this.getPfcs();

  }

  getPfcs() {
    this.pfcUpload.getAll().subscribe((data) => {
      this.pfcs = data;
      data.forEach(element => {
        this.disabData.push({
          'day': Number(element['pfc_id'].slice(0, 2)),
          'month': Number(element['pfc_id'].slice(3, 5)),
          'year': Number(element['pfc_id'].slice(6))
        });
      });
    }, );
  }


  fileEvent(files: File[]) {
    this.myFile = files;
    if (this.myFile == null) {
      this.fileValid = false;
    } else {
      this.fileValid = true;
    }
  }

  showSuccess(mesaj: string) { this.toastr.success( mesaj); }
  showError(mesaj: string) { this.toastr.error(mesaj); }

  onSubmit(data: any) {
    this.loading = true;
    const formDataPfc: any = new FormData();
    formDataPfc.append('pfc_market', 'true');
    if (this.myFile) {
      for (let i = 0; i < this.myFile.length; i++) {
        formDataPfc.append('files', this.myFile[i], this.myFile[i].name);
        }
    } else { formDataPfc.append('files', ''); }
    if (String(data['date']['date']['month']).length === 1) {
      const months = '0' + String(data['date']['date']['month']);
      formDataPfc.append('date', String(data['date']['date']['day']) + '.' + months + '.' + String(data['date']['date']['year']));
    } else {
      const months = String(data['date']['date']['month']);
      formDataPfc.append('date', String(data['date']['date']['day']) + '.' + months + '.' + String(data['date']['date']['year']));
    }
    this.pfcUpload.upload(formDataPfc)
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
              this.reloadService.changePfc(true);

            }
    );

  }

  createFormControles() {
      this.date = new FormControl('', Validators.required);
  }

  createForm() {
    this.uploadForm = new FormGroup({
      date: this.date,
    });
  }

  onDateChanged(event: IMyDateModel): void {
    this.currentDate = event;
  }

}
