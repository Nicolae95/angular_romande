import { CompanyService, AdminService} from '../../_services/index';
import { Company, User, Admin } from '../../_models';
import { Component, OnInit, Input } from '@angular/core';
import { FormGroup, FormArray, FormControl, Validators, FormBuilder} from '@angular/forms';
import 'rxjs/add/operator/debounceTime';
import 'rxjs/add/operator/distinctUntilChanged';
import { ToastrService } from 'ngx-toastr';
import { Meter } from './../../_models/meter';
import { ReloadService } from '../../_services/reload.sevice';

@Component({
  selector: 'app-add-new-client',
  templateUrl: './add-new-client.component.html',
  styleUrls: [
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css'
  ]
})

export class AddNewClientComponent implements OnInit {
@Input() companyEdit: any;
currentUser: User;
cmp: Company;
companies: Company[] = [];
company: Company;
form: FormGroup;
name:  FormControl;
// crm_id:  FormControl;
nom_entrepise:  FormControl;
surname: FormControl;
zip_code: FormControl;
address: FormControl;
email: FormControl;
headForm: FormGroup;
search: FormControl;
loading = false;
showDropDown = false;
add_edit = true;
term: any;
id: FormControl;
func: FormControl;
temporary: any[];
plusF: boolean;
showPods = false;
meters: Array<Meter>;
podsRows: FormControl;
adresRows: FormControl;
podsForms = [];
adresForms = [];
podsExist = false;
site: any;
year: number;
volume: {};
pag = 1;
idOffer: number;
curentClient: Admin;
pods: FormControl;
types: boolean;
show = [false];
showOffre = [false];
showOffa = [false];
nom = '';
adminsTab = true;
offesCockpit = [];
allOffer = [];
infoOffer = false;
finger: false;
curentU: any;
editer_client = false;
sex: FormControl;
pods_unique = false;
pattern = '[a-zA-Z0-9-.-_éèàûç]{1,}[@]{1}[a-zA-Z.-]{2,}[.]{1}[a-zA-Z]{2,}';


constructor(private companyService: CompanyService,
            private toastr: ToastrService,
            private podsList: FormBuilder,
            private adresList: FormBuilder,
            private reloadService: ReloadService,
            private adminService: AdminService,
          ) {
            this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
 }

  ngOnInit() {
    this.createHeadControles();
    this.updateHead();
    this.createFormControlesCompany();
    this.createFormCompany();
    this.onChangesAdd();
    if (this.companyEdit) {   this.company = this.companyEdit; this.edit();  } else { this.add(); }
  }

  onChangesAdd(): void {
    this.form.get('podsRows').valueChanges
    .subscribe(val => {
      this.observableSourceAdd(val);
    });
  }

  observableSourceAdd(add: string) {
    this.pods_unique = false;
    if (add[add.length - 1]['podsname']) {
      if (add[add.length - 1]['podsname'].length > 0) {
        this.plusF = true;
        this.podsExist = false;
        for (let index = 0; index < add.length - 1; index++) {
          if ( add.length > 1) {
            if ( add[index]['podsname']  === add[add.length - 1]['podsname']  ) {
                // this.podsExist = true;
           }
          }
        }
      }
    }
  }


  closeDropDown() { this.showDropDown = false; }
  openDropDown() { this.showDropDown = true; }

  showSuccess(mesaj: string) { this.toastr.success(mesaj); }
  showError(mesaj: string) { this.toastr.error(mesaj); }


  deleteCompany() {
    this.loading = true;
    this.companyService.delete(this.company.id).subscribe(
      (data) => {
        this.loading = false;
        this.showSuccess('Le client ' + this.company.name + 'a été supprimé.');
        $('#cancel-btn-delete').click();
        $('body').click();
        this.company = null;
        this.companies = null;
        this.term = '';
      },
      (errores) => {
        this.loading = false;
        this.showError(errores.error);
      }
    );
  }

  createHeadControles() { this.search = new FormControl(); }

