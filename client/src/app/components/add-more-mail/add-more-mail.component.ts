import { Component, OnInit, Input} from '@angular/core';
import { FormBuilder, FormGroup, FormControl, FormArray } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { OfferService } from '../../_services/offer.service';
import { CustomObservable, CompanyService } from '../../_services';
import { ReloadService } from '../../_services/reload.sevice';
import { fail } from 'assert';
import { Admin } from '../../_models';

@Component({
  selector: 'app-add-more-mail',
  templateUrl: './add-more-mail.component.html',
  styleUrls: [
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css',
    // '../../../assets/css/styles/animate.css',
]
})
export class AddMoreMailComponent implements OnInit {
  @Input() type: any;
  id: number;
  mePattern = '[a-zA-Z0-9-.-_éèàûç]{1,}[@]{1}[a-zA-Z.-]{2,}[.]{1}[a-zA-Z]{2,}';
  addMailGroup: FormGroup;
  mailRows: FormControl;
  plusMail: boolean;
  mailExist = false;
  loading = false;
  add = false;
  mailForms = [];
  sme_emails: any;


  constructor(private mailList: FormBuilder,
              private offerService: OfferService,
              private toastr: ToastrService,
              private reloadService: ReloadService,
              private customObservable: CustomObservable,
              private companyService: CompanyService,
            ) { }

  ngOnInit() {
    this.createForm();
    this.changesAddMail();
    this.id = null;
    this.customObservable.isAddMail.subscribe(
      (data) => {
        if (data) {
          this.id = data.id;
          this.mailForms.length = 0;
          this.type = undefined;
          if (data['emails_list'][0] !== '') {
            data['emails_list'].forEach(element => { this.mailForms.push(this.mailList.group({mailname: element})); });
            const control = <FormArray>this.addMailGroup.controls['mailRows'];
            control.controls = this.mailForms;
            this.addNewRow();
          } else {
            const control = <FormArray>this.addMailGroup.controls['mailRows'];
            control.controls.length = 0;
            this.addNewRow();
          }
        }
      });

      if (this.type === 'adminT') {
        this.companyService.getDistributionSME().subscribe(
          (data) => {
            this.sme_emails = data;
            this.mailForms.length = 0;
            if (this.sme_emails !== '') {
              this.sme_emails.forEach(element => { this.mailForms.push(this.mailList.group({mailname: element.email})); });
              const control = <FormArray>this.addMailGroup.controls['mailRows'];
              control.controls = this.mailForms;
              this.addNewRow();
            } else {
              const control = <FormArray>this.addMailGroup.controls['mailRows'];
              control.controls.length = 0;
              this.addNewRow();
            }
           }
        );
      }

  }

  changesAddMail(): void {
    this.addMailGroup.get('mailRows').valueChanges.subscribe(val => { this.observableSourceAdd(val); });
  }

  observableSourceAdd(add: string) {
    if (add[add.length - 1]['mailname']) {
      if (add[add.length - 1]['mailname'].length > 0) {
        this.plusMail = true;
        this.mailExist = false;
        for (let index = 0; index < add.length - 1; index++) {
          if ( add.length > 1) {
            if ( add[index]['mailname']  === add[add.length - 1]['mailname']  ) {
                this.mailExist = true;
           }
          }
        }
      }
    }
  }

  initmailRows() {  return this.mailList.group({mailname: ['']});  }

  addNewRow() {
    this.plusMail = false;
    const control = <FormArray>this.addMailGroup.controls['mailRows'];
    control.push(this.initmailRows());
  }

  deleteRow(index: number) {
    const control = <FormArray>this.addMailGroup.controls['mailRows'];
    control.removeAt(index);
  }

  onSubmit(mails: any) {
    this.loading = true;
    if (this.type !== 'adminT') {
      this.offerService.insertMails(mails, this.id).subscribe(
        (data) => {
          this.addMailGroup.reset();
          const control = <FormArray>this.addMailGroup.controls['mailRows'];
          control.controls.length = 1;
          this.reloadService.changeEditOffer(true);
          this.showSuccess('Une adresse email en CC a été ajoutée');
          $('#cancelAddMail').click();
          $('#cancel').click();
          $('body').click();
          this.loading = false;
        },
        (errores) => {
          this.showError('L\'email n\'a pas été envoyé.');
          this.loading = false;
        });
    }

    if (this.type === 'adminT') {
      this.companyService.postDistributionSME(mails).subscribe(
        (data) => {
          this.loading = false;
          this.showSuccess('Une adresse email en CC a été ajoutée');
          $('#cancelAddMail').click();
          $('#cancel').click();
          $('body').click();
        },
        (er) => { this.loading = false;  this.showError('L\'email n\'a pas été envoyé.'); }
      );
    }
  }

  createForm() {
    this.add = true;
    this.addMailGroup = new FormGroup({
      mailRows: this.mailList.array([this.initmailRows()]),
    });
  }

  showSuccess(mesaj: string) { this.toastr.success(mesaj); }
  showError(mesaj: string) { this.toastr.error(mesaj); }

}
