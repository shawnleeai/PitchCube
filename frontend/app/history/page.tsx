"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  History,
  FileText,
  Video,
  Mic,
  Box,
  Download,
  Trash2,
  Eye,
  Calendar,
  Clock,
  Search,
  MoreVertical
} from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

interface HistoryItem {
  id: string;
  type: 'poster' | 'video' | 'voice' | 'ip';
  name: string;
  status: 'completed' | 'processing' | 'failed';
  created_at: string;
  thumbnail?: string;
}

const mockHistory: HistoryItem[] = [
  { id: '1', type: 'poster', name: '产品宣传海报 v2', status: 'completed', created_at: '2024-01-15 14:30' },
  { id: '2', type: 'video', name: '产品介绍视频脚本', status: 'completed', created_at: '2024-01-15 12:20' },
  { id: '3', type: 'voice', name: '宣传语音 - 专业版', status: 'completed', created_at: '2024-01-15 10:15' },
  { id: '4', type: 'ip', name: 'IP形象设计 - 蓝色版本', status: 'processing', created_at: '2024-01-15 09:00' },
  { id: '5', type: 'poster', name: '海报设计 - 极简风格', status: 'completed', created_at: '2024-01-14 18:45' },
  { id: '6', type: 'video', name: '产品演示视频', status: 'failed', created_at: '2024-01-14 16:30' },
  { id: '7', type: 'poster', name: '活动海报 - 促销版', status: 'completed', created_at: '2024-01-14 14:20' },
  { id: '8', type: 'voice', name: '语音播报 - 正式版', status: 'completed', created_at: '2024-01-14 11:10' },
];

const typeConfig: Record<string, { icon: any; bgClass: string; textClass: string; label: string }> = {
  poster: { icon: FileText, bgClass: "bg-blue-500/10", textClass: "text-blue-400", label: "海报" },
  video: { icon: Video, bgClass: "bg-purple-500/10", textClass: "text-purple-400", label: "视频" },
  voice: { icon: Mic, bgClass: "bg-green-500/10", textClass: "text-green-400", label: "语音" },
  ip: { icon: Box, bgClass: "bg-amber-500/10", textClass: "text-amber-400", label: "IP" }
};

const statusConfig: Record<string, { bgClass: string; textClass: string; dotClass: string; label: string }> = {
  completed: { bgClass: "bg-green-500/10", textClass: "text-green-400", dotClass: "bg-green-400", label: "已完成" },
  processing: { bgClass: "bg-blue-500/10", textClass: "text-blue-400", dotClass: "bg-blue-400", label: "处理中" },
  failed: { bgClass: "bg-red-500/10", textClass: "text-red-400", dotClass: "bg-red-400", label: "失败" }
};

export default function HistoryPage() {
  const [filter, setFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedItems, setSelectedItems] = useState<string[]>([]);

  const filteredHistory = mockHistory.filter(item => {
    const matchesFilter = filter === 'all' || item.type === filter;
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const toggleSelect = (id: string) => {
    setSelectedItems(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const toggleSelectAll = () => {
    if (selectedItems.length === filteredHistory.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(filteredHistory.map(i => i.id));
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <Navbar />

      <div className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h1 className="text-3xl font-bold text-white mb-2">
              <History className="inline-block w-8 h-8 mr-2 text-blue-500" />
              生成历史
            </h1>
            <p className="text-gray-400">查看和管理您所有的生成记录</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-[#12121a] rounded-2xl border border-white/10 p-4 mb-6"
          >
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="搜索生成记录..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div className="flex gap-2">
                {[
                  { id: 'all', label: '全部', bgClass: 'bg-blue-500', default: true },
                  { id: 'poster', label: '海报', bgClass: 'bg-blue-500' },
                  { id: 'video', label: '视频', bgClass: 'bg-purple-500' },
                  { id: 'voice', label: '语音', bgClass: 'bg-green-500' },
                  { id: 'ip', label: 'IP', bgClass: 'bg-amber-500' }
                ].map((btn) => (
                  <button
                    key={btn.id}
                    onClick={() => setFilter(btn.id)}
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      filter === btn.id
                        ? `${btn.bgClass} text-white`
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                  >
                    {btn.label}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>

          {selectedItems.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4 mb-6 flex items-center justify-between"
            >
              <span className="text-blue-400">已选择 {selectedItems.length} 项</span>
              <div className="flex gap-2">
                <button className="px-4 py-2 bg-blue-500/20 text-blue-400 rounded-lg hover:bg-blue-500/30 transition-colors">
                  批量下载
                </button>
                <button className="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors">
                  删除选中
                </button>
              </div>
            </motion.div>
          )}

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-[#12121a] rounded-2xl border border-white/10 overflow-hidden"
          >
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="w-12 p-4">
                      <input
                        type="checkbox"
                        checked={selectedItems.length === filteredHistory.length && filteredHistory.length > 0}
                        onChange={toggleSelectAll}
                        className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500"
                      />
                    </th>
                    <th className="p-4 text-left text-sm font-medium text-gray-400">类型</th>
                    <th className="p-4 text-left text-sm font-medium text-gray-400">名称</th>
                    <th className="p-4 text-left text-sm font-medium text-gray-400">状态</th>
                    <th className="p-4 text-left text-sm font-medium text-gray-400">创建时间</th>
                    <th className="p-4 text-right text-sm font-medium text-gray-400">操作</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredHistory.map((item, index) => {
                    const typeConf = typeConfig[item.type] || typeConfig.poster;
                    const statusConf = statusConfig[item.status] || statusConfig.completed;
                    const Icon = typeConf.icon;
                    
                    return (
                      <motion.tr
                        key={item.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className={`border-b border-white/5 hover:bg-white/5 transition-colors ${
                          selectedItems.includes(item.id) ? 'bg-blue-500/5' : ''
                        }`}
                      >
                        <td className="p-4">
                          <input
                            type="checkbox"
                            checked={selectedItems.includes(item.id)}
                            onChange={() => toggleSelect(item.id)}
                            className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500"
                          />
                        </td>
                        <td className="p-4">
                          <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full ${typeConf.bgClass} ${typeConf.textClass}`}>
                            <Icon className="w-4 h-4" />
                            <span className="text-sm">{typeConf.label}</span>
                          </div>
                        </td>
                        <td className="p-4">
                          <span className="text-white">{item.name}</span>
                        </td>
                        <td className="p-4">
                          <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${statusConf.bgClass} ${statusConf.textClass}`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${statusConf.dotClass} ${item.status === 'processing' ? 'animate-pulse' : ''}`} />
                            {statusConf.label}
                          </span>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2 text-gray-400">
                            <Calendar className="w-4 h-4" />
                            <span className="text-sm">{item.created_at}</span>
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center justify-end gap-2">
                            <button className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
                              <Eye className="w-4 h-4" />
                            </button>
                            {item.status === 'completed' && (
                              <button className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
                                <Download className="w-4 h-4" />
                              </button>
                            )}
                            <button className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
                              <MoreVertical className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </motion.tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {filteredHistory.length === 0 && (
              <div className="p-12 text-center">
                <History className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <div className="text-gray-400">没有找到相关记录</div>
              </div>
            )}
          </motion.div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
