class DotPlacer {
    private selectedColor: string | null = null;
    private currentDots: {row: number, col: number, color: string}[] = [];
    private colorCounter: {[color: string]: number} = {};

    private rows: number = 3;
    private cols: number = 3;

    constructor() {
      this.getRowsCols();
      this.getDots();
      this.initColorPicker();
      this.generateGrid()
      this.initSaveButton();
    }

    private getDots(): void {
      let inital_dots = document.getElementById('dots-json')?.innerHTML || '';
      this.currentDots = JSON.parse(inital_dots);
    }
    private getRowsCols(): void {
      let rows_str = document.getElementById('grid-container')?.getAttribute('data-rows') || '';
      let cols_str = document.getElementById('grid-container')?.getAttribute('data-cols') || '';
      this.rows = +rows_str;
      this.cols = +cols_str;
    }

    private initColorPicker(): void {
        document.querySelectorAll('.color-option').forEach(option => {
            option.addEventListener('click', () => {
                this.selectedColor = option.getAttribute('data-color');
                document.querySelectorAll('.color-option').forEach(o => 
                    o.classList.remove('selected'));
                option.classList.add('selected');
            });
        });
    }

    private generateGrid(): void {
        const container = document.getElementById('grid-container')!;
        container.innerHTML = '';
        
        container.style.display = 'grid';
        container.style.gridTemplateColumns = `repeat(${this.cols}, 80px)`;
        container.style.gridTemplateRows = `repeat(${this.cols}, 80px)`;
        container.style.gap = '2px';

        for (let i = 0; i < this.rows; i++) {
            for (let j = 0; j < this.cols; j++) {
                const cell = document.createElement('div');
                cell.className = 'cell bg-gray-200 cursor-pointer';
                cell.dataset.row = i.toString();
                cell.dataset.col = j.toString();
                

                cell.addEventListener('click', () => this.handleCellClick(cell));
                container.appendChild(cell);

                const existingDot = this.currentDots.find(d => d.row === i && d.col === j);
                if (existingDot) {
                  this.colorCounter[existingDot.color] = (this.colorCounter[existingDot.color] || 0) + 1;
                  const dot = document.createElement('div');
                  dot.style.backgroundColor = existingDot.color;
                  dot.className = 'dot';
                  cell.appendChild(dot);
                }
            }
        }
    }

    private handleCellClick(cell: HTMLDivElement): void {
        if (!this.selectedColor) return;

        const row = parseInt(cell.dataset.row!);
        const col = parseInt(cell.dataset.col!);
        
        // Sprawdź czy komórka jest pusta
        const existingDot = this.currentDots.find(d => d.row === row && d.col === col);
        if (existingDot) return;

        // Sprawdź limit kropek dla koloru
        if ((this.colorCounter[this.selectedColor] || 0) >= 2) return;

        // Dodaj kropkę
        this.currentDots.push({row, col, color: this.selectedColor});
        this.colorCounter[this.selectedColor] = (this.colorCounter[this.selectedColor] || 0) + 1;
        
        // Wizualizacja
        const dot = document.createElement('div');
        dot.style.backgroundColor = this.selectedColor;
        dot.className = 'dot';

        cell.appendChild(dot);
    }

    private initSaveButton(): void {
        const boardId = document.getElementById('board-id')?.getAttribute('value') || null;
        const url = `/gameboard/${boardId}/`;

        document.getElementById('save-btn')?.addEventListener('click', async () => {
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken(),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.currentDots)
                });

                console.log(JSON.stringify(this.currentDots));

                if (response.ok) {
                    alert('Plansza zapisana!');
                }
            } catch (error) {
                console.error('Błąd zapisu:', error);
            }
        });
    }

    private getCSRFToken(): string {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.getAttribute('value') || '';
    }
}

// Inicjalizacja po załadowaniu strony
document.addEventListener('DOMContentLoaded', () => {
    new DotPlacer();
});