  updateHead() {
    this.headForm = new FormGroup({
      search: this.search,
    });
  }

  onSubmit(company: any) {
      // this.loading = true;
      // const control = <FormArray>this.form.controls['podsRows'];
      // this.adminService.verifyExistPod(control.value[control.length - 1].podsname).subscribe(
      //   (data) => { if (data) {
      //     this.pods_unique = true;
      //      this.loading = false; } },
      //   (er) => {   if (er) { this.pods_unique = false;
      //   this.showPods = true;
        this.loading = true;
        if (this.add_edit) {
          // add-company
          this.companyService.createCompany(company).subscribe(
          (data) => {
            this.showSuccess('Le client ' + data['name'] + ' a été créé');
            $('#modal').click();
            $('body').click();
            this.form.reset();
            this.reloadService.changeReloadClient(true);
            this.loading = false;
          },
          (errores) => {
            this.showError(errores.error);
            this.loading = false;
          });
        } else { // update company
            this.companyService.update(company).subscribe(
              (data) => {
                this.loading = false;
                this.showSuccess('Les modifications ont été sauvegardées.');
                $('#modal').click();
                $('body').click();
                // this.saveCompany(company);
                this.showPods = false;
              },
              (e) => {
                this.loading = false;
                this.showPods = false;
                this.showError('Le client n\'a pas été mis à jour.');
              });
          }
          this.podsForms = [];
          this.adresForms = [];
        // }});
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
    this.podsForms = [];
    this.adresForms = [];
  }

  createFormControlesCompany() {
    this.add_edit = true;
    this.name = new FormControl('', Validators.required),
    // this.crm_id = new FormControl('', Validators.required),
    this.nom_entrepise = new FormControl('', Validators.required),
    this.sex = new FormControl('', Validators.required),
    this.func = new FormControl('', Validators.required),
    this.surname = new FormControl('', Validators.required),
    this.address = new FormControl(''),
    this.zip_code = new FormControl(''),
    this.email = new FormControl('', [Validators.required, Validators.pattern( this.pattern )]);
  }

  createFormCompany() {
    this.form = new FormGroup({
      podsRows: this.podsList.array([this.initpodsRows()]),
      adresRows: this.adresList.array([this.initadresRows()]),
      name: this.name,
      // crm_id: this.crm_id,
      nom_entrepise: this.nom_entrepise,
      sex: this.sex,
      surname: this.surname,
      address: this.address,
      zip_code: this.zip_code,
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
      // this.crm_id = new FormControl( this.company.crm_id, Validators.required),
      this.nom_entrepise = new FormControl( this.company.nom_entrepise, Validators.required),
      this.sex = new FormControl(this.company.sex, Validators.required),
      this.surname = new FormControl(this.company.surname, Validators.required),
      this.zip_code = new FormControl(this.company.zip_code, Validators.required),
      this.address = new FormControl(this.company.address, Validators.required),
      this.email = new FormControl(this.company.email, Validators.required),
      this.func = new FormControl(this.company.func, Validators.required),
      this.updateFormCompany();
    }

  updateFormCompany() {
    this.form = new FormGroup({
      podsRows: this.podsList.array(this.podsForms),
      adresRows: this.adresList.array(this.adresForms),
      name: this.name,
      // crm_id: this.crm_id,
      nom_entrepise: this.nom_entrepise,
      sex: this.sex,
      surname: this.surname,
      zip_code: this.zip_code,
      address: this.address,
      email: this.email,
      func: this.func,
      id: this.id

    });
  }

  addOrEdit(companyEdit: boolean) {
    this.companyEdit = companyEdit;
    this.edit();
  }

  verifyExistPod(ps: any) {
    this.pods_unique = false;
    this.addNewRow();
    // this.adminService.verifyExistPod(ps.value.podsname).subscribe(
    //   (data) => { if (data) { this.pods_unique = true; } },
    //   (er) => {   if (er)   { this.pods_unique = false; this.addNewRow(); } }
    // );
  }

}

