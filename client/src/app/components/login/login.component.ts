import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthenticationService } from '../../_services/index';
import { ToastrService } from 'ngx-toastr';

@Component({
    moduleId: module.id.toString(),
    templateUrl: 'login.component.html',
    styleUrls:  ['login.component.css']
})

export class LoginComponent implements OnInit {
    model: any = {};
    loading = false;
    error = false;
    returnUrl: string;
    trimis = false;
    try: any;
    check = false;

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private authenticationService: AuthenticationService,
        private toastr: ToastrService) { }

    ngOnInit() {
        // reset login status
        this.authenticationService.logout();

        // get return url from route parameters or default to '/'
        this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';
    }

    login() {
        this.loading = true;
        this.error = false;
        this.authenticationService.login(this.model.username, this.model.password)
            .subscribe(
                data => {
                    this.toastr.success('Bienvenue ' + data.user.username  + '.');
                    this.router.navigate([this.returnUrl]);
                },
                er => {
                    this.error = true;
                    this.loading = false;
                    try {
                         if (er.status === 403) { this.try = er.error.try; } else { this.try = null; }
                    } catch (error) {  }
                });
    }
    resetMail() {
        if (this.model.username) {
            this.loading = true;
            this.authenticationService.resetPassword(this.model.username).subscribe(
                data => { this.loading = false; this.toastr.success('L\'email a été envoyé.'); },
                er => { this.loading = false; }
            );
        }
    }
}
