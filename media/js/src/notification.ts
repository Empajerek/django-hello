class NotificationManager {
    private eventSource: EventSource | null = null;
    private notificationContainer: HTMLElement;
    private reconnectTimeout = 5000; // 5 seconds
    private sseUrl = '/sse/notifications/';

    constructor() {
        this.notificationContainer = this.createNotificationContainer();
        this.initSSE();
    }

    private initSSE(): void {
        this.eventSource = new EventSource(this.sseUrl);
        
        // Obsługa otwarcia połączenia
        this.eventSource.onopen = () => {
            console.log('SSE connection opened');
            this.showNotification('Połączenie z powiadomieniami ustanowione', 'info');
        };
        
        // Obsługa błędów
        this.eventSource.onerror = (event) => {
            console.error('SSE error:', event);
            this.showNotification('Błąd połączenia z powiadomieniami. Próba ponownego połączenia...', 'error');
            
            // Zamknij istniejące połączenie
            if (this.eventSource) {
                this.eventSource.close();
            }
            
            // Spróbuj ponownie po czasie
            setTimeout(() => this.initSSE(), this.reconnectTimeout);
        };
        
        // Obsługa zdarzeń
        this.eventSource.addEventListener('newBoard', (event) => {
            const data = JSON.parse((event as MessageEvent).data);
            this.handleNewBoard(data);
        });
        
        this.eventSource.addEventListener('newGame', (event) => {
            const data = JSON.parse((event as MessageEvent).data);
            this.handleNewPath(data);
        });
    }
    
    private handleNewBoard(data: any): void {
        const message = `Użytkownik <strong>${data.creator_username}</strong> utworzył nową planszę: <strong>${data.board_name}</strong>`;
        this.showNotification(message, 'success', () => {
            // Przejdź do planszy po kliknięciu
            window.location.href = `/gameboard/${data.board_id}/`;
        });
    }
    
    private handleNewPath(data: any): void {
        const message = `Użytkownik <strong>${data.user_username}</strong> zapisał ścieżkę na planszy: <strong>${data.board_name}</strong>`;
        this.showNotification(message, 'info', () => {
            // Przejdź do planszy po kliknięciu
            window.location.href = `/gameboard/${data.board_id}/`;
        });
    }
    
    private createNotificationContainer(): HTMLElement {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'fixed top-4 right-4 space-y-2 z-50 w-80';
        document.body.appendChild(container);
        return container;
    }
    
    public showNotification(
        message: string, 
        type: 'success'|'error'|'info' = 'info',
        onClick?: () => void
    ): void {
        const notification = document.createElement('div');
        notification.className = `p-4 rounded-lg shadow-lg cursor-pointer transition-all transform hover:scale-105 ${
            type === 'success' ? 'bg-green-100 border-green-500 text-green-700' :
            type === 'error' ? 'bg-red-100 border-red-500 text-red-700' :
            'bg-blue-100 border-blue-500 text-blue-700'
        } border-l-4`;
        notification.innerHTML = message;
        
        // Animacja pojawiania się
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        notification.style.transition = 'opacity 0.3s, transform 0.3s';
        
        this.notificationContainer.prepend(notification);
        
        // Uruchom animację
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // Obsługa kliknięcia
        if (onClick) {
            notification.addEventListener('click', onClick);
        }
        
        // Automatyczne zniknięcie po czasie
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
  new NotificationManager();
});

