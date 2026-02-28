import { useTranslation } from 'react-i18next';

export type Metric = 'weight' | 'prints' | 'time';

const METRICS: Metric[] = ['weight', 'prints', 'time'];

interface MetricToggleProps {
  value: Metric;
  onChange: (metric: Metric) => void;
}

export function MetricToggle({ value, onChange }: MetricToggleProps) {
  const { t } = useTranslation();

  const labels: Record<Metric, string> = {
    weight: t('stats.filamentByWeight'),
    prints: t('stats.filamentByPrints'),
    time: t('stats.filamentByTime'),
  };

  return (
    <div className="flex gap-0.5 bg-bambu-dark rounded-lg p-0.5">
      {METRICS.map(m => (
        <button
          key={m}
          onClick={() => onChange(m)}
          className={`px-2 py-0.5 text-xs rounded-md transition-colors ${
            value === m ? 'bg-bambu-green text-white' : 'text-bambu-gray hover:text-white'
          }`}
        >
          {labels[m]}
        </button>
      ))}
    </div>
  );
}
