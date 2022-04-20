import { Component, OnInit, Input} from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { CompanyService, CustomObservable } from '../../_services';
import { CockpitService } from '../../_services/cockpit.service';
import { ReloadService } from '../../_services/reload.sevice';
import { OfferService, } from '../../_services/offer.service';

@Component({
  selector: 'app-add-cockpit',
  templateUrl: './add-cockpit.component.html',
  styleUrls: [
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css',
    // '../../../assets/css/styles/animate.css',
  ]
})


export class AddCockpitComponent implements OnInit {
  @Input() type: any;

  cockpitB: FormGroup;
  cockpitName: FormControl;
  cockpitClients: FormControl;
  ofersList: FormControl;
  loading = false;
  offersList = [];
  offersSettings = {};
  selectedoffers = [];
  // ids = [];
  attachedUser: any;
  edit: boolean;
  id: number;
  clientList: any;
  ngClients: any;
  obj_editer: any;

  constructor(private companyService:   CompanyService,
              private cockpitService:   CockpitService,
              private toastr:           ToastrService,
              private reloadService:    ReloadService,
              private offerService:     OfferService,
              private customObservable: CustomObservable,
            ) { }

  ngOnInit() {
    this.createForm();
    this.customObservable.iscockpitB.subscribe((data) => {
      if (data === true) { this.createForm(); this.getAllList(); }
      try {
        if (data.id) { this.obj_editer = data;
           this.getOfferListBy(data.clients[0].id , true); this.getAllList(); this.editForm(data);  }
      } catch (error) { }
    });
  }

  getAllList() {
    this.companyService.getAllList().subscribe( (data) => { this.clientList = data; } );
  }



  onSubmit(forms: any) {

    const cockpitClients = [];
    cockpitClients.push(Number(this.cockpitClients.value));
    const ofersList = [];
    if (forms.ofersList) { if (forms.ofersList.length !== 0) { forms.ofersList.forEach(e => {ofersList.push(Number(e.id)); }); } }
    const objectSubmit = { name: forms.cockpitName, clients: cockpitClients };

    console.log('objectSubmit', objectSubmit);
    if (!this.edit) { // adaugare
      this.cockpitService.postCockpitNews(objectSubmit).subscribe(
        (data) => {
                    // console.log(data);
                    if (ofersList.length !== 0) { this.addOffersToclient(data['id'], ofersList); }
                    this.cockpitB.reset();
                    this.reloadService.changereloadCockpits(true);
                    this.toastr.success('L\' Cockpit  pas été souvegarder.');
                    $('#cancelcreateNewCockpitB').click(); $('body').click();
                    this.loading = false;
                  },
        (er) => { this.toastr.error(er);    this.loading = false; }
      );
    } else if (this.edit) { // editare
      this.cockpitService.editCockpitNewsById(this.obj_editer.id , objectSubmit).subscribe(
        (data) => {
                    if (ofersList.length !== 0) { this.addOffersToclient(data['id'], ofersList); }
                    this.cockpitB.reset();
                    this.reloadService.changereloadCockpits(true);
                    this.toastr.success('L\' Cockpit  pas été souvegarder.');
                    $('#cancelcreateNewCockpitB').click(); $('body').click();
                    this.loading = false;
                  },
        (er) => { this.toastr.error(er);    this.loading = false; }
      );
    }
  }


  addOffersToclient(id: number, oferts: any) {
    this.cockpitService.putCockpitNewsOffer(id, oferts).subscribe(
      (data) => { },
      (e) => { }
    );
  }

  editForm(data: any) {
    this.cockpitName = new FormControl(data.name, Validators.required);
    if (data.clients[0]) { this.cockpitClients = new FormControl(data.clients[0].id);
    } else { this.cockpitClients = new FormControl(''); }
    this.ofersList = new FormControl();
    this.cockpitB = new FormGroup({
      cockpitName: this.cockpitName,
      cockpitClients: this.cockpitClients,
      ofersList: this.ofersList
    });

    if (data) {
      this.edit = true;
      this.cockpitB.get('cockpitName').setValue(data.name);
      this.ngClients = data.clients[0].id;

    } else { this.edit = false; this.selectedoffers = [];  this.cockpitB.reset(); }

  }

  createForm() {
    this.cockpitName = new FormControl('', Validators.required);
    this.cockpitClients = new FormControl('');
    this.ofersList = new FormControl();
    this.cockpitB = new FormGroup({
      cockpitName: this.cockpitName,
      cockpitClients: this.cockpitClients,
      ofersList: this.ofersList
    });
    this.ngClients = null;
  }

  multiSelect(data: any, edit: boolean) {
    this.selectedoffers = [];
    this.offersList.length = 0;
    this.offersList = [];
    // da add from
    if (data) {
      data.forEach(client => { this.offersList.push({'id' : client['id'], 'itemName' : client['name']}); });
    }
    if (edit === true) { // for edit from
      this.selectedoffers = [];
      data.forEach(all_offer => {
        this.obj_editer.offers.forEach(my_el => {
          if (all_offer.id === my_el.id) {
            // this.selectedoffers.push(all_offer.id);
            this.selectedoffers.push({'id' : my_el['id'], 'itemName' : my_el['name']});
          }
        });
      });
    }




    this.offersSettings = {
      singleSelection: false,
      text: 'Attach Offres',
      enableSearchFilter: true,
      selectAllText: 'Tout sélectionner',
      unSelectAllText: 'Tout désélectionner',
      classes: 'myclass custom-class '
    };
  }

  getOfferListBy(id: number, edit?: boolean ) {
    this.offersList.length = 0;
    if (id) {
      this.cockpitB.get('cockpitClients').setValue(id);
      this.offerService.getOfferList(id, '').subscribe(
        (data) => {
          if (edit) {
            this.multiSelect(data, true);
          } else { this.multiSelect(data, false); }
         }
      );
    }
  }




}
