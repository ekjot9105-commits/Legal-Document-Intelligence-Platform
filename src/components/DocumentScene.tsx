import { useEffect, useRef } from 'react'

type DocumentSceneProps = { active: boolean }
const particles = Array.from({ length: 30 }, (_, index) => ({ x: (index * 47) % 420, y: (index * 73) % 370, radius: index % 3 === 0 ? 2 : 1, speed: 0.15 + (index % 4) * 0.04 }))

export default function DocumentScene({ active }: DocumentSceneProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  useEffect(() => {
    if (!active) return
    const canvas = canvasRef.current
    const context = canvas?.getContext('2d')
    if (!canvas || !context) return
    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    canvas.width = 520 * dpr; canvas.height = 450 * dpr; context.scale(dpr, dpr)
    let frame = 0; let animationFrame = 0
    const render = () => {
      context.clearRect(0, 0, 520, 450)
      const time = frame * 0.012
      particles.forEach((particle, index) => {
        const x = particle.x + Math.sin(time * particle.speed + index) * 12
        const y = (particle.y + frame * particle.speed) % 410
        context.beginPath(); context.arc(x, y, particle.radius, 0, Math.PI * 2)
        context.fillStyle = index % 5 === 0 ? '#b4f1e6' : 'rgba(255,255,255,.42)'; context.fill()
      })
      context.save(); context.translate(260, 208); context.rotate(Math.sin(time) * 0.025)
      context.shadowColor = 'rgba(120, 240, 218, .2)'; context.shadowBlur = 30
      context.fillStyle = 'rgba(19, 34, 47, .95)'; context.strokeStyle = 'rgba(180, 241, 230, .55)'; context.lineWidth = 1
      context.beginPath(); context.roundRect(-112, -148, 224, 296, 10); context.fill(); context.stroke(); context.shadowBlur = 0
      context.fillStyle = 'rgba(180, 241, 230, .88)'; context.fillRect(-78, -98, 70, 4)
      context.fillStyle = 'rgba(255,255,255,.35)'; for (let line = 0; line < 8; line += 1) context.fillRect(-78, -63 + line * 23, 154 - (line % 3) * 25, 3)
      context.fillStyle = 'rgba(255, 193, 92, .85)'; context.fillRect(-78, 38, 115, 7)
      context.fillStyle = 'rgba(116, 224, 203, .9)'; context.fillRect(-78, 86, 66, 7); context.restore()
      frame += 1; animationFrame = window.requestAnimationFrame(render)
    }
    render(); return () => window.cancelAnimationFrame(animationFrame)
  }, [active])
  return <canvas ref={canvasRef} className="scene-canvas" aria-hidden="true" />
}
