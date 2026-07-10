export default function Skyline() {
  return (
    <svg
      viewBox="0 0 480 200"
      className="w-full h-auto"
      preserveAspectRatio="xMidYMax slice"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#C1592B" stopOpacity="0.9" />
          <stop offset="55%" stopColor="#9c4520" stopOpacity="0.55" />
          <stop offset="100%" stopColor="#26211D" stopOpacity="0" />
        </linearGradient>
      </defs>
      <circle cx="240" cy="70" r="46" fill="url(#dusk)" />
      {/* Phare des Mamelles */}
      <rect x="40" y="120" width="8" height="60" fill="#26211D" />
      <rect x="34" y="112" width="20" height="10" fill="#26211D" />
      {/* Monument de la Renaissance africaine, stylized */}
      <path d="M120 180 L128 100 L140 108 L148 180 Z" fill="#26211D" />
      <path d="M148 180 L156 96 L166 106 L172 180 Z" fill="#26211D" />
      {/* Mosquée / arches, Plateau skyline */}
      <path
        d="M200 180 L200 130 Q212 108 224 130 L224 180 Z"
        fill="#26211D"
      />
      <rect x="230" y="150" width="14" height="30" fill="#26211D" />
      <rect x="252" y="140" width="10" height="40" fill="#26211D" />
      <path
        d="M270 180 L270 125 Q284 100 298 125 L298 180 Z"
        fill="#26211D"
      />
      {/* immeubles */}
      <rect x="310" y="150" width="18" height="30" fill="#26211D" />
      <rect x="332" y="135" width="16" height="45" fill="#26211D" />
      <rect x="352" y="155" width="14" height="25" fill="#26211D" />
      <rect x="370" y="140" width="20" height="40" fill="#26211D" />
      {/* baobab silhouette */}
      <path
        d="M415 180 L417 145 Q408 138 404 126 Q412 132 417 132 Q414 118 420 108 Q422 122 428 128 Q432 118 440 116 Q436 126 430 132 Q436 132 442 126 Q438 138 428 144 L430 180 Z"
        fill="#26211D"
      />
      <line x1="0" y1="180" x2="480" y2="180" stroke="#26211D" strokeWidth="2" />
    </svg>
  );
}
