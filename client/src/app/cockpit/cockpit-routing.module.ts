import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AuthGuard } from '../_guards';
import { CockpitsTabComponent } from './cockpits-tab/cockpits-tab.component';
// import { HeaderComponent } from './header/header.component';
import { EditCockpitBComponent } from './edit-cockpit-b/edit-cockpit-b.component';
import { AddChartsComponent } from './add-charts/add-charts.component';
import { ViewCockpitFinalComponent } from './view-cockpit-final/view-cockpit-final.component';
import { WysiwygComponent } from './wysiwyg/wysiwyg.component';
import { HeaderComponent } from '../components/header/header.component';

const routes: Routes = [
  { path: '', redirectTo: 'list', pathMatch: 'full'},
  { path: '', component: HeaderComponent, canActivate: [AuthGuard], data: {title: ''},
    children: [
        { path: '', redirectTo: 'list', pathMatch: 'full'},

        { path: 'list',       component: CockpitsTabComponent,      data: { title: 'Cockpit List' }},
        { path: 'edit/:id',   component: EditCockpitBComponent,     data: { title: 'Edit Cockpit' }},
        { path: 'charts/:id', component: AddChartsComponent,        data: { title: 'Add Charts'   }},
    ]
  },
  { path: 'view/:id',   component: ViewCockpitFinalComponent, data: { title: 'Cockpit'      }},
  { path: 'world', component: WysiwygComponent, data: {title: 'Wysiwyg'}},

  { path: '**', redirectTo: '' }



];

@NgModule({
  // imports: [RouterModule.forChild(routes)],
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class CockpitRoutingModule { }
