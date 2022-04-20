import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AnalyticsComponent } from './analytics/analytics.component';
import { AnlTablauBordComponent } from './anl-tablau-bord/anl-tablau-bord.component';
import { AnlOffersComponent } from './anl-offers/anl-offers.component';
import { AnlActivitiClientComponent } from './anl-activiti-client/anl-activiti-client.component';
import { AnlInteretBarChartComponent } from './anl-interet-bar-chart/anl-interet-bar-chart.component';
import { UserActivityAnalyticsComponent } from './user-activity-analytics/user-activity-analytics.component';
import { WysiwygComponent } from './wysiwyg/wysiwyg.component';
import { WorldMapComponent } from './world-map/world-map.component';

const routes: Routes = [
  // { path: '**', redirectTo: 're' },
  { path: '', component: AnalyticsComponent,  data: {title: 'Analytics'},
      children: [
        { path: '', redirectTo: 'tableau', pathMatch: 'full'},
        { path: 'tableau', component: AnlTablauBordComponent, data: {title: 'Tableau de bord'}},
        { path: 'offres', component: AnlOffersComponent, data: {title: 'Offres'}},
        { path: 'activite', component: AnlActivitiClientComponent, data: {title: 'Activité'}},
        { path: 'world', component: WorldMapComponent, data: {title: 'Activité'}}
      ]
    },
  ];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AnalitycsRoutingModule { }
