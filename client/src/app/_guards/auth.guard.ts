import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { UserService } from '../_services/index';


@Injectable()
export class AuthGuard implements CanActivate {
    valid: Boolean = true;
    user: any;

    constructor(private router: Router, private userService: UserService) {
        this.userService.getUser().subscribe(user => { this.user = user; }, err => this.valid = false);
    }

    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
        if (localStorage.getItem('currentUser')) {
            // console.log('state', state);
            // this.getUser();

            this.userService.getUser().subscribe(user => {
                this.user = user;
                this.valid = true;
                // console.log('user', user);
            }, err => {
                // console.log('er', err);
                this.valid = false;
                localStorage.removeItem('currentUser');
                localStorage.removeItem('token');
                this.router.navigate(['/login'], { queryParams: { returnUrl: state.url }});
                // console.log('neautorizat erorr', this.valid);
            });

            return true;
        }

        // not logged in so redirect to login page with the return url
        this.router.navigate(['/login'], { queryParams: { returnUrl: state.url }});
        return false;
    }

    // private getUser() {
    //     this.userService.getUser().subscribe(user => { this.user = user; }, err => this.valid = false);
    // }

}
