import { useEffect, useRef, useState } from 'react'
import { Search } from 'lucide-react'

export interface SearchBarProps {
  placeholder?: string
  value?: string
  onChange?: (value: string) => void
  onSearch?: (value: string) => void
  debounce?: number
  className?: string
}

export function SearchBar({
  placeholder = 'Search…',
  value: controlledValue,
  onChange,
  onSearch,
  debounce = 300,
  className = '',
}: SearchBarProps) {
  const [internalValue, setInternalValue] = useState(controlledValue || '')
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const currentValue = controlledValue !== undefined ? controlledValue : internalValue

  useEffect(() => {
    if (controlledValue !== undefined) {
      setInternalValue(controlledValue)
    }
  }, [controlledValue])

  const handleInputChange = (text: string) => {
    setInternalValue(text)
    if (onChange) onChange(text)

    if (onSearch) {
      if (timer.current) clearTimeout(timer.current)
      timer.current = setTimeout(() => {
        onSearch(text)
      }, debounce)
    }
  }

  return (
    <div className={['relative', className].join(' ')}>
      <Search
        size={15}
        className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none"
      />
      <input
        type="text"
        value={currentValue}
        onChange={(e) => handleInputChange(e.target.value)}
        placeholder={placeholder}
        className="w-full pl-9 pr-4 py-2 text-sm bg-white border border-slate-200 rounded-lg text-slate-700 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/40 focus:border-sky-500 transition-all"
      />
    </div>
  )
}
