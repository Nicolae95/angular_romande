import { CompanyService, UserService , CcService, CustomObservable, SearchService} from '../../_services/index';
import { Company, User, Admin } from '../../_models';
import { Router } from '@angular/router';
import { Component, OnInit} from '@angular/core';
import { FormGroup, FormArray, FormControl, Validators, FormBuilder} from '@angular/forms';
import 'rxjs/add/operator/debounceTime';
import 'rxjs/add/operator/distinctUntilChanged';
import { ToastrService } from 'ngx-toastr';
import { Meter } from './../../_models/meter';
import { ReloadService } from '../../_services/reload.sevice';




@Component({
    moduleId: module.id.toString(),
    templateUrl: 'home.component.html',
  selector: 'app-home',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css'
  ]

})
export class HomeComponent implements OnInit {
  currentUser: User;
  users: User[] = [];
  optionsSelect: Array<any>;
  cmp: Company;
  companies: Company[] = [];
  company: Company;
  form: FormGroup;
  name:  FormControl;
  crm_id:  FormControl;
  surname: FormControl;
  email: FormControl;
  headForm: FormGroup;
  search: FormControl;
  loading = false;
  showDropDown = false;
  add_edit = true;
  term: any;
  id: FormControl;
  func: FormControl;
  pods: FormControl;
  types: boolean;
  temporary: any[];
  plusF: boolean;
  showPods = false;
  meters: Array<Meter>;
  podsRows: FormControl;
  adresRows: FormControl;
  podsForms = [];
  adresForms = [];
  podsExist = false;
  show = [false];
  showOffre = [false];
  showOffa = [false];
  site: any;
  year: number;
  volume: {};
  // companyPagination: Pagination<any>;
  pag = 1;
  nom = '';
  adminsTab = true;
  offesCockpit = [];
  allOffer = [];
  infoOffer = false;
  idOffer: number;
  curentClient: Admin;
  finger: false;
  curentU: any;
  showAdmins = false;

  constructor(private companyService: CompanyService,
              private toastr: ToastrService,
              private ccService: CcService,
              private podsList: FormBuilder,
              private adresList: FormBuilder,
              private reloadService: ReloadService,
              private userService: UserService,
              private router: Router,
              private customObservable: CustomObservable,
              private searchService: SearchService,
            ) {
              this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
   }

  ngOnInit() {
    this.verifyRoleWithRequestbyAdmins();
    const isIE =  /msie\s|trident\/|isIE\//i.test(window.navigator.userAgent);
    console.log('isIE:', isIE);
    if (this.currentUser.role !== 1) { this.router.navigate(['clients']); }
    this.loadAllUsers();
    this.createFormControlesCompany();
    this.createFormCompany();
    this.onChangesAdd();
    this.getcurentClient();
    // tslint:disable-next-line:max-line-length
    this.reloadService.isReloadEditCurentUser.subscribe((data) => { if (data === true) { this.getcurentClient(); this.reloadService.changeEditCurentUser(false); } });
    this.customObservable.isShowAdmins.subscribe((data) => { this.showAdmins = data; } );
  }

  private loadAllUsers() {
    this.userService.getAll().subscribe(users => { this.users = users; });
}

  verifyRoleWithRequestbyAdmins() {
      this.searchService.searchAdmins('', 1, 10).subscribe (
        (data) => { this.customObservable.changeShowAdmins(true); },
        (er) => { if (er.status === 403) { this.customObservable.changeShowAdmins(false); } },
    );
  }

  getcurentClient() {
    this.curentClient = null;
      if (this.currentUser.role) {
        this.ccService.getClient(this.currentUser.id).subscribe(
        (data) => {this.curentClient = data; },
        (e) => {}
      );
    }

  }

  onChangesAdd(): void {
    this.form.get('podsRows').valueChanges
    .subscribe(val => {
      this.observableSourceAdd(val);
    });
  }

  observableSourceAdd(add: string) {
    if (add[add.length - 1]['podsname']) {
      if (add[add.length - 1]['podsname'].length > 0) {
        this.plusF = true;
        this.podsExist = false;
        for (let index = 0; index < add.length - 1; index++) {
          if ( add.length > 1) {
            if ( add[index]['podsname']  === add[add.length - 1]['podsname']  ) {
                this.podsExist = true;
           }
          }
        }
      }
    }
  }

  closeDropDown() {this.showDropDown = false; }
  openDropDown() {this.showDropDown = true; }

  showSuccess(mesaj: string) { this.toastr.success(mesaj); }
  showError(mesaj: string) { this.toastr.error(mesaj); }

  deleteCompany() {
    this.loading = true;
    this.companyService.delete(this.company.id).subscribe(
       (data) => {
         this.loading = false;
         this.showSuccess('Le client ' + this.company.name + ' a été supprimé.');
         $('#cancel-btn-delete').click();
         $('body').click();
         this.saveCompany(null);
         this.company = null;
         this.companies = null;
         this.term = '';
      },
      (er) => {
        this.loading = false;
        this.showError('Le client ' + this.company.name + ' n\a pas été supprimé.');
      }
    );
  }

