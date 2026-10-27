import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebsocketService, FraudAlert } from '../../../../core/services/websocket.service';

@Component({
  selector: 'app-alert-feed',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './alert-feed.component.html',
  styleUrls: ['./alert-feed.component.css']
})
export class AlertFeedComponent {
  private wsService = inject(WebsocketService);
  readonly alerts = this.wsService.alerts;

  getSeverityBadgeClass(severity: string): string {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
        return 'badge-critical';
      case 'HIGH':
        return 'badge-high';
      case 'MEDIUM':
        return 'badge-medium';
      default:
        return 'badge-low';
    }
  }

  formatTime(timestamp: number): string {
    return new Date(timestamp * 1000).toLocaleTimeString();
  }
}
