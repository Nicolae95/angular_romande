import { Component, OnInit, Input } from '@angular/core';
import { SharableService } from '../../_services';

@Component({
  selector: 'app-deletesection',
  templateUrl: './deletesection.component.html',
  styleUrls: ['./deletesection.component.css']
})
export class DeletesectionComponent implements OnInit {

  @Input() active: boolean;

  constructor(private vano: SharableService) {}

  cmon: boolean;

  ngOnInit() {
    this.vano.adel.subscribe(cmon => this.cmon = cmon);
  }

  offMe() {
    this.vano.changeDel(this.cmon);
  }

}
