import { Component, OnInit } from '@angular/core';
import { CompanyService } from '../../_services/index';
import { Company } from '../../_models';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import 'rxjs/add/operator/switchMap';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-company',
  templateUrl: './company.component.html',
  styleUrls: [
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css'
  ]
})
export class CompanyComponent implements OnInit {
  company: Company;
  form: FormGroup;
  id: number;
  name:  FormControl;
  address: FormControl;
  zip_code: FormControl;
  nick: FormControl;
  surname: FormControl;
  func: FormControl;
  email: FormControl;
  phone: FormControl;
  data: any;
  load: Boolean = true;


  constructor(private route: ActivatedRoute,
              private companyService: CompanyService,
              private toastr: ToastrService) {
    this.route.params.subscribe( params =>  {this.id = params.id; });
  }


  showSuccess(mesaj: string) { this.toastr.success(mesaj); }
  showError(mesaj: string) { this.toastr.error(mesaj); }

  ngOnInit() {
    this.getCompanyById();
  }

  getCompanyById() {
    this.companyService.getCompanyById(Number(this.id))
        .subscribe(
          (data) => { this.company = data ; this.createFormControles(data); },
          (er) => { console.log(er.error); },
          () => { this.load = false; }
        );
  }
    createFormControles(company: Company) {
    this.name = new FormControl(company.name, Validators.required),
    this.surname = new FormControl(company.surname, Validators.required),
    this.email = new FormControl(company.email, [Validators.required, Validators.pattern('[^ @]*@[^ @]*')]),
    this.updateForm();

  }

  updateForm() {
    this.form = new FormGroup({
      name: this.name,
      address: this.address,
      zip_code: this.zip_code,
      nick: this.nick,
      surname: this.surname,
      func: this.func,
      email: this.email,
      phone: this.phone,
    });
  }

  updateCompany(company: any) {
    this.companyService.update(new Company(company)).subscribe(
      (data) => { this.showSuccess('Les modifications ont été sauvegardées.'); },
      (errores) => { this.showError(errores.name); });
  }
}
