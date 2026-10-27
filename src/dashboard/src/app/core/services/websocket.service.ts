import { Injectable, signal, computed } from '@angular/core';

export interface Transaction {
  id: string;
  user_id: string;
  amount: number;
  currency: string;
  card_number_masked: string;
  merchant: string;
  location_country: string;
  ip_address: string;
  timestamp: number;
}

export interface FraudAlert {
  alert_id: string;
  transaction_id: string;
  user_id: string;
  amount: number;
  currency: string;
  reason: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  score: number;
  timestamp: number;
  ai_analysis?: string;
}


export interface SystemMetrics {
  current_tps: number;
  total_processed: number;
  total_frauds_detected: number;
  total_retained_amount: number;
}

export interface WsEvent {
  type: 'NewTransaction' | 'FraudAlertDetected' | 'MetricsUpdate';
  data: any;
}

@Injectable({
  providedIn: 'root',
})
export class WebsocketService {
  private socket: WebSocket | null = null;
  private reconnectInterval = 3000;
  private wsUrl = 'ws://localhost:3000/ws';

  // Angular Signals for high-performance reactive updates
  readonly connectionStatus = signal<'CONNECTING' | 'CONNECTED' | 'DISCONNECTED'>('DISCONNECTED');
  readonly metrics = signal<SystemMetrics>({
    current_tps: 0,
    total_processed: 0,
    total_frauds_detected: 0,
    total_retained_amount: 0,
  });
  readonly alerts = signal<FraudAlert[]>([]);
  readonly recentTransactions = signal<Transaction[]>([]);

  readonly fraudRate = computed(() => {
    const total = this.metrics().total_processed;
    const frauds = this.metrics().total_frauds_detected;
    if (total === 0) return 0;
    return Number(((frauds / total) * 100).toFixed(2));
  });

  constructor() {
    this.connect();
  }

  public connect(): void {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.connectionStatus.set('CONNECTING');

    try {
      this.socket = new WebSocket(this.wsUrl);

      this.socket.onopen = () => {
        this.connectionStatus.set('CONNECTED');
        console.log('[WebSocket] Conectado al Core API de Rust');
      };

      this.socket.onmessage = (event) => {
        try {
          const payload: WsEvent = JSON.parse(event.data);
          this.handleEvent(payload);
        } catch (e) {
          console.error('[WebSocket] Error parseando mensaje:', e);
        }
      };

      this.socket.onclose = () => {
        this.connectionStatus.set('DISCONNECTED');
        console.warn('[WebSocket] Conexión cerrada. Reconectando en 3s...');
        setTimeout(() => this.connect(), this.reconnectInterval);
      };

      this.socket.onerror = (err) => {
        console.error('[WebSocket] Error de socket:', err);
        this.socket?.close();
      };
    } catch (e) {
      this.connectionStatus.set('DISCONNECTED');
      setTimeout(() => this.connect(), this.reconnectInterval);
    }
  }

  private handleEvent(event: WsEvent): void {
    switch (event.type) {
      case 'NewTransaction': {
        const tx = event.data as Transaction;
        this.recentTransactions.update((list) => [tx, ...list.slice(0, 49)]);
        break;
      }
      case 'FraudAlertDetected': {
        const alert = event.data as FraudAlert;
        this.alerts.update((list) => [alert, ...list.slice(0, 99)]);
        break;
      }
      case 'MetricsUpdate': {
        const metrics = event.data as SystemMetrics;
        this.metrics.set(metrics);
        break;
      }
    }
  }
}
