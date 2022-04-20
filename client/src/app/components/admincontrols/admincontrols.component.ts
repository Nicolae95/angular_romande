import { Component, OnInit } from '@angular/core';
import { SearchService, UserService, CustomObservable, FileService } from '../../_services';
import { ToastrService } from 'ngx-toastr';
import { Admin, User } from '../../_models';
import { FormGroup, FormControl, Validators} from '@angular/forms';
import { AdminService } from '../../_services/admin.service';
import * as $ from 'jquery';
import { Pagination } from '../../_models/pagination';
import { OfferService } from '../../_services/offer.service';
import { Router } from '@angular/router';


@Component({
  selector: 'app-admincontrols',
  templateUrl: './admincontrols.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css'
  ]

})

export class AdmincontrolsComponent implements OnInit {
  currentUser: User;
  admins: Pagination<Admin>;
  userGroup: FormGroup;
  adminsForm: FormGroup;
  id: FormControl;
  searchAdmin: FormControl;
  crm_id: FormControl;
  username: FormControl;
  sex: FormControl;
  first_name: FormControl;
  fonction: FormControl;
  other_fonction: FormControl;
  last_name: FormControl;
  email: FormControl;
  role: FormControl;
  // chPassword: FormControl;
  chSign: FormControl;
  editBoolean: Boolean = false;
  pk: number;
  pkDelete: Admin;
  changeP: Boolean = false;
  changeS: Boolean = false;
  loading = false;
  loadingSm = false;
  del: Boolean = false;
  pag = 1;
  nr: number;
  keyword = '';
  stop: boolean;
  getStop = null;
  loadingButtAlarm = false;
  myFile: File[];
  fileValid = false;
  pattern = '[a-zA-Z0-9-.-_éèàûç]{1,}@[a-zA-Z.-]{2,}[.]{1}[a-zA-Z]{2,}';
  editAdmin: any;
  setkeyAdmin: Admin;
  usName: any;
  adminsMail = false;
  showAdmins: boolean;
  signatur_B64: any;

  constructor(private adminService: AdminService,
              private searchService: SearchService,
              private offerService: OfferService,
              private fileService: FileService,
              private userService: UserService,
              private customObservable: CustomObservable,
              private router: Router,
              private toastr: ToastrService) {
                this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
                this.nr = this.currentUser.nr;
              }

  ngOnInit() {
    this.customObservable.isShowAdmins.subscribe((data) => { this.showAdmins = data; } );
    this.add();
    this.onChanges();
    this.getAdmin('', 1);
    this.getalarm_Stop_Star();
  }

  onChanges(): void {
    this.adminsForm.get('searchAdmin').valueChanges
    .debounceTime(200)
    .distinctUntilChanged()
    .subscribe(val => {
      this.getAdmin(val, this.pag);
    });
  }



  getAdmin(keyword: string , pag: number) {
    if ( this.nr === 10 && pag === 1) { this.loading = true; }
    this.keyword = keyword;
    this.pag = pag;
      this.searchService.searchAdmins(keyword, this.pag, this.nr)
      .subscribe (
        (data) => { this.admins = data; this.loading = false; this.customObservable.changeShowAdmins(true); },
        (er) => { this.loading = false;
          if (er.status === 403) {
              this.router.navigate(['clients']);
             this.customObservable.changeShowAdmins(false);
          } },
    );
  }

  setNumberperPag(nr: number) {
    this.nr = Number(nr);
    this.userService.chnageNrPerPag(this.currentUser, nr).subscribe((data) => { this.getAdmin(this.keyword, 1); });
  }

  showSuccess(mesaj: string) { this.toastr.success(mesaj); }
  showError(errors) {this.toastr.error(errors); }



  add() {
    this.createFormControles();
    this.createForm();
    this.editBoolean = false;
    this.changeP = true;
    this.changeS = true;
    this.userGroup.get('username').valueChanges.subscribe(val => {
      if (val !== undefined) {this.usName = this.usName.replace(/\s/g, ''); } });
  }

