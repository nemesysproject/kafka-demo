import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <div class="app-layout">
      <header class="app-header">
        <div class="brand">
          <div class="logo-pulse"></div>
          <div class="brand-text">
            <span class="system-title">KRaft Sentinel</span>
            <span class="system-subtitle">Real-Time Fraud Detection Engine (Rust + Kafka)</span>
          </div>
        </div>
        <div class="system-status">
          <span class="status-indicator"></span>
          <span class="status-text">Pipeline Active</span>
        </div>
      </header>
      <main class="app-content">
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styles: [`
    .app-layout {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .app-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem 2rem;
      border-bottom: 1px solid var(--border-color);
      background: rgba(10, 13, 20, 0.85);
      backdrop-filter: blur(12px);
      position: sticky;
      top: 0;
      z-index: 50;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 1rem;
    }
    .logo-pulse {
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: var(--accent-cyan);
      box-shadow: 0 0 12px var(--accent-cyan);
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0% { transform: scale(0.95); opacity: 0.8; }
      50% { transform: scale(1.15); opacity: 1; }
      100% { transform: scale(0.95); opacity: 0.8; }
    }
    .brand-text {
      display: flex;
      flex-direction: column;
    }
    .system-title {
      font-weight: 700;
      font-size: 1.15rem;
      letter-spacing: -0.02em;
      color: #fff;
    }
    .system-subtitle {
      font-size: 0.75rem;
      color: var(--text-muted);
    }
    .system-status {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.25);
      padding: 0.35rem 0.85rem;
      border-radius: 9999px;
    }
    .status-indicator {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--status-safe);
    }
    .status-text {
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--status-safe);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .app-content {
      flex: 1;
      padding: 2rem;
      max-width: 1600px;
      width: 100%;
      margin: 0 auto;
    }
  `]
})
export class AppComponent {}
