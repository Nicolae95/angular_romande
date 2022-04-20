
import { User } from './../../_models/user';
import { CcService } from './../../_services/cc.service';
import { Component, HostListener} from '@angular/core';
import 'rxjs/add/operator/switchMap';
import { Router, ActivatedRoute, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';


@Component({
  selector: 'app-offermail',
  templateUrl: './offermail.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/animate.css',
    // '../../../assets/css/styles/theme.css',
]
})

export class OffermailComponent {
  currentUser: User;
  idOffer: any;
  token: string;
  chartByYears: any;
  loading = false;
  nr = 0;

  constructor(private ccService: CcService,
              private router: Router,
              private activatedRoute: ActivatedRoute
              ) {
                this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
                this.activatedRoute.params.subscribe ( params =>  {this.token = params.token; });
                this.data();
        }


  data() {
    console.log(' data() {}', this.token);
    this.ccService.getOfferByToken(this.token).subscribe(
       (data) => { this.idOffer = data.id;  console.log('getOfferByToken', data); },
       (er) => { console.log('errr', er); },
       () => { console.log('nimic'); },
      //  (er) => { this.router.navigate(['/login']; }
       );
    // setInterval(() =>  this.yourfunction(new MouseEvent('click', {bubbles: true})), 15000);
    }

    // @HostListener('mouseover') onHover() {
    //   window.onbeforeunload = function() {
    //     return confirm('Do you  want to leave?');
    //   };
    // }



  // canDeactivate(): any {
  //   // insert logic to check if there are pending changes here;
  //   // returning true will navigate without confirmation
  //   // returning false will show a confirm alert before navigating away
  // }

  // // @HostListener allows us to also guard against browser refresh, close, etc.
  // @HostListener('window:beforeunload', ['$event'])
  // yourfunction($event: any) { console.log($event);
  //   if (!this.canDeactivate()) {
  //       $event.returnValue = 'cirjova';
  //   }

  // }

}
