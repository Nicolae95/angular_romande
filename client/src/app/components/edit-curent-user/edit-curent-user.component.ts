import { Component, OnInit, Input } from '@angular/core';
import { Admin, User } from '../../_models';
import { AdminService, UserService } from '../../_services';
import { ToastrService } from 'ngx-toastr';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { ReloadService } from '../../_services/reload.sevice';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { Router } from '@angular/router';

@Component({
  selector: 'app-edit-curent-user',
  templateUrl: './edit-curent-user.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css'
  ]
})
export class EditCurentUserComponent implements OnInit {
  @Input() curentU: any;
  curentUserGroup: FormGroup;
  id: FormControl;
  username: FormControl;
  sex: FormControl;
  first_name: FormControl;
  last_name: FormControl;
  email: FormControl;
  role: FormControl;
  chPassword: FormControl;
  pk: number;
  pkDelete: Admin;
  loading = false;
  changeP: Boolean = false;
  pattern = '[a-zA-Z0-9-.-_éèàûç]{1,}@[a-zA-Z.-]{2,}[.]{1}[a-zA-Z]{2,}';
  currentUser: User;
  private loggedIn = new BehaviorSubject<boolean>(false); // {1}

  get isLoggedIn() {
    return this.loggedIn.asObservable(); // {2}
}


  constructor(private adminService: AdminService,
              private userService: UserService,
              private router: Router,
              private reloadService: ReloadService,
              private toastr: ToastrService) {
                this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
              }

  ngOnInit() {
    this.editFormControles(this.curentU);
  }

  showSuccess(mesaj: string) { this.toastr.success(mesaj); }
  showError(mesaj: string) { this.toastr.error(mesaj); }

  // changePassword(value: boolean) {
  //   this.changeP = value;
  //   if (this.changeP) {
  //     this.curentUserGroup.get('sex').setValue(0);
  //   } else {this.curentUserGroup.get('sex').setValue(null); }
  // }

  editFormControles(om: Admin) {
    this.username = new FormControl({value: om.username, disabled: true}, Validators.required);
    this.sex = new FormControl(om.sex, Validators.required);
    this.first_name = new FormControl(om.first_name, Validators.required);
    this.last_name = new FormControl(om.last_name, Validators.required);
    this.email = new FormControl(om.email, [Validators.required, Validators.pattern( this.pattern )]);
    this.role = new FormControl(om.role, Validators.required);
    this.chPassword = new FormControl(false);
    this.editForm();
  }

  editForm() {
    this.curentUserGroup = new FormGroup({
      username: this.username,
      sex: this.sex,
      first_name: this.first_name,
      last_name: this.last_name,
      email: this.email,
      role: this.role,
      chPassword: this.chPassword,
    });
  }




  onSubmit(admin: Admin) {
    this.loading = true;
    admin.pk = this.curentU.pk;
    admin.fonction = this.curentU.fonction;
    admin.username = this.curentU.username;
    admin.other_fonction = 'other';

       this.adminService.update(admin).subscribe(
         (data) => {
          this.reloadService.changeCC(true);
          this.showSuccess('Utilisateur ' + data['username'] + ' a été modifié');
          this.loading = false;
          $('#cancel-btn').click();
          $('body').click();
          this.reloadService.changeEditCurentUser(true);
          this.getById(data['pk'], admin);
        },
        (er) => { this.showError(er.statusText); this.loading = false; });

  }

  getById(id: number, admin: any) {
    // console.log('id', id);
    this.userService.getById(id).subscribe(
      (data) => {
        const toStory = {
          'id': data['user'].pk,
          'username': data['user'].username,
          'firstName': data['user'].first_name,
          'lastName':  data['user'].last_name,
          'email': data['user'].email,
          'role': data['user'].role,
          'fonction': data['user'].fonction
        };
        if (data && data['token']) {
            localStorage.removeItem('currentUser');
            localStorage.setItem('currentUser', JSON.stringify(toStory));
        }
      },
      (er) => {console.log('er', er);
      this.router.navigate(['login']);
    }
    );

  }

}
