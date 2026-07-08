export default function EmptyState({ icon: Icon, title, description, action, className = '' }) {
  return (
    <div className={`flex flex-col items-center justify-center px-6 py-14 text-center ${className}`}>
      {Icon && (
        <span className="mb-3 grid h-12 w-12 place-items-center rounded-full bg-surface-2 text-muted">
          <Icon size={22} />
        </span>
      )}
      <h3 className="text-sm font-semibold text-content">{title}</h3>
      {description && <p className="mt-1 max-w-sm text-sm text-muted">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
