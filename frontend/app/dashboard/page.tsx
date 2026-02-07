"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { 
  LayoutDashboard, 
  Image as ImageIcon, 
  Video, 
  Mic,
  Settings,
  Plus,
  Clock,
  Download,
  MoreVertical,
  Trash2,
  Edit,
  Sparkles
} from "lucide-react";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const stats = [
  { label: "总项目", value: 12, icon: LayoutDashboard, color: "blue" },
  { label: "海报生成", value: 28, icon: ImageIcon, color: "purple" },
  { label: "视频生成", value: 8, icon: Video, color: "pink" },
];

const recentGenerations = [
  {
    id: 1,
    type: "poster",
    productName: "AI智能客服",
    template: "科技现代",
    createdAt: "2024-01-15 14:30",
    status: "completed",
    preview: null,
  },
  {
    id: 2,
    type: "video",
    productName: "数据可视化平台",
    template: "产品演示",
    createdAt: "2024-01-14 10:15",
    status: "completed",
    preview: null,
  },
  {
    id: 3,
    type: "poster",
    productName: "区块链钱包",
    template: "极简主义",
    createdAt: "2024-01-13 16:45",
    status: "completed",
    preview: null,
  },
];

const projects = [
  {
    id: 1,
    name: "AI智能客服系统",
    description: "基于大语言模型的智能客服解决方案",
    createdAt: "2024-01-10",
    generations: 5,
  },
  {
    id: 2,
    name: "数据分析平台",
    description: "企业级数据可视化与分析工具",
    createdAt: "2024-01-08",
    generations: 3,
  },
];

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <main className="min-h-screen bg-[#0a0a0f] text-white">
      <Navbar />
      
      <div className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h1 className="text-3xl font-bold mb-2">我的项目</h1>
            <p className="text-gray-400">管理你的产品项目和生成的展示物料</p>
          </motion.div>

          {/* Stats */}
          {/* 演示提示 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="mb-6 p-4 rounded-xl bg-blue-500/10 border border-blue-500/20"
          >
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
              <p className="text-sm text-blue-300">
                🎉 欢迎体验 PitchCube！点击"快速操作"开始生成你的第一张海报
              </p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
          >
            {stats.map((stat, index) => (
              <div
                key={stat.label}
                className="p-6 rounded-2xl bg-white/[0.03] border border-white/[0.08]"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">{stat.label}</p>
                    <p className="text-3xl font-bold mt-1">{stat.value}</p>
                  </div>
                  <div className={`w-12 h-12 rounded-xl bg-${stat.color}-500/20 flex items-center justify-center`}>
                    <stat.icon className={`w-6 h-6 text-${stat.color}-400`} />
                  </div>
                </div>
              </div>
            ))}
          </motion.div>

          {/* Tabs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="flex items-center gap-4 mb-6 border-b border-white/10"
          >
            {[
              { id: "overview", label: "概览" },
              { id: "projects", label: "项目" },
              { id: "generations", label: "生成记录" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`pb-4 px-2 text-sm font-medium transition-colors relative ${
                  activeTab === tab.id
                    ? "text-white"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                {tab.label}
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-600"
                  />
                )}
              </button>
            ))}
          </motion.div>

          {/* Content */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {activeTab === "overview" && (
              <div className="space-y-8">
                {/* Quick Actions */}
                <div>
                  <h2 className="text-lg font-semibold mb-4">快速操作</h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <Link
                      href="/generate"
                      className="group p-6 rounded-xl bg-gradient-to-br from-blue-500/30 via-purple-500/30 to-pink-500/30 border border-blue-500/30 hover:border-blue-500/50 transition-all hover:scale-[1.02]"
                    >
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                          <Sparkles className="w-5 h-5 text-white" />
                        </div>
                        <span className="px-2 py-0.5 text-xs bg-green-500/20 text-green-400 rounded-full">已可用</span>
                      </div>
                      <p className="font-bold text-lg mb-1">生成海报</p>
                      <p className="text-sm text-gray-400">10秒生成专业路演海报</p>
                    </Link>
                    
                    <Link
                      href="/generate"
                      className="group block p-6 rounded-xl bg-gradient-to-br from-emerald-500/30 via-teal-500/30 to-cyan-500/30 border border-emerald-500/30 hover:border-emerald-500/50 transition-all hover:scale-[1.02]"
                    >
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                          <Mic className="w-5 h-5 text-white" />
                        </div>
                        <span className="px-2 py-0.5 text-xs bg-green-500/20 text-green-400 rounded-full">已可用</span>
                      </div>
                      <p className="font-bold text-lg mb-1">生成语音</p>
                      <p className="text-sm text-gray-400">AI语音解说与旁白</p>
                    </Link>
                  </div>
                </div>

                {/* Recent Generations */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold">最近生成</h2>
                    <button
                      onClick={() => setActiveTab("generations")}
                      className="text-sm text-blue-400 hover:text-blue-300"
                    >
                      查看全部
                    </button>
                  </div>
                  <div className="space-y-3">
                    {recentGenerations.map((gen) => (
                      <div
                        key={gen.id}
                        className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.08] flex items-center justify-between"
                      >
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-lg bg-white/5 flex items-center justify-center">
                            {gen.type === "poster" ? (
                              <ImageIcon className="w-6 h-6 text-blue-400" />
                            ) : (
                              <Video className="w-6 h-6 text-purple-400" />
                            )}
                          </div>
                          <div>
                            <p className="font-medium">{gen.productName}</p>
                            <p className="text-sm text-gray-400">
                              {gen.template} · {gen.createdAt}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <button className="p-2 rounded-lg hover:bg-white/5 transition-colors">
                            <Download className="w-4 h-4" />
                          </button>
                          <button className="p-2 rounded-lg hover:bg-white/5 transition-colors">
                            <MoreVertical className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === "projects" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {projects.map((project) => (
                  <div
                    key={project.id}
                    className="p-6 rounded-xl bg-white/[0.03] border border-white/[0.08] hover:border-white/[0.15] transition-colors"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                        <LayoutDashboard className="w-5 h-5" />
                      </div>
                      <div className="flex items-center gap-1">
                        <button className="p-2 rounded-lg hover:bg-white/5">
                          <Edit className="w-4 h-4" />
                        </button>
                        <button className="p-2 rounded-lg hover:bg-white/5 text-red-400">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <h3 className="font-semibold mb-1">{project.name}</h3>
                    <p className="text-sm text-gray-400 mb-4">{project.description}</p>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>{project.generations} 次生成</span>
                      <span>创建于 {project.createdAt}</span>
                    </div>
                  </div>
                ))}
                
                <button className="p-6 rounded-xl border border-dashed border-white/20 hover:border-white/30 hover:bg-white/[0.02] transition-colors flex flex-col items-center justify-center text-gray-400">
                  <Plus className="w-8 h-8 mb-2" />
                  <span>新建项目</span>
                </button>
              </div>
            )}

            {activeTab === "generations" && (
              <div className="space-y-3">
                {recentGenerations.map((gen) => (
                  <div
                    key={gen.id}
                    className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.08] flex items-center justify-between"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-lg bg-white/5 flex items-center justify-center">
                        {gen.type === "poster" ? (
                          <ImageIcon className="w-6 h-6 text-blue-400" />
                        ) : (
                          <Video className="w-6 h-6 text-purple-400" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium">{gen.productName}</p>
                        <div className="flex items-center gap-3 text-sm text-gray-400">
                          <span>{gen.template}</span>
                          <span>·</span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {gen.createdAt}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-3 py-1 rounded-full text-xs bg-green-500/20 text-green-400">
                        已完成
                      </span>
                      <button className="p-2 rounded-lg hover:bg-white/5">
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        </div>
      </div>

      <Footer />
    </main>
  );
}
