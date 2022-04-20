import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-view-cockpit-final',
  templateUrl: './view-cockpit-final.component.html',
  styleUrls: ['./view-cockpit-final.component.css']
})

export class ViewCockpitFinalComponent implements OnInit {
  id: number;

  constructor(private activatedRoute: ActivatedRoute, private router: Router) {
    this.activatedRoute.params.subscribe( params =>  {this.id = params.id; });
    }

  ngOnInit() {
    $(document).keyup(function(e) {
      if (e.keyCode === 27 ) {
      $('.closeallbtn').click();
      }
    });
    if ( !this.id ) { this.router.navigate(['cockpits/list']); }
  }

}
