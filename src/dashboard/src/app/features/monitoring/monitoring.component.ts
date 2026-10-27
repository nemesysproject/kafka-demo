import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MetricsCardsComponent } from './components/metrics-cards/metrics-cards.component';
import { AlertFeedComponent } from './components/alert-feed/alert-feed.component';
import { WebsocketService } from '../../core/services/websocket.service';

@Component({
  selector: 'app-monitoring',
  standalone: true,
  imports: [CommonModule, MetricsCardsComponent, AlertFeedComponent],
  templateUrl: './monitoring.component.html',
  styleUrls: ['./monitoring.component.css']
})
export class MonitoringComponent {
  private wsService = inject(WebsocketService);

  readonly recentTransactions = this.wsService.recentTransactions;
  readonly connectionStatus = this.wsService.connectionStatus;

  reconnect(): void {
    this.wsService.connect();
  }
}