  edit(admin: any) {
    this.editAdmin = admin;
    this.pk = admin.pk;
    this.changeP = false;
    this.changeS = false;
    this.editBoolean = true;
    this.editFormControles(admin);
  }

  setPs() {
    this.loadingSm = true;
    this.adminService.setPassword(this.setkeyAdmin).subscribe(
      (data) => { $('#keys').click(); $('body').click(); this.loadingSm = false; this.showSuccess('L\'email a été envoyé.'); }
    );
  }

  keyConfirm(admin: any) { this.setkeyAdmin = admin; }

  deleteConfirm(admin: any) {
    this.del = true;
    this.pkDelete = admin;
  }


  delete(admin: any) {
    this.loadingSm = true;
     this.adminService.delete(admin.pk).subscribe(
       (data) => {
        this.showSuccess('Le client ' +  admin.username + ' a été supprimé');
        this.loadingSm = false;
       this.getAdmin(this.keyword, this.pag);
        $('#dels').click();
        $('body').click();
      },
      (e) => {
        this.showSuccess('Le client ' +  admin.username + ' n\'a pas a été supprimé');
        this.loadingSm = false;
       this.getAdmin(this.keyword, this.pag);
        $('#dels').click();
        $('body').click();
      });
  }

  onSubmit(admin: any) {
    this.loading = true;
    admin.username = admin.username.replace(/\s/g, '');
      if (this.editBoolean) {
        const newAdmin: any = new FormData();
        newAdmin.append('pk', this.pk);
        newAdmin.append('crm_id', admin.crm_id);
        newAdmin.append('username', admin.username);
        newAdmin.append('sex', admin.sex);
        newAdmin.append('first_name', admin.first_name);
        newAdmin.append('fonction', admin.fonction);
        newAdmin.append('other_fonction', admin.other_fonction);
        newAdmin.append('last_name', admin.last_name);
        newAdmin.append('email', admin.email);
        newAdmin.append('role', admin.role);
        if (this.myFile) {
          for (let i = 0; i < this.myFile.length; i++) {
            newAdmin.append('files', this.myFile[i], this.myFile[i].name);
            }
        } else { newAdmin.append('files', ''); }
        this.adminService.uploadFile(newAdmin, 'edit', this.pk)
        .then( res => { this.ifIsCuresntuser(res); } )
        .catch( er => { this.showError(er.error); this.loading = false;  console.log('er', er); } )
        .then(
          () => {
                 this.showSuccess('Le client ' + admin.username + ' a été modifié');
                 this.loading = false;
                 this.getAdmin(this.keyword, this.pag);
                 $('#cancel-btn').click();
                 $('body').click();
                }
        );
      }

     if (!this.editBoolean) {
      const newAdmin: any = new FormData();
      newAdmin.append('crm_id', admin.crm_id);
      newAdmin.append('username', admin.username);
      newAdmin.append('sex', admin.sex);
      newAdmin.append('first_name', admin.first_name);
      newAdmin.append('fonction', admin.fonction);
      newAdmin.append('other_fonction', admin.other_fonction);
      newAdmin.append('last_name', admin.last_name);
      newAdmin.append('email', admin.email);
      newAdmin.append('role', admin.role);
      if (this.myFile) {
        for (let i = 0; i < this.myFile.length; i++) {
          newAdmin.append('files', this.myFile[i], this.myFile[i].name);
          }
      } else { newAdmin.append('files', ''); }

      this.adminService.uploadFile(newAdmin, 'add')
      .then( res => { } )
      .catch( er => { this.showError(er.error); this.loading = false; } )
      .then(
        () => {
               this.showSuccess('Le client ' + admin.username + ' a été créé');
               this.loading = false;
               this.getAdmin(this.keyword, this.pag);
              //  this.myFile = [];
               $('#cancel-btn').click();
               $('body').click();
              }
      );
    }

  }

  createFormControles() {
    this.crm_id = new FormControl();
    this.username = new FormControl('', Validators.required);
    this.sex = new FormControl('', Validators.required);
    this.first_name = new FormControl('', Validators.required);
    this.fonction = new FormControl('', Validators.required);
    this.other_fonction = new FormControl('', Validators.required);
    this.last_name = new FormControl('', Validators.required);
    this.email = new FormControl('', [Validators.required, Validators.pattern( this.pattern)]);
    this.role = new FormControl(null, Validators.required);
    this.searchAdmin = new FormControl();
  }

  createForm() {
    this.adminsForm = new FormGroup({ searchAdmin: this.searchAdmin });
    this.userGroup = new FormGroup({
      crm_id: this.crm_id,
      username: this.username,
      sex: this.sex,
      first_name: this.first_name,
      fonction: this.fonction,
      other_fonction: this.other_fonction,
      last_name: this.last_name,
      email: this.email,
      role: this.role,
    });
  }

  editFormControles(admin: Admin) {
    this.crm_id = new FormControl(admin.crm_id, Validators.required);
    this.username = new FormControl(admin.username, Validators.required);
    this.sex = new FormControl(admin.sex, Validators.required);
    this.first_name = new FormControl(admin.first_name, Validators.required);
    this.fonction = new FormControl(admin.fonction, Validators.required);
    if (Number(admin.fonction) === 10) {
      this.other_fonction = new FormControl(admin.other_fonction, Validators.required);
    } else {  this.other_fonction = new FormControl('no value', Validators.required); }
    this.last_name = new FormControl(admin.last_name, Validators.required);
    this.email = new FormControl(admin.email, [Validators.required, Validators.pattern( this.pattern)]);
    this.role = new FormControl(admin.role, Validators.required);
    this.chSign = new FormControl();
    this.editForm();
  }

  editForm() {
    this.userGroup = new FormGroup({
      crm_id: this.crm_id,
      username: this.username,
      sex: this.sex,
      first_name: this.first_name,
      fonction: this.fonction,
      other_fonction: this.other_fonction,
      last_name: this.last_name,
      email: this.email,
      role: this.role,
      chSign: this.chSign,
    });
  }

  getalarm_Stop_Star() {
    this.offerService.get_alarm_Stop_Star().subscribe( (data) => {  this.stop =  data[0]['stop']; this.getStop = data; });
  }

  putalarm_Stop_Star(alarm: boolean) {
    this.loadingButtAlarm = true;
    this.offerService.put_alarm_Stop_Star(this.currentUser, alarm).subscribe(
      (data) => {
        this.stop =  !alarm;
        this.loadingButtAlarm = false;
      });
    this.getalarm_Stop_Star();
  }

    fileEvent(files: File[]) {
      this.myFile = files;
      if (this.myFile == null) { this.fileValid = false;
      } else { this.fileValid = true; }
    }

    other() {
      if (Number(this.fonction.value) === 5) {
        this.userGroup.get('other_fonction').setValue(null);
      } else { this.userGroup.get('other_fonction').setValue('no value'); }
    }


    ifIsCuresntuser(us: any) {
      this.adminService.getById(this.currentUser.id).subscribe(
        (data) => { const user = data;
        console.log('currentUser', this.currentUser, user.pk, this.currentUser.id);
        if (user.pk === this.currentUser.id) {
          const toStory = {'id': user.pk,
                          'username': user.username,
                          'firstName': user.first_name,
                          'lastName':  user.last_name,
                          'email': user.email,
                          'role': user.role,
                          'fonction': user.fonction,
                          'alarm': this.currentUser.alarm,
                          'nr': this.currentUser.nr,
                        };
          console.log('toStory', toStory);
          localStorage.removeItem('currentUser');
          localStorage.setItem('currentUser', JSON.stringify(toStory));
        }
      }

      );
  }
  getSignature(id: number) {
    this.fileService.getSignature(id).subscribe(
      (data) => { this.signatur_B64 = data.image; },
      (er) => {}
    );
  }
}
