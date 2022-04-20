import { CompanyService ,  SearchService, CcService, CustomObservable, AdminService} from '../../_services/index';
import { Company, User, Admin } from '../../_models';
import { Router } from '@angular/router';
import {  Component, OnInit,  Input } from '@angular/core';
import { FormGroup, FormArray, FormControl, Validators, FormBuilder} from '@angular/forms';
import 'rxjs/add/operator/debounceTime';
import 'rxjs/add/operator/distinctUntilChanged';
import { ToastrService } from 'ngx-toastr';
import { Meter } from './../../_models/meter';
import { ReloadService } from '../../_services/reload.sevice';
import { Offer } from '../../_models/offerData';
import { DashboardService } from '../../_services/dashboart.service';

  @Component({
    selector: 'app-cc',
    templateUrl: './cc.component.html',
    styleUrls: [
      // '../../../assets/css/styles/nexus.css',
      // '../../../assets/css/styles/layout.css',
      // '../../../assets/css/styles/theme.css'
    ]
  })

export class CcComponent implements OnInit {
  @Input() company: Company;
  currentUser: User;
  cmp: Company;
  companies: Company[] = [];
  form: FormGroup;
  name:  FormControl;
  crm_id:  FormControl;
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
  sex: FormControl;
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
  editer_client = false;
  companyEdit: boolean;
  offer: Offer;
  interval: any;
  pods_unique = false;
  pattern = '[a-zA-Z0-9-.-_éèàûç]{1,}@[a-zA-Z.-]{2,}[.]{1}[a-zA-Z]{2,}';


  constructor(private companyService: CompanyService,
              private searchService: SearchService,
              private toastr: ToastrService,
              private ccService: CcService,
              private podsList: FormBuilder,
              private adresList: FormBuilder,
              private customObservable: CustomObservable,
              private reloadService: ReloadService,
              private router: Router,
              private adminService: AdminService,
              private dashboardService: DashboardService,
            ) {this.currentUser = JSON.parse(localStorage.getItem('currentUser')); }

   ngOnInit() {
    this.updateHead();
    this.onChanges();
    this.createFormControlesCompany();
    this.createFormCompany();
    this.reloadService.isReloadCC.subscribe(
      (data) => {
        if (data === true) {
          this.company = null;
          this.companies = null;
          this.term = '';
          this.observableSource('');
          this.getcurentClient();
          this.reloadService.changeCC(false);
        }
      }
    );

    this.customObservable.isOffer.subscribe((data) => { this.offer = data; } );
    this.customObservable.isCompany.subscribe((data) => { this.saveCompany(data); });
    this.customObservable.isYear.subscribe((data) => { this.year = data; } );
    this.customObservable.isVolume.subscribe((data) => { this.volume = data; } );
    this.customObservable.isSite.subscribe((data) => {
      this.site = data;
      if (this.site) {
        this.customObservable.changeOffer(null);
       this.getDashbord(this.site.id, this.site.year);
      } } );

    if (!this.company) { this.router.navigate(['clients']); }

    this.getcurentClient();
  }

  getcurentClient() {
    this.curentClient = null;
      if (this.currentUser.role !== 1) {  this.ccService.getClient(this.currentUser.id).subscribe(
        (data) => {this.curentClient = data; },
        (e) => {}
      );
    }
  }

  onChanges(): void {
    this.headForm.get('search').valueChanges
    .debounceTime(200)
    .distinctUntilChanged()
    .subscribe(val => {
      this.observableSource(val);
    });
    this.ccService.change(null);
  }

  observableSource(keyword: string) {
    if (keyword === '') {
      // this.saveCompany(null);
      this.companies = null;
      // this.getAlls(this.pag, keyword);
    }
    if (keyword) {
    this.term = keyword;
    // this.getAlls(this.pag, keyword);
      this.searchService.searchCompany(keyword)
      .subscribe (
        (data) => { this.companies = data; },
        (er) => {  this.term = null; },
    );
    }
  }