  saveCompany(cmp: Company) {
    if (this.company) {
    this.reloadService.changeCC(true);
    }
    this.company = null;
    this.getMetersByCompany(cmp);
    this.ccService.change(null);
    this.ccService.change(cmp);
    if (cmp) {
    this.company = cmp;
      this.term = this.company.name;
      this.updateFormControlesCompany();
    } else { this.company = null; }
  }

  onSubmit(company: any) {
    this.showPods = true;
    this.loading = true;
    if (this.add_edit) { // add-company
      this.companyService.createCompany(company).subscribe(
      (data) => {
        this.showSuccess('Le client ' + data['name'] + ' a été créé');
        $('#modal').click();
         $('body').click();
         this.form.reset();
        //  this.observableSource(company.name);
         this.saveCompany(new Company(data));
         this.loading = false;
      },
      (errores) => {
        this.showError(errores.error);
        this.loading = false;
      });
    } else {// update company
        this.companyService.update(company).subscribe(
          (data) => {
            this.loading = false;
            this.showSuccess('Les modifications ont été sauvegardées.');
            $('#modal').click();
            $('body').click();
            this.saveCompany(company);
            this.showPods = false;
          },
          (e) => {
            this.loading = false;
            this.showPods = false;
            this.showError('Something went wrong');
          });
      }
      this.podsForms = [];
      this.adresForms = [];
  }

  add() {
    this.form.reset();
    this.add_edit = true;
    this.showPods = true;
    const control = <FormArray>this.form.controls['podsRows'];
    control.controls = [];
    const controlAdres = <FormArray>this.form.controls['adresRows'];
    controlAdres.controls = [];
    this.addNewRow();
  }

  edit() {
    this.showPods = true;
    this.add_edit = false;
    this.saveCompany(this.company);
    this.podsForms = [];
    this.adresForms = [];
  }

  createFormControlesCompany() {
    this.add_edit = true;
    this.name = new FormControl(Validators.required),
    this.crm_id = new FormControl(Validators.required),
    this.func = new FormControl(Validators.required),
    this.surname = new FormControl(Validators.required),
    this.email = new FormControl('', [Validators.required, Validators.pattern('[a-zA-Z0-9.-_]{1,}@[a-zA-Z.-]{2,}[.]{1}[a-zA-Z]{2,}')]);
  }

  createFormCompany() {
    this.form = new FormGroup({
      podsRows: this.podsList.array([this.initpodsRows()]),
      adresRows: this.adresList.array([this.initadresRows()]),
      name: this.name,
      crm_id: this.crm_id,
      surname: this.surname,
      email: this.email,
      func: this.func,
    });
  }

  initpodsRows() { return this.podsList.group({podsname: ['']}); }
  initadresRows() { return this.adresList.group({adresname: ['']}); }

  addNewRow() {
    this.plusF = false;
    const control = <FormArray>this.form.controls['podsRows']; control.push(this.initpodsRows());
    const controlAdres = <FormArray>this.form.controls['adresRows']; controlAdres.push(this.initadresRows());
  }

  deleteRow(index: number) {
    const control = <FormArray>this.form.controls['podsRows']; control.removeAt(index);
    const controlAdres = <FormArray>this.form.controls['adresRows']; controlAdres.removeAt(index);
  }

    updateFormControlesCompany() {
      this.add_edit = false;
      this.id = new FormControl(this.company.id),
      this.name = new FormControl( this.company.name, Validators.required),
      this.crm_id = new FormControl( this.company.crm_id, Validators.required),
      this.surname = new FormControl(this.company.surname, Validators.required),
      this.email = new FormControl(this.company.email, Validators.required),
      this.func = new FormControl(this.company.func, Validators.required),
      this.updateFormCompany();
    }

    updateFormCompany() {
      this.form = new FormGroup({
        podsRows: this.podsList.array(this.podsForms),
        adresRows: this.adresList.array(this.adresForms),
        name: this.name,
        crm_id: this.crm_id,
        surname: this.surname,
        email: this.email,
        func: this.func,
        id: this.id

      });
    }

    getMetersByCompany(cmp: Company) {
      if (cmp) {
        this.meters = [];
        this.companyService.getMetersByCompany(cmp.id).subscribe(
          (data) => {
            this.meters = data;
            data.forEach(element => {
              this.podsForms.push(this.podsList.group({podsname: [element.meter_id]}));
              this.adresForms.push(this.podsList.group({adresname: [element.address]}));
            });
          }
        );
      }
    }
  sendd(off: any) {
    if (off) {
      this.idOffer = off.id;
    }
  }
}

