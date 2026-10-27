import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebsocketService } from '../../../../core/services/websocket.service';

@Component({
  selector: 'app-metrics-cards',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './metrics-cards.component.html',
  styleUrls: ['./metrics-cards.component.css']
})
export class MetricsCardsComponent {
  private wsService = inject(WebsocketService);
  
  readonly metrics = this.wsService.metrics;
  readonly fraudRate = this.wsService.fraudRate;
  readonly connectionStatus = this.wsService.connectionStatus;
}
