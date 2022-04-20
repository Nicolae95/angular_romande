import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { PfcMarketUploadComponent } from './pfc-market-upload/pfc-market-upload.component';
import { PfcUploadComponent } from './pfc-upload/pfc-upload.component';
import { PfcComponent } from './pfc/pfc.component';
import { PfcMarketComponent } from './pfc-market/pfc-market.component';
import { AuthGuard } from './../_guards/index';



const routes: Routes = [
  // { path: '', redirectTo: 'upload', pathMatch: 'full'},

  { path: '',    component: PfcComponent, canActivate: [AuthGuard] , data: {title: 'Pfc'},
    children: [
        { path: '', redirectTo: 'upload', pathMatch: 'full'},
        { path: 'upload', component: PfcUploadComponent ,  data: {title: 'Upload'}}
      ]
  },



  // { path: '**', redirectTo: 'upload', pathMatch: 'full'},

];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class PfcRoutingModule { }
