class RouteRenderer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private image: HTMLImageElement;
  private highlighted: number;
  

  constructor(image: HTMLImageElement) {
    this.canvas = document.getElementById('route-canvas') as HTMLCanvasElement;
    this.ctx = this.canvas.getContext('2d')!;
    this.image = image;
    this.highlighted = -1;
    
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
  }

  private resizeCanvas(): void {
    const rect = this.image.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }

  private scaleCoordinates(x: number, y: number): {x: number, y: number} {
    const naturalWidth = this.image.naturalWidth;
    const naturalHeight = this.image.naturalHeight;
    const displayedWidth = this.image.clientWidth;
    const displayedHeight = this.image.clientHeight;

    return {
      x: (x / naturalWidth) * displayedWidth,
      y: (y / naturalHeight) * displayedHeight
    };
  }

  public highlightPoint(id: number): void {
    this.highlighted = id;
  }

  public drawRoute(points: Array<{x: number, y: number, id:number}>): void {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Rysowanie linii trasy
    this.ctx.beginPath();
    points.forEach((point, index) => {
      const scaled = this.scaleCoordinates(point.x, point.y);
      if (index === 0) {
        this.ctx.moveTo(scaled.x, scaled.y);
      } else {
        this.ctx.lineTo(scaled.x, scaled.y);
      }
    });
    this.ctx.strokeStyle = '#ef4444'; // Tailwind red-500
    this.ctx.lineWidth = 2;
    this.ctx.stroke();

    // Rysowanie punktów
    points.forEach((point, index) => {
      const scaled = this.scaleCoordinates(point.x, point.y);
      this.ctx.beginPath();
      if (this.highlighted == point.id) {
        this.ctx.arc(scaled.x, scaled.y, 20, 0, Math.PI * 2);
        this.ctx.fillStyle = '#078dcca' // Tailwind bermuda
      } else {
        this.ctx.arc(scaled.x, scaled.y, 6, 0, Math.PI * 2);
        this.ctx.fillStyle = '#10b981'; // Tailwind emerald-500
      }
      this.ctx.fill();
      
      // Biała obwódka
      this.ctx.strokeStyle = 'white';
      this.ctx.lineWidth = 2;
      this.ctx.stroke();
      
      // Numer punktu
      this.ctx.fillStyle = '#1f2937'; // Tailwind gray-800
      this.ctx.font = '12px Arial';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(
        (index + 1).toString(),
        scaled.x,
        scaled.y - 10
      );
    });
  }
}

class RouteEditor {
  private routeRenderer: RouteRenderer;
  private imageElement: HTMLImageElement;
  private canvasElement: HTMLCanvasElement;

  private canvasContext: CanvasRenderingContext2D;
  
  constructor() {
    this.imageElement = document.getElementById('route-image') as HTMLImageElement;
    this.canvasElement = document.getElementById('route-canvas') as HTMLCanvasElement;
    this.canvasContext = this.canvasElement.getContext("2d")!;
    this.routeRenderer = new RouteRenderer(this.imageElement);
    
    this.initializeRoute();
    this.initImageClickHandler();
    this.initFormSubmitHandler();
    this.initPointHighlight();
  }

  private initializeRoute(): void {
    const points = this.getCurrentPoints();
    this.routeRenderer.drawRoute(points);
  }

  private initImageClickHandler(): void {
    this.canvasElement.addEventListener('click', (event) => {
      const rect = this.imageElement.getBoundingClientRect();
      const scaleX = this.imageElement.naturalWidth / rect.width;
      const scaleY = this.imageElement.naturalHeight / rect.height;
      
      const x = (event.clientX - rect.left) * scaleX;
      const y = (event.clientY - rect.top) * scaleY;

      (document.getElementById('id_x') as HTMLInputElement).value = Math.round(x).toString();
      (document.getElementById('id_y') as HTMLInputElement).value = Math.round(y).toString();
    });
  }

  private initFormSubmitHandler(): void {
    document.getElementById('point-form')?.addEventListener('submit', () => {
      setTimeout(() => this.routeRenderer.drawRoute(this.getCurrentPoints()), 100);
    });
  }

  private getCurrentPoints(): Array<{x: number, y: number, id:number}> {
    return Array.from(document.querySelectorAll('.point-item')).map(point => ({
      x: parseFloat(point.getAttribute('data-x')!),
      y: parseFloat(point.getAttribute('data-y')!),
      id: parseFloat(point.getAttribute('data-id')!)
    }));
  }

  private initPointHighlight(): void {
    document.querySelectorAll('.point-item').forEach(point => {
      point.addEventListener('mouseenter', () => {
        const id = parseFloat(point.getAttribute('data-id')!);
        this.routeRenderer.highlightPoint(id);
        this.initializeRoute();
      });
    });
  }
}

// Inicjalizacja
document.addEventListener('DOMContentLoaded', () => {
  new RouteEditor();
});
