import { Component, OnInit, Input } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { CockpitService } from '../../_services/cockpit.service';

@Component({
  selector: 'app-edit-cockpit-b',
  templateUrl: './edit-cockpit-b.component.html',
  styleUrls: [
    './edit-cockpit-b.component.css',
    // '../../../assets/css/cockpitB.css',
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

 frequencySetings: any;


 days = [
  {'id' : 1, 'itemName' : 'Lundi'},
  {'id' : 2, 'itemName' : 'Mardi'},
  {'id' : 3, 'itemName' : 'Mercredi'},
  {'id' : 4, 'itemName' : 'Jeudi'},
  {'id' : 5, 'itemName' : 'Vendredi'},
  // {'id' : 6, 'itemName' : 'Samedi'},
  // {'id' : 7, 'itemName' : 'Dimanche'},
 ];

 name: any;
 emp_news: any;
 romande_news: any;
 email_name: any;
 automatic: any;
 weekdays = [];
 frequency: any;

 constructor(private activatedRoute: ActivatedRoute,
             private router: Router,
             private cockpitService: CockpitService,
             private toastr: ToastrService) {
             this.activatedRoute.params.subscribe( params =>  {this.id = params.id; });
            }

  ngOnInit() {
    if (this.id) { this.getcockpit(this.id); }

    this.frequencySetings = {
      singleSelection: false,
      text: 'Veuillez choisir le(s) jour(s) souhaité(s)',
      selectAllText: 'Tout sélectionner',
      unSelectAllText: 'Tout désélectionner',
      classes: 'myclass1 custom-class',

    };
  }

  getcockpit(id: number) {
    this.cockpitService.getCockpitNewsById(Number(this.id)).subscribe(
      (data) => {
        console.log('cockpit', data);
         this.cockpit = data;
         this.name = this.cockpit.name;
         this.emp_news = this.cockpit.emp_news;
         this.romande_news = this.cockpit.romande_news;
         this.email_name = this.cockpit.email_name;
         this.automatic = this.cockpit.automatic;
         this.cockpit.weekdays.forEach(element => {
           switch (element) {
            case 1: this.weekdays.push({'id' : 1, 'itemName' : 'Lundi'});    break;
            case 2: this.weekdays.push({'id' : 2, 'itemName' : 'Mardi'});    break;
            case 3: this.weekdays.push({'id' : 3, 'itemName' : 'Mercredi'}); break;
            case 4: this.weekdays.push({'id' : 4, 'itemName' : 'Jeudi'});    break;
            case 5: this.weekdays.push({'id' : 5, 'itemName' : 'Vendredi'}); break;
           }
         });
         },
      (er) => { this.router.navigate(['/cockpit']); }
    );
  }

  onSubmit() {
    const obj = {
      name: this.name,
      emp_news: this.emp_news,
      romande_news: this.romande_news,
      email_name: this.email_name,
      automatic: this.automatic,
      weekdays: [],
    };
    this.weekdays.forEach(e => { obj.weekdays.push(e.id); });
    console.log('obj', obj);
    this.cockpitService.editCockpit(this.cockpit.id, obj).subscribe(
      (data) => {
        this.toastr.success('Cockpit was updated');
        this.router.navigate(['/cockpits']); },
      (er) => {  this.toastr.success('Error'); },
    );
  }

  deleteCockpit() {
    this.cockpitService.deleteCockpitNewsById(this.cockpit.id).subscribe(
      (data) => {
        this.toastr.success('Cockpit was deleted');
        this.router.navigate(['/cockpits']); },
      (er) => {  this.toastr.success('Error'); },
    );
  }

}
