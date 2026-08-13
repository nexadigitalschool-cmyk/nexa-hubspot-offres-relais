import type { ReactNode } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { sectionReveal, sectionRevealReduced, VIEWPORT_ONCE } from '../../lib/motion';

interface Props {
  children: ReactNode;
  className?: string;
  as?: 'div' | 'section';
  id?: string;
}

// Scroll reveal generique : translation 24px + fade, once, seuil 15%.
// Se reduit a un fade simple si prefers-reduced-motion.
export default function SectionReveal({ children, className, id }: Props) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      id={id}
      className={className}
      variants={reduce ? sectionRevealReduced : sectionReveal}
      initial="hidden"
      whileInView="visible"
      viewport={VIEWPORT_ONCE}
    >
      {children}
    </motion.div>
  );
}
