import { Component, OnInit, Input } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { CockpitService } from '../../_services/cockpit.service';

@Component({
  selector: 'app-edit-cockpit-b',
  templateUrl: './edit-cockpit-b.component.html',
  styleUrls: [
    // './edit-cockpit-b.component.css',
    //           '../../../assets/css/styles/nexus.css',
    //           '../../../assets/css/styles/layout.css',
    //           '../../../assets/css/styles/theme.css'
            ]
})
export class EditCockpitBComponent implements OnInit {

 id: number;
 cockpit: any;
 nameMenu = 'general';
 contenTab = 'manag';

 constructor(private activatedRoute: ActivatedRoute,
             private router: Router,
             private cockpitService: CockpitService,
             private toastr: ToastrService) {
             this.activatedRoute.params.subscribe( params =>  {this.id = params.id; });
            }

  ngOnInit() {
    if (this.id) { this.getcockpit(this.id); }
  }

  getcockpit(id: number) {
    this.cockpitService.getCockpitNewsById(Number(this.id)).subscribe(
      (data) => {console.log('cockpit', data); this.cockpit = data; },
      (er) => { this.router.navigate(['/cockpit']); }
    );
  }

}
