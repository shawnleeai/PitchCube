"use client";

import { motion } from "framer-motion";
import { 
  Sparkles, 
  Palette, 
  Video, 
  Box, 
  Mic, 
  Users, 
  BarChart3,
  ArrowRight,
  Zap,
  Shield,
  Clock,
  Github,
  Twitter,
  Linkedin
} from "lucide-react";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import FeatureCard from "@/components/FeatureCard";
import HowItWorks from "@/components/HowItWorks";
import CTASection from "@/components/CTASection";
import Footer from "@/components/Footer";

type FeatureStatus = "available" | "beta" | "coming";

interface Feature {
  icon: any;
  title: string;
  description: string;
  color: string;
  status: FeatureStatus;
}

const features: Feature[] = [
  {
    icon: Palette,
    title: "海报工坊",
    description: "AI智能海报设计，10秒生成专业级宣传海报。支持多平台尺寸、品牌定制、批量导出。",
    color: "from-blue-500 to-cyan-500",
    status: "available",
  },
  {
    icon: Video,
    title: "视频演播室",
    description: "自动生成路演视频脚本与演示视频。1-3分钟专业视频，多平台格式适配。",
    color: "from-purple-500 to-pink-500",
    status: "available",
  },
  {
    icon: Box,
    title: "IP铸造厂",
    description: "基于产品特征生成3D打印IP形象。输出STL/OBJ格式，支持在线打印服务。",
    color: "from-amber-500 to-orange-500",
    status: "beta",
  },
  {
    icon: Mic,
    title: "语音解说员",
    description: "智能语音讲解生成与实时问答。多语言支持，多种讲解风格可选。",
    color: "from-emerald-500 to-teal-500",
    status: "beta",
  },
  {
    icon: Users,
    title: "协作空间",
    description: "多人实时协作编辑路演内容。版本管理、评论批注、权限控制一应俱全。",
    color: "from-rose-500 to-red-500",
    status: "coming",
  },
  {
    icon: BarChart3,
    title: "数据魔镜",
    description: "A/B测试数据分析与优化建议。数据驱动提升路演效果与转化率。",
    color: "from-indigo-500 to-violet-500",
    status: "coming",
  },
];

const benefits = [
  {
    icon: Zap,
    title: "效率提升 90%",
    description: "从8小时缩短至30分钟完成路演物料准备",
  },
  {
    icon: Shield,
    title: "专业品质保证",
    description: "AI生成效果媲美专业设计团队水准",
  },
  {
    icon: Clock,
    title: "24/7 随时可用",
    description: "无需等待，随时生成所需展示物料",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-[#0a0a0f] text-white overflow-x-hidden">
      <Navbar />
      
      {/* Hero Section */}
      <HeroSection />

      {/* Features Grid */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 relative">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm text-blue-400 mb-6">
              <Sparkles className="w-4 h-4" />
              六大核心模块
            </span>
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              像搭积木一样
              <span className="gradient-text"> 构建路演展示</span>
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              模块化设计，按需组合。从海报到视频，从IP形象到语音讲解，全方位覆盖路演展示需求。
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <FeatureCard key={feature.title} {...feature} index={index} />
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 relative">
        <div className="absolute inset-0 animated-bg opacity-50" />
        <div className="max-w-7xl mx-auto relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              为什么选择
              <span className="gradient-text"> PitchCube</span>
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              专为路演场景优化，理解时间压力与展示效果的双重需求
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {benefits.map((benefit, index) => (
              <motion.div
                key={benefit.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="text-center p-8"
              >
                <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
                  <benefit.icon className="w-8 h-8 text-blue-400" />
                </div>
                <h3 className="text-2xl font-bold mb-3">{benefit.title}</h3>
                <p className="text-gray-400">{benefit.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <HowItWorks />

      {/* CTA Section */}
      <CTASection />

      {/* Footer */}
      <Footer />
    </main>
  );
}
