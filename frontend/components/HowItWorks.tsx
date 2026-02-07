"use client";

import { motion } from "framer-motion";
import { Upload, Cpu, Download } from "lucide-react";

const steps = [
  {
    icon: Upload,
    number: "01",
    title: "输入产品资料",
    description: "提供产品名称、描述、核心功能和目标受众等基本信息。支持批量上传和智能解析。",
  },
  {
    icon: Cpu,
    number: "02",
    title: "AI 分析处理",
    description: "AI 深度解析产品特征，自动匹配合适的设计模板和生成策略，智能优化展示效果。",
  },
  {
    icon: Download,
    number: "03",
    title: "生成展示物料",
    description: "一键生成完整路演套件，包括海报、视频脚本、PPT等。支持实时预览和自定义编辑。",
  },
];

export default function HowItWorks() {
  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 relative">
      <div className="absolute inset-0 grid-pattern opacity-20" />
      
      <div className="max-w-7xl mx-auto relative">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            三步生成
            <span className="gradient-text"> 专业展示</span>
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            极简操作，10分钟完成传统数小时工作
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.2 }}
              className="relative"
            >
              {/* Connector Line */}
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-16 left-[60%] w-[80%] h-[2px]">
                  <div className="w-full h-full bg-gradient-to-r from-blue-500/50 to-transparent" />
                </div>
              )}

              <div className="text-center">
                {/* Number Badge */}
                <div className="relative inline-block mb-8">
                  <div className="w-32 h-32 rounded-full bg-gradient-to-br from-blue-500/10 to-purple-500/10 flex items-center justify-center border border-white/10">
                    <step.icon className="w-12 h-12 text-blue-400" />
                  </div>
                  <span className="absolute -top-2 -right-2 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm font-bold">
                    {step.number}
                  </span>
                </div>

                <h3 className="text-2xl font-bold mb-4">{step.title}</h3>
                <p className="text-gray-400 leading-relaxed">{step.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
