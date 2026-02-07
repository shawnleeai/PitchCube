"use client";

import { motion } from "framer-motion";
import { Book, Code, Shield, Zap, ArrowRight, ExternalLink } from "lucide-react";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const docSections = [
  {
    icon: Book,
    title: "使用指南",
    description: "快速上手 PitchCube，学习如何生成专业路演物料",
    links: [
      { label: "快速开始", href: "/docs/guide/quickstart" },
      { label: "海报生成", href: "/docs/guide/posters" },
      { label: "视频脚本", href: "/docs/guide/videos" },
      { label: "最佳实践", href: "/docs/guide/best-practices" },
    ],
  },
  {
    icon: Code,
    title: "API 文档",
    description: "完整的 RESTful API 参考，包含示例代码",
    links: [
      { label: "认证", href: "/docs/api/auth" },
      { label: "产品管理", href: "/docs/api/products" },
      { label: "海报生成", href: "/docs/api/posters" },
      { label: "视频生成", href: "/docs/api/videos" },
    ],
  },
  {
    icon: Shield,
    title: "安全指南",
    description: "API 密钥管理、数据隐私保护和安全最佳实践",
    links: [
      { label: "API 密钥安全", href: "/docs/security/api-keys" },
      { label: "数据隐私", href: "/docs/security/privacy" },
      { label: "部署安全", href: "/docs/security/deployment" },
    ],
  },
  {
    icon: Zap,
    title: "部署指南",
    description: "使用 Docker 或 Kubernetes 部署 PitchCube",
    links: [
      { label: "Docker 部署", href: "/docs/deployment/docker" },
      { label: "生产环境", href: "/docs/deployment/production" },
      { label: "环境配置", href: "/docs/deployment/configuration" },
    ],
  },
];

const quickLinks = [
  { label: "GitHub 仓库", href: "https://github.com/yourusername/pitchcube", external: true },
  { label: "更新日志", href: "/changelog", external: false },
  { label: "常见问题", href: "/faq", external: false },
  { label: "反馈建议", href: "https://github.com/yourusername/pitchcube/issues", external: true },
];

export default function DocsPage() {
  return (
    <main className="min-h-screen bg-[#0a0a0f] text-white">
      <Navbar />
      
      <div className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-16"
          >
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="gradient-text">文档中心</span>
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              全面的使用指南、API 参考和部署文档
            </p>
          </motion.div>

          {/* Search */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="max-w-2xl mx-auto mb-16"
          >
            <div className="relative">
              <input
                type="text"
                placeholder="搜索文档..."
                className="w-full px-6 py-4 rounded-xl bg-white/[0.03] border border-white/[0.08] focus:border-blue-500/50 focus:bg-white/[0.05] outline-none transition-all"
              />
              <div className="absolute right-4 top-1/2 -translate-y-1/2 px-2 py-1 rounded bg-white/10 text-xs text-gray-400">
                Ctrl K
              </div>
            </div>
          </motion.div>

          {/* Doc Sections */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16"
          >
            {docSections.map((section, index) => (
              <div
                key={section.title}
                className="p-6 rounded-2xl bg-white/[0.03] border border-white/[0.08] hover:border-white/[0.15] transition-colors"
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center flex-shrink-0">
                    <section.icon className="w-6 h-6 text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-xl font-semibold mb-2">{section.title}</h2>
                    <p className="text-gray-400 text-sm mb-4">{section.description}</p>
                    <ul className="space-y-2">
                      {section.links.map((link) => (
                        <li key={link.label}>
                          <Link
                            href={link.href}
                            className="text-sm text-gray-400 hover:text-blue-400 transition-colors flex items-center gap-1 group"
                          >
                            {link.label}
                            <ArrowRight className="w-3 h-3 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </motion.div>

          {/* Quick Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="p-8 rounded-2xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-white/[0.08]"
          >
            <h2 className="text-xl font-semibold mb-6">快速链接</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {quickLinks.map((link) => (
                <Link
                  key={link.label}
                  href={link.href}
                  target={link.external ? "_blank" : undefined}
                  rel={link.external ? "noopener noreferrer" : undefined}
                  className="flex items-center justify-between p-4 rounded-xl bg-white/5 hover:bg-white/[0.07] transition-colors group"
                >
                  <span className="text-sm">{link.label}</span>
                  {link.external && <ExternalLink className="w-4 h-4 text-gray-500 group-hover:text-gray-300" />}
                </Link>
              ))}
            </div>
          </motion.div>

          {/* Help */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mt-16 text-center"
          >
            <p className="text-gray-400">
              没有找到你需要的信息？
              <Link href="/contact" className="ml-1 text-blue-400 hover:text-blue-300">联系我们</Link>
              或
              <Link href="https://github.com/yourusername/pitchcube/discussions" className="ml-1 text-blue-400 hover:text-blue-300">参与社区讨论</Link>
            </p>
          </motion.div>
        </div>
      </div>

      <Footer />
    </main>
  );
}
