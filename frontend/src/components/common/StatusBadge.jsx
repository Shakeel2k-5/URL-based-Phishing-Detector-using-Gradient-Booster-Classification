export default function StatusBadge({ safe }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold ${
        safe
          ? 'bg-emerald-100 text-emerald-700'
          : 'bg-red-100 text-red-700'
      }`}
    >
      <span className={`w-2 h-2 rounded-full ${safe ? 'bg-emerald-500' : 'bg-red-500'}`} />
      {safe ? 'Safe' : 'Not Safe'}
    </span>
  );
}
