"use client";

import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  color: string;
  status: "available" | "beta" | "coming";
  index: number;
}

const statusLabels = {
  available: { text: "可用", className: "bg-green-500/20 text-green-400 border-green-500/30" },
  beta: { text: "Beta", className: "bg-amber-500/20 text-amber-400 border-amber-500/30" },
  coming: { text: "即将推出", className: "bg-gray-500/20 text-gray-400 border-gray-500/30" },
};

export default function FeatureCard({
  icon: Icon,
  title,
  description,
  color,
  status,
  index,
}: FeatureCardProps) {
  const statusConfig = statusLabels[status];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ y: -8 }}
      className="group relative"
    >
      <div className="relative h-full p-6 rounded-2xl bg-white/[0.03] border border-white/[0.08] overflow-hidden transition-all duration-300 hover:border-white/[0.15] hover:bg-white/[0.05]">
        {/* Gradient Border Effect */}
        <div
          className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${color} opacity-0 group-hover:opacity-10 transition-opacity duration-500`}
        />
        
        {/* Icon */}
        <div
          className={`relative w-14 h-14 rounded-xl bg-gradient-to-br ${color} p-[1px] mb-5`}
        >
          <div className="w-full h-full rounded-xl bg-[#0a0a0f] flex items-center justify-center">
            <Icon className="w-6 h-6 text-white" />
          </div>
        </div>

        {/* Status Badge */}
        <span
          className={`absolute top-4 right-4 px-2 py-1 text-xs font-medium rounded-full border ${statusConfig.className}`}
        >
          {statusConfig.text}
        </span>

        {/* Content */}
        <h3 className="text-xl font-bold mb-3 text-white group-hover:text-blue-400 transition-colors">
          {title}
        </h3>
        <p className="text-gray-400 text-sm leading-relaxed">{description}</p>

        {/* Hover Arrow */}
        <div className="mt-4 flex items-center gap-2 text-sm text-gray-500 group-hover:text-blue-400 transition-colors">
          <span>了解更多</span>
          <motion.span
            initial={{ x: 0 }}
            whileHover={{ x: 4 }}
            className="inline-block"
          >
            →
          </motion.span>
        </div>
      </div>
    </motion.div>
  );
}
