import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { AdminService } from '../../_services';

@Component({
  selector: 'app-set-password',
  templateUrl: './set-password.component.html',
  styleUrls: ['./set-password.component.css']
})
export class SetPasswordComponent implements OnInit {
  token: string;
  coincid = false;
  trimis = false;
  passwordGroup: FormGroup;
  password: FormControl;
  secndPass: FormControl;
  pattern = '((?=.*\\d)(?=.*[a-z])(?=.*[A-Z]).{10,30})';
  existTerm: boolean;
  loading = false;

  constructor(
      private activatedRoute: ActivatedRoute,
      private router: Router,
      private adminService: AdminService,
      private toastr: ToastrService) { this.activatedRoute.params.subscribe( params =>  {this.token = params.token; }); }

  // showSuccess(name) { this.toastr.success('Bienvenue ' + name  + '.'); }
  ngOnInit() {
    if (this.token) {
      this.adminService.getPassword(this.token).subscribe(
        (data) => {
          if (data) {
            this.existTerm = true;
            this.password = new FormControl('', [ Validators.required, Validators.pattern(this.pattern)]);
            this.secndPass = new FormControl('', [ Validators.required, Validators.pattern(this.pattern)]);
            this.passwordGroup = new FormGroup({
              password: this.password,
              secndPass: this.secndPass,
            });
            this.onChangesSecondPass();
            this.loading = true;
        } },
        (er) => { if (er) { this.existTerm = false;  this.loading = true;
          setTimeout(() => { this.router.navigate(['login']); }, 2000); } }
      );

    } else { this.router.navigate(['login']); }

  }

  onSubmit(form: any) {
    this.passwordGroup.reset();
    this.adminService.postPassword(this.token, form.password).subscribe(
      (data) => { this.toastr.success('Sauvegardé avec succès.'); this.router.navigate(['login']); }
    );

  }

  onChangesSecondPass(): void {
    this.passwordGroup.get('secndPass').valueChanges
    .debounceTime(100)
    .distinctUntilChanged()
    .subscribe(val => {
      this.observableSecondPass(val);
    });
  }
  observableSecondPass(val: any) {
    this.coincid = false;
    if (val !== '') {
      if (this.password.value === this.secndPass.value) {
        //  console.log('true', this.password.value, this.secndPass.value);
         this.trimis = true; this.coincid = true; }
    } else { this.trimis = false;  }
    // console.log('**', this.password.value, val);
  }



}
