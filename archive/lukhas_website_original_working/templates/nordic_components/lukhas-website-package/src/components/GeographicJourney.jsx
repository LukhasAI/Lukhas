import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const GeographicJourney = () => {
  const containerRef = useRef(null);
  const canvasRef = useRef(null);
  const [currentStage, setCurrentStage] = useState(0);
  
  const journeyStages = [
    {
      id: 'jerez',
      title: 'Cuartillos, Jerez de la Frontera',
      subtitle: 'Where innovation begins',
      description: 'In the heart of Andalusian vineyards, LUKHΛS takes root',
      image: '/journey-images/jerez-vineyards.jpg',
      zoom: 1,
      position: { x: 0, y: 0 },
      wireframe: false
    },
    {
      id: 'spain-aerial',
      title: 'Rising Above Spain',
      subtitle: 'Expanding horizons',
      description: 'From local innovation to national impact',
      image: null,
      zoom: 0.3,
      position: { x: -20, y: -30 },
      wireframe: true,
      wireframeType: 'spain'
    },
    {
      id: 'europe',
      title: 'European Vision',
      subtitle: 'Continental reach',
      description: 'Connecting European values with technological advancement',
      image: null,
      zoom: 0.1,
      position: { x: -50, y: -60 },
      wireframe: true,
      wireframeType: 'europe'
    },
    {
      id: 'eurasia',
      title: 'Transcontinental Bridge',
      subtitle: 'East meets West',
      description: 'Bridging European ethics with global innovation',
      image: null,
      zoom: 0.05,
      position: { x: -80, y: -70 },
      wireframe: true,
      wireframeType: 'eurasia'
    },
    {
      id: 'pacific',
      title: 'Pacific Crossing',
      subtitle: 'Global connectivity',
      description: 'Spanning oceans to connect minds',
      image: null,
      zoom: 0.02,
      position: { x: -120, y: -60 },
      wireframe: true,
      wireframeType: 'pacific'
    },
    {
      id: 'san-francisco',
      title: 'San Francisco Bay',
      subtitle: 'Innovation destination',
      description: 'Honoring the pioneers of artificial intelligence',
      image: '/journey-images/golden-gate.jpg',
      zoom: 1,
      position: { x: -150, y: -40 },
      wireframe: false
    }
  ];

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Wireframe drawing functions
    const drawWireframe = (type, zoom, position) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 1 / zoom;
      ctx.globalAlpha = 0.6;

      const centerX = canvas.width / 2 + position.x * zoom * 10;
      const centerY = canvas.height / 2 + position.y * zoom * 10;

      switch (type) {
        case 'spain':
          drawSpainWireframe(ctx, centerX, centerY, zoom);
          break;
        case 'europe':
          drawEuropeWireframe(ctx, centerX, centerY, zoom);
          break;
        case 'eurasia':
          drawEurasiaWireframe(ctx, centerX, centerY, zoom);
          break;
        case 'pacific':
          drawPacificWireframe(ctx, centerX, centerY, zoom);
          break;
      }
    };

    const drawSpainWireframe = (ctx, centerX, centerY, zoom) => {
      const scale = zoom * 200;
      // Simplified Spain outline
      ctx.beginPath();
      ctx.moveTo(centerX - 60 * scale, centerY - 40 * scale);
      ctx.lineTo(centerX + 40 * scale, centerY - 30 * scale);
      ctx.lineTo(centerX + 50 * scale, centerY + 20 * scale);
      ctx.lineTo(centerX - 70 * scale, centerY + 30 * scale);
      ctx.closePath();
      ctx.stroke();
      
      // Add grid lines
      for (let i = -3; i <= 3; i++) {
        ctx.beginPath();
        ctx.moveTo(centerX + i * 30 * scale, centerY - 50 * scale);
        ctx.lineTo(centerX + i * 30 * scale, centerY + 50 * scale);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(centerX - 100 * scale, centerY + i * 20 * scale);
        ctx.lineTo(centerX + 100 * scale, centerY + i * 20 * scale);
        ctx.stroke();
      }
    };

    const drawEuropeWireframe = (ctx, centerX, centerY, zoom) => {
      const scale = zoom * 100;
      // Simplified Europe outline
      ctx.beginPath();
      ctx.moveTo(centerX - 100 * scale, centerY - 80 * scale);
      ctx.lineTo(centerX + 120 * scale, centerY - 60 * scale);
      ctx.lineTo(centerX + 150 * scale, centerY + 100 * scale);
      ctx.lineTo(centerX - 120 * scale, centerY + 80 * scale);
      ctx.closePath();
      ctx.stroke();
      
      // Connection lines
      for (let i = 0; i < 8; i++) {
        const angle = (i / 8) * Math.PI * 2;
        const x1 = centerX + Math.cos(angle) * 50 * scale;
        const y1 = centerY + Math.sin(angle) * 50 * scale;
        const x2 = centerX + Math.cos(angle) * 120 * scale;
        const y2 = centerY + Math.sin(angle) * 120 * scale;
        
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
      }
    };

    const drawEurasiaWireframe = (ctx, centerX, centerY, zoom) => {
      const scale = zoom * 50;
      // Continental outline
      ctx.beginPath();
      ctx.moveTo(centerX - 200 * scale, centerY - 100 * scale);
      ctx.lineTo(centerX + 300 * scale, centerY - 80 * scale);
      ctx.lineTo(centerX + 350 * scale, centerY + 150 * scale);
      ctx.lineTo(centerX - 180 * scale, centerY + 120 * scale);
      ctx.closePath();
      ctx.stroke();
      
      // Network connections
      const points = [
        { x: centerX - 100 * scale, y: centerY - 50 * scale },
        { x: centerX, y: centerY },
        { x: centerX + 150 * scale, y: centerY - 30 * scale },
        { x: centerX + 200 * scale, y: centerY + 50 * scale }
      ];
      
      points.forEach((point, i) => {
        points.forEach((otherPoint, j) => {
          if (i !== j) {
            ctx.beginPath();
            ctx.moveTo(point.x, point.y);
            ctx.lineTo(otherPoint.x, otherPoint.y);
            ctx.stroke();
          }
        });
      });
    };

    const drawPacificWireframe = (ctx, centerX, centerY, zoom) => {
      const scale = zoom * 30;
      // Ocean grid
      for (let i = -10; i <= 10; i++) {
        for (let j = -10; j <= 10; j++) {
          const x = centerX + i * 50 * scale;
          const y = centerY + j * 50 * scale;
          
          ctx.beginPath();
          ctx.arc(x, y, 2 * scale, 0, Math.PI * 2);
          ctx.stroke();
          
          if (i < 10) {
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x + 50 * scale, y);
            ctx.stroke();
          }
          
          if (j < 10) {
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x, y + 50 * scale);
            ctx.stroke();
          }
        }
      }
    };

    // Animation timeline
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: container,
        start: 'top top',
        end: 'bottom bottom',
        scrub: 1,
        pin: true,
        onUpdate: (self) => {
          const progress = self.progress;
          const stageIndex = Math.floor(progress * journeyStages.length);
          const stageProgress = (progress * journeyStages.length) % 1;
          
          setCurrentStage(stageIndex);
          
          if (journeyStages[stageIndex]?.wireframe) {
            const stage = journeyStages[stageIndex];
            drawWireframe(stage.wireframeType, stage.zoom + stageProgress * 0.1, stage.position);
          }
        }
      }
    });

    return () => {
      ScrollTrigger.getAll().forEach(trigger => trigger.kill());
    };
  }, []);

  const currentStageData = journeyStages[currentStage] || journeyStages[0];

  return (
    <section ref={containerRef} className="relative h-[600vh] overflow-hidden">
      {/* Canvas for wireframes */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 z-10 pointer-events-none"
        style={{ mixBlendMode: 'multiply' }}
      />
      
      {/* Background images */}
      {journeyStages.map((stage, index) => (
        stage.image && (
          <div
            key={stage.id}
            className={`absolute inset-0 transition-opacity duration-1000 ${
              currentStage === index ? 'opacity-100' : 'opacity-0'
            }`}
            style={{
              backgroundImage: `url(${stage.image})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              transform: `scale(${stage.zoom})`,
            }}
          />
        )
      ))}
      
      {/* Wireframe background for wireframe stages */}
      {currentStageData.wireframe && (
        <div className="absolute inset-0 bg-gradient-to-br from-slate-50 to-blue-50" />
      )}
      
      {/* Content overlay */}
      <div className="absolute inset-0 z-20 flex items-center justify-center">
        <div className="text-center text-white max-w-4xl px-6">
          <div className="bg-black/20 backdrop-blur-md rounded-2xl p-8 border border-white/20">
            <h2 className="text-5xl md:text-7xl font-light mb-4 lambda">
              {currentStageData.title}
            </h2>
            <h3 className="text-2xl md:text-3xl font-light mb-6 text-blue-200">
              {currentStageData.subtitle}
            </h3>
            <p className="text-xl md:text-2xl leading-relaxed text-white/90">
              {currentStageData.description}
            </p>
            
            {/* Progress indicator */}
            <div className="flex justify-center mt-8 space-x-2">
              {journeyStages.map((_, index) => (
                <div
                  key={index}
                  className={`w-3 h-3 rounded-full transition-all duration-300 ${
                    index === currentStage
                      ? 'bg-blue-400 scale-125'
                      : index < currentStage
                      ? 'bg-blue-600'
                      : 'bg-white/30'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-30">
        <div className="flex flex-col items-center text-white/70">
          <div className="text-sm mb-2">Scroll to journey</div>
          <div className="w-6 h-10 border-2 border-white/30 rounded-full flex justify-center">
            <div className="w-1 h-3 bg-white/50 rounded-full mt-2 animate-bounce" />
          </div>
        </div>
      </div>
    </section>
  );
};

export default GeographicJourney;

