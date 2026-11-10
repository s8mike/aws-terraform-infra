// A titled row of headline number cards, used for operator, manager and report figures.
// Each card gets a color tone: pass "tone" to choose one, otherwise it is inferred from the label.
type Tone = 'blue' | 'green' | 'amber' | 'slate'

interface SummaryCardsProps {
  title: string
  items: { label: string; value: string; tone?: Tone }[]
}

// Pick a tone from the wording of the label so related figures share a color on every screen.
function toneFor(label: string): Tone {
  const text = label.toLowerCase()
  if (text.includes('delay')) return 'amber'
  if (text.includes('effective') || text.includes('container') || text.includes('moves')) return 'green'
  if (text.includes('task') || text.includes('shift')) return 'blue'
  return 'slate'
}

export default function SummaryCards({ title, items }: SummaryCardsProps) {
  return (
    <>
      <h2 className="cards-title">{title}</h2>
      <div className="card-grid">
        {items.map((item) => (
          <div className={`card card-tone-${item.tone ?? toneFor(item.label)}`} key={item.label}>
            <div className="card-value">{item.value}</div>
            <div className="card-label">{item.label}</div>
          </div>
        ))}
      </div>
    </>
  )
}