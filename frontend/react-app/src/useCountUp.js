import { useEffect, useRef, useState } from "react";

/**
 * Animate a number from its previous value to a new target over `duration` ms.
 */
export default function useCountUp(target, duration = 700) {
  const [value, setValue] = useState(target ?? 0);
  const frame = useRef(null);
  const startValue = useRef(0);
  const startTime = useRef(0);

  useEffect(() => {
    if (target === null || target === undefined) return;

    const prefersReducedMotion =
      typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

    if (prefersReducedMotion) {
      setValue(target);
      return;
    }

    startValue.current = value;
    startTime.current = performance.now();
    cancelAnimationFrame(frame.current);

    const tick = (now) => {
      const elapsed = now - startTime.current;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const next = startValue.current + (target - startValue.current) * eased;
      setValue(next);
      if (progress < 1) {
        frame.current = requestAnimationFrame(tick);
      }
    };

    frame.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target, duration]);

  return value;
}
