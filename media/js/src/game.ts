class Gameboard {
    private currentDots: {row: number, col: number, color: string, paired: boolean}[] = [];
    private colorCounter: {[color: string]: number} = {};

    private canvas = document.getElementById('flowCanvas') as HTMLCanvasElement;
    private ctx = this.canvas.getContext('2d')!;

    private paths: { color: string; points: {x: number, y:number}[] }[] = [];
    private currentPath: { color: string; points: {x:number, y:number}[] } | null = null;

    private CELL = 82;

    private rows: number = 3;
    private cols: number = 3;

    constructor() {
      this.getRowsCols();
      this.getDots();
      this.getPaths();
      this.generateGrid();
      this.canvasInit();
      this.initSaveButton();
      this.canvas.height = this.rows * this.CELL;
      this.canvas.width = this.cols * this.CELL;
      this.drawPaths();
    }

    private getDots(): void {
      let inital_dots = document.getElementById('dots-json')?.innerHTML || '';
      if (inital_dots != "\"\"")
        this.currentDots = JSON.parse(inital_dots);
    }

    private getPaths(): void {
      let inital_paths = document.getElementById('paths-json')?.innerHTML || '';
      if (inital_paths != "\"\"")
        this.paths = JSON.parse(inital_paths);
    }

    private getRowsCols(): void {
      let rows_str = document.getElementById('grid-container')?.getAttribute('data-rows') || '';
      let cols_str = document.getElementById('grid-container')?.getAttribute('data-cols') || '';
      this.rows = +rows_str;
      this.cols = +cols_str;
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

    private drawPaths(): void {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.paths.forEach(path => {
        this.ctx.strokeStyle = path.color;
        this.ctx.lineWidth = this.CELL / 3;
        this.ctx.lineCap = 'round';
        this.ctx.beginPath();
        path.points.forEach((p, i) => {
          const cx = p.x * this.CELL + this.CELL / 2;
          const cy = p.y * this.CELL + this.CELL / 2;
          if (i === 0) this.ctx.moveTo(cx, cy);
          else this.ctx.lineTo(cx, cy);
        });
        this.ctx.stroke();
      });
      if (this.currentPath) {
        this.ctx.strokeStyle = this.currentPath.color;
        this.ctx.lineWidth = this.CELL / 3;
        this.ctx.beginPath();
        this.currentPath.points.forEach((p, i) => {
          const cx = p.x * this.CELL + this.CELL / 2;
          const cy = p.y * this.CELL + this.CELL / 2;
          if (i === 0) this.ctx.moveTo(cx, cy);
          else this.ctx.lineTo(cx, cy);
        });
        this.ctx.stroke();
      }
    }
    
    private getCellFromEvent(e: MouseEvent): {x:number, y:number} {
      const rect = this.canvas.getBoundingClientRect();
      const x = Math.floor((e.clientX - rect.left) / this.CELL);
      const y = Math.floor((e.clientY - rect.top) / this.CELL);
      return { x: this.clamp(x, 0, this.rows - 1), y: this.clamp(y, 0, this.rows - 1) };
    }

    private clamp(val: number, min: number, max: number): number {
      return Math.min(Math.max(val, min), max);
    }
    private getCSRFToken(): string {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.getAttribute('value') || '';
    }

    private canvasInit(): void {
      this.canvas.addEventListener('pointerdown', e => {
        const cell = this.getCellFromEvent(e as MouseEvent);
        const hit = this.currentDots.find(n => n.col === cell.x && n.row === cell.y && !n.paired);
        if (hit) {
          this.currentPath = { color: hit.color, points: [cell] };
        }
      });

      this.canvas.addEventListener('pointermove', e => {
        if (!this.currentPath) return;
        const cell = this.getCellFromEvent(e as MouseEvent);
        const last = this.currentPath.points[this.currentPath.points.length - 1];
        if (cell.x === last.x && cell.y === last.y) return;
        // ensure moving in straight rooe
        if (Math.abs(cell.x - last.x) + Math.abs(cell.y - last.y) === 1) {
          this.currentPath.points.push(cell);
          this.drawPaths();
        }
      });

      this.canvas.addEventListener('pointerup', () => {
        if (!this.currentPath) return;
        // check if ended on matching node
        const end = this.currentPath.points[this.currentPath.points.length - 1];
        const target = this.currentDots.find(
          n => n.col === end.x && n.row === end.y && n.color === this.currentPath!.color
        );
        if (target) {
          // finalize path
          this.paths.push(this.currentPath);
          // mark paired nodes
          this.currentDots.filter(n => n.color === this.currentPath?.color).forEach(n => n.paired = true);
        }
        this.currentPath = null;
        this.drawPaths()
      });
    }

    private initSaveButton(): void {
        const gameId = document.getElementById('game-id')?.getAttribute('value') || null;
        const url = `/game/${gameId}/`;

        document.getElementById('save-btn')?.addEventListener('click', async () => {
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken(),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.paths)
                });

                console.log(JSON.stringify(this.paths));

                if (response.ok) {
                    alert('Plansza zapisana!');
                }
            } catch (error) {
                console.error('Błąd zapisu:', error);
            }
        });
    }
}

// Inicjalizacja po załadowaniu strony
document.addEventListener('DOMContentLoaded', () => {
    new Gameboard();
});