  onChangesAdd(): void {
    this.form.get('podsRows').valueChanges.subscribe(val => { this.observableSourceAdd(val); });
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
                this.podsExist = true;
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
         this.showSuccess('Les données ont été sauvegardées.');
         $('#cancel-btn-delete').click();
         $('body').click();
         this.saveCompany(null);
         this.company = null;
         this.companies = null;
         this.term = '';
         this.router.navigate(['clients']);
      },
      (errores) => {
        this.loading = false;
        this.showError('Le client n\'a pas été supprimé');
      }
    );
  }


  updateHead() {
    this.search = new FormControl();
    this.headForm = new FormGroup({
      search: this.search,
    });
  }

  saveCompany(cmp: Company) {
    this.company = null;
    if (cmp) {
      this.getMetersByCompany(cmp);
      this.ccService.change(cmp);
      this.company = cmp;
      this.term = this.company.name;
      this.updateFormControlesCompany();
    } else { this.company = null; }
  }


  onSubmit(company: any) {
    this.loading = true;
    this.onSubmitFinal(company);
    // const control = <FormArray>this.form.controls['podsRows'];
    // if (control.value[control.length - 1].podsname !== '') {
    // this.adminService.verifyExistPod(control.value[control.length - 1].podsname).subscribe(
    //   (data) => { if (data) {
    //     // console.log(this.podsForms, 'podsForms');
    //      this.podsForms.forEach(element => {
    //       if (element.value.podsname === data.meter_id) { this.onSubmitFinal(company);  this.pods_unique = false; } else {
    //         this.pods_unique = true;
    //         this.loading = false; }
    //      });
    //     }},
    //   (er) => {  this.loading = false;
    //      if (er) {
    //         this.pods_unique = false;
    //         this.onSubmitFinal(company);
    //       }
    //  });
    // } else { this.onSubmitFinal(company); }
  }


  onSubmitFinal(company: any) {
    console.log('onSubmitFinal', company);
    this.showPods = true;
    if (this.add_edit) { // add-comspany
      this.companyService.createCompany(company).subscribe(
      (data) => {
        this.showSuccess('Le client ' + data['name'] + ' a été créé');
        $('#modal').click();
        $('body').click();
        this.form.reset();
        this.observableSource(company.name);
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
            this.showSuccess('Les données du client ' + data['name'] + ' ont été modifiées.');
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
    const control = <FormArray>this.form.controls['podsRows'];
    control.controls = [];
    const controlAdres = <FormArray>this.form.controls['adresRows'];
    controlAdres.controls = [];
    this.addNewRow();
  }

  edit() {
    this.add_edit = false;
    this.saveCompany(this.company);
    this.podsForms = [];
    this.adresForms = [];
  }

  createFormControlesCompany() {
    this.add_edit = true;
    this.name = new FormControl(Validators.required),
    this.crm_id = new FormControl(Validators.required),
    this.nom_entrepise = new FormControl(Validators.required),
    this.func = new FormControl(Validators.required),
    this.sex = new FormControl(Validators.required),
    this.surname = new FormControl(Validators.required),
    this.email = new FormControl('', [Validators.required, Validators.pattern(this.pattern)]),
    this.address = new FormControl(''),
    this.zip_code = new FormControl('');
  }

  createFormCompany() {
    this.form = new FormGroup({
      podsRows: this.podsList.array([this.initpodsRows()]),
      adresRows: this.adresList.array([this.initadresRows()]),
      name: this.name,
      crm_id: this.crm_id,
      nom_entrepise: this.nom_entrepise,
      surname: this.surname,
      email: this.email,
      func: this.func,
      sex: this.sex,
      address: this.address,
      zip_code: this.zip_code,
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
    if (index === control.length - 1) { this.pods_unique = false; }
  }
  deleteRowByAPI(podsrow: any) {
    this.adminService.deletePods(podsrow.value.podsname).subscribe(
      (data) => {},
      (er) => {},
    );
  }

    updateFormControlesCompany() {
      this.add_edit = false;
      this.id = new FormControl(this.company.id),
      this.name = new FormControl( this.company.name, Validators.required),
      this.crm_id = new FormControl( this.company.crm_id, Validators.required),
      this.nom_entrepise = new FormControl( this.company.nom_entrepise, Validators.required),
      this.surname = new FormControl(this.company.surname, Validators.required),
      this.email = new FormControl(this.company.email, Validators.required),
      this.func = new FormControl(this.company.func, Validators.required),
      this.sex = new FormControl(this.company.sex, Validators.required),
      this.zip_code = new FormControl(this.company.zip_code),
      this.address = new FormControl(this.company.address),
      this.updateFormCompany();
    }

    updateFormCompany() {
      this.form = new FormGroup({
        podsRows: this.podsList.array(this.podsForms),
        adresRows: this.adresList.array(this.adresForms),
        name: this.name,
        crm_id: this.crm_id,
        nom_entrepise: this.nom_entrepise,
        surname: this.surname,
        email: this.email,
        func: this.func,
        sex: this.sex,
        id: this.id,
        zip_code: this.zip_code,
        address: this.address

      });
    }

    getMetersByCompany(cmp: Company) {
      if (cmp) {
        this.meters = [];
        this.companyService.getMetersByCompany(cmp.id).subscribe(
          (data) => {this.meters = data; }
        );
        this.companyService.getMetersUploadByCompany(cmp.id).subscribe(
          (data) => {
            if (data.length !== 0) {
            data.forEach(element => {
              this.podsForms.push(this.podsList.group({podsname: [element.meter_id], id: [element.id] }));
              this.adresForms.push(this.podsList.group({adresname: [element.address], id: [element.id] }));
            });
          } else { this.addNewRow(); }
          // console.log('podsForms', this.podsForms);
          }
        );

      }


    }

  sendd(off: any) { if (off) { this.idOffer = off.id; }}

  send(site: any) {
    if (site === null ) { this.customObservable.changeVolume(null); this.customObservable.changeOffer(null); }
    this.site = null;
    this.site = site;
    this.customObservable.changeSite(null);
    this.customObservable.changeSite(site);
  }

  getDashbord(id: number, year: any) {
    this.dashboardService.getDashboard(id, year).subscribe( (data) => { this.interval = data.interval; } );
  }

  verifyExistPod(ps: any) {
    this.onChangesAdd();
    this.pods_unique = false;
    if (ps.value.podsname !== '') {
      this.pods_unique = false;
      this.addNewRow();
      // this.adminService.verifyExistPod(ps.value.podsname).subscribe(
      //   (data) => { if (data) {
      //     this.pods_unique = true;
      //     if (!this.add_edit) {
      //       // console.log('data', data, data.meter_id,  this.podsForms[this.podsForms.length - 1].value.podsname,
      //       //  data.meter_id === this.podsForms[this.podsForms.length - 1].value.podsname);
      //       if (this.podsForms.length !== 0) {
      //         if (data.meter_id === this.podsForms[this.podsForms.length - 1].value.podsname) {
      //           this.pods_unique = false; this.addNewRow();
      //         }
      //       }
      //     }

      //    } },
      //   (er) => {   if (er)   { this.pods_unique = false; this.addNewRow(); } }
      // );
    }
  }

}


