import { useEffect, useState } from "react";
import { useReducedMotion } from "./useReducedMotion";

export function useCountUp(target: number, duration = 900) {
  const [value, setValue] = useState(0);
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    if (reduceMotion) {
      setValue(target);
      return;
    }

    let frame = 0;
    const totalFrames = Math.max(1, Math.round(duration / 16));
    const timer = window.setInterval(() => {
      frame += 1;
      const progress = Math.min(frame / totalFrames, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(target * eased);
      if (progress === 1) {
        window.clearInterval(timer);
      }
    }, 16);

    return () => window.clearInterval(timer);
  }, [duration, reduceMotion, target]);

  return value;
}
