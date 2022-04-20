import { Component, OnInit } from '@angular/core';
import { CockpitService } from '../../_services/cockpit.service';
import { CockpitNews } from '../../_models/cockpitNews';
import { CustomObservable, CompanyService } from '../../_services';
import { ReloadService } from '../../_services/reload.sevice';

@Component({
  selector: 'app-cockpits-tab',
  templateUrl: './cockpits-tab.component.html',
  styleUrls: [
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css',
    // '../../../assets/css/styles/animate.css',
  ]
})
export class CockpitsTabComponent implements OnInit {
  cockpitNews: any;
  voirClients = [false];
  clients = {};
  count = [0];
  toPut: any;
  delCock: any;
  delCli:  any;
  detailCockpit: any;
  loadingSm = false;

  constructor(private cockpitService: CockpitService,
              private customObservable: CustomObservable,
              private reloadService: ReloadService) { }

  ngOnInit() {
    this.getCockpitNews();
    // tslint:disable-next-line:max-line-length
    this.reloadService.isReloadreloadCockpits.subscribe((data) => { if (data === true) { this.getCockpitNews(); this.reloadService.changereloadCockpits(false); }});
  }

  getCockpitNews() {
    this.cockpitService.getCockpitNews().subscribe(data => this.cockpitNews = data);
  }

  attachedUser(cockpit: any) {
    this.customObservable.changecockpitB(cockpit);
  }

  delClient() {
    this.loadingSm = true;
    this.cockpitNews.forEach(cockpit => {
      if ( cockpit.id === this.delCock.id) {
        const clientsAfterR = [];
        const idsAfterR = [];
        cockpit.clients.forEach(element => {
          if (element.id !== this.delCli.id) { clientsAfterR.push(element); idsAfterR.push(element.id); }
        });
        this.toPut = cockpit;
        this.toPut.clients = idsAfterR; // facem obiectul pentru put clients doar cu iduri
        this.cockpitService.putCockpitNewsById(this.toPut.id, this.toPut).subscribe((data) => { }, (er) => { this.getCockpitNews(); });
        cockpit.clients = clientsAfterR;
        this.loadingSm = false;
        $('#canceldeleteClients').click(); $('body').click();
      }
    });
  }

}
