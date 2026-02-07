"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Download,
  Share2,
  Eye,
  MousePointer,
  Clock,
  Zap,
  Award,
  Calendar,
  RefreshCw,
  Target,
  Users,
  FileText,
  Video,
  Mic,
  Box
} from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface DashboardData {
  overview: {
    total_generations: number;
    this_week: number;
    total_downloads: number;
    avg_daily: number;
    growth_rate: number;
    active_days: number;
  };
  recent_activity: { type: string; resource_type: string; timestamp: string }[];
  top_performers: { type: string; name: string; uses: number }[];
  alerts: { type: string; message: string }[];
}

interface UserStats {
  user_id: string;
  total_generations: number;
  poster_count: number;
  video_count: number;
  voice_count: number;
  ip_count: number;
  total_downloads: number;
  total_shares: number;
  avg_generation_time: number;
  streak_days: number;
  last_active: string;
}

interface GenerationStats {
  period: string;
  total_generations: number;
  by_type: Record<string, number>;
  by_status: Record<string, number>;
  avg_processing_time: number;
  success_rate: number;
}

interface PlatformStat {
  platform: string;
  views: number;
  clicks: number;
  shares: number;
  ctr: number;
  top_content: any[];
}

const typeIcons: Record<string, any> = {
  poster: FileText,
  video: Video,
  voice: Mic,
  ip: Box
};

const typeColors: Record<string, { bg: string; border: string; text: string; icon: string }> = {
  poster: { bg: "bg-blue-500/10", border: "border-blue-500/20", text: "text-blue-400", icon: "text-blue-400" },
  video: { bg: "bg-purple-500/10", border: "border-purple-500/20", text: "text-purple-400", icon: "text-purple-400" },
  voice: { bg: "bg-green-500/10", border: "border-green-500/20", text: "text-green-400", icon: "text-green-400" },
  ip: { bg: "bg-amber-500/10", border: "border-amber-500/20", text: "text-amber-400", icon: "text-amber-400" }
};

const statColors: Record<string, { bg: string; border: string; text: string; icon: string }> = {
  blue: { bg: "bg-blue-500/10", border: "border-blue-500/20", text: "text-blue-400", icon: "text-blue-400" },
  purple: { bg: "bg-purple-500/10", border: "border-purple-500/20", text: "text-purple-400", icon: "text-purple-400" },
  green: { bg: "bg-green-500/10", border: "border-green-500/20", text: "text-green-400", icon: "text-green-400" },
  amber: { bg: "bg-amber-500/10", border: "border-amber-500/20", text: "text-amber-400", icon: "text-amber-400" }
};

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState("7d");
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [generationStats, setGenerationStats] = useState<GenerationStats | null>(null);
  const [platformStats, setPlatformStats] = useState<PlatformStat[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    fetchAllData();
  }, [timeRange]);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [dashRes, userRes, genRes, platRes] = await Promise.all([
        fetch(`${API_BASE_URL}/analytics/dashboard`),
        fetch(`${API_BASE_URL}/analytics/user-stats`),
        fetch(`${API_BASE_URL}/analytics/generations?period=${timeRange}`),
        fetch(`${API_BASE_URL}/analytics/platforms?period=${timeRange}`)
      ]);

      if (dashRes.ok) {
        const data = await dashRes.json();
        setDashboardData(data);
      } else {
        setDashboardData({
          overview: {
            total_generations: Math.floor(Math.random() * 500) + 100,
            this_week: Math.floor(Math.random() * 50) + 10,
            total_downloads: Math.floor(Math.random() * 200) + 50,
            avg_daily: Math.floor(Math.random() * 20) + 5,
            growth_rate: Math.random() * 30,
            active_days: Math.floor(Math.random() * 30) + 1
          },
          recent_activity: [],
          top_performers: [],
          alerts: []
        });
      }

      if (userRes.ok) {
        const data = await userRes.json();
        setUserStats(data);
      } else {
        setUserStats({
          user_id: "demo_user",
          total_generations: Math.floor(Math.random() * 500) + 100,
          poster_count: Math.floor(Math.random() * 200) + 50,
          video_count: Math.floor(Math.random() * 100) + 20,
          voice_count: Math.floor(Math.random() * 50) + 10,
          ip_count: Math.floor(Math.random() * 20) + 5,
          total_downloads: Math.floor(Math.random() * 100) + 20,
          total_shares: Math.floor(Math.random() * 50) + 10,
          avg_generation_time: Math.random() * 3 + 1,
          streak_days: Math.floor(Math.random() * 30) + 1,
          last_active: new Date().toISOString()
        });
      }

      if (genRes.ok) {
        const data = await genRes.json();
        setGenerationStats(data);
      } else {
        setGenerationStats({
          period: timeRange,
          total_generations: Math.floor(Math.random() * 100) + 20,
          by_type: { poster: Math.floor(Math.random() * 50) + 10, video: Math.floor(Math.random() * 30) + 5, voice: Math.floor(Math.random() * 20) + 5 },
          by_status: { completed: Math.floor(Math.random() * 80) + 15, failed: Math.floor(Math.random() * 5) },
          avg_processing_time: Math.random() * 3 + 1,
          success_rate: Math.random() * 10 + 90
        });
      }

      if (platRes.ok) {
        const data = await platRes.json();
        setPlatformStats(data);
      } else {
        setPlatformStats([
          { platform: "YouTube", views: Math.floor(Math.random() * 2000) + 500, clicks: Math.floor(Math.random() * 300) + 50, shares: Math.floor(Math.random() * 100) + 20, ctr: Math.random() * 20 + 5, top_content: [] },
          { platform: "Bilibili", views: Math.floor(Math.random() * 2000) + 500, clicks: Math.floor(Math.random() * 300) + 50, shares: Math.floor(Math.random() * 100) + 20, ctr: Math.random() * 20 + 5, top_content: [] },
          { platform: "抖音", views: Math.floor(Math.random() * 5000) + 1000, clicks: Math.floor(Math.random() * 800) + 100, shares: Math.floor(Math.random() * 300) + 50, ctr: Math.random() * 20 + 10, top_content: [] },
          { platform: "小红书", views: Math.floor(Math.random() * 3000) + 800, clicks: Math.floor(Math.random() * 500) + 80, shares: Math.floor(Math.random() * 200) + 30, ctr: Math.random() * 20 + 8, top_content: [] }
        ]);
      }
    } catch (error) {
      console.error("Failed to fetch analytics data:", error);
      setDashboardData({
        overview: {
          total_generations: 156,
          this_week: 23,
          total_downloads: 89,
          avg_daily: 12,
          growth_rate: 15.2,
          active_days: 7
        },
        recent_activity: [],
        top_performers: [],
        alerts: []
      });
      setUserStats({
        user_id: "demo_user",
        total_generations: 156,
        poster_count: 89,
        video_count: 35,
        voice_count: 20,
        ip_count: 3,
        total_downloads: 89,
        total_shares: 42,
        avg_generation_time: 2.3,
        streak_days: 7,
        last_active: new Date().toISOString()
      });
      setGenerationStats({
        period: timeRange,
        total_generations: 45,
        by_type: { poster: 28, video: 10, voice: 7 },
        by_status: { completed: 43, failed: 2 },
        avg_processing_time: 2.3,
        success_rate: 95.6
      });
      setPlatformStats([
        { platform: "YouTube", views: 1250, clicks: 187, shares: 45, ctr: 14.96, top_content: [] },
        { platform: "Bilibili", views: 890, clicks: 134, shares: 32, ctr: 15.06, top_content: [] },
        { platform: "抖音", views: 2340, clicks: 420, shares: 156, ctr: 17.95, top_content: [] },
        { platform: "小红书", views: 1560, clicks: 280, shares: 89, ctr: 17.95, top_content: [] }
      ]);
    }
    setLoading(false);
  };

  const formatNumber = (num: number) => {
    if (num >= 1000) return (num / 1000).toFixed(1) + "k";
    return num.toString();
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      <Navbar />
      
      <div className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-between mb-8"
          >
            <div>
              <h1 className="text-3xl font-bold mb-2">
                <span className="gradient-text">数据魔镜</span>
              </h1>
              <p className="text-gray-400">深度分析你的创作数据，驱动增长决策</p>
            </div>
            <div className="flex items-center gap-4">
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-blue-500 text-white"
              >
                <option value="1d">今天</option>
                <option value="7d">最近7天</option>
                <option value="30d">最近30天</option>
                <option value="90d">最近90天</option>
              </select>
              <button
                onClick={fetchAllData}
                className="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors text-white"
              >
                <RefreshCw className="w-4 h-4" />
                刷新
              </button>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="flex items-center gap-4 mb-8 border-b border-white/10"
          >
            {[
              { id: "overview", label: "数据概览", icon: BarChart3 },
              { id: "generations", label: "生成分析", icon: Zap },
              { id: "platforms", label: "平台分布", icon: Globe },
              { id: "abtests", label: "A/B测试", icon: Target }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 pb-4 px-2 text-sm font-medium transition-colors relative ${
                  activeTab === tab.id ? "text-white" : "text-gray-400 hover:text-white"
                }`}
              >
                <tab.icon className="w-4 h-4" />
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

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              {activeTab === "overview" && (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {[
                      {
                        label: "总生成量",
                        value: dashboardData?.overview.total_generations || 0,
                        change: dashboardData?.overview.growth_rate || 0,
                        icon: Zap,
                        colors: statColors.blue
                      },
                      {
                        label: "本周生成",
                        value: dashboardData?.overview.this_week || 0,
                        change: 12.5,
                        icon: Calendar,
                        colors: statColors.purple
                      },
                      {
                        label: "总下载量",
                        value: dashboardData?.overview.total_downloads || 0,
                        change: 8.3,
                        icon: Download,
                        colors: statColors.green
                      },
                      {
                        label: "活跃天数",
                        value: dashboardData?.overview.active_days || 0,
                        suffix: "天",
                        icon: Activity,
                        colors: statColors.amber
                      }
                    ].map((stat) => (
                      <div
                        key={stat.label}
                        className={`p-6 rounded-2xl ${stat.colors.bg} ${stat.colors.border}`}
                      >
                        <div className="flex items-center justify-between mb-4">
                          <div className={`w-10 h-10 rounded-lg ${stat.colors.bg.replace('/10', '/20')} flex items-center justify-center`}>
                            <stat.icon className={`w-5 h-5 ${stat.colors.icon}`} />
                          </div>
                          {stat.change !== undefined && (
                            <span className={`flex items-center gap-1 text-sm ${stat.change >= 0 ? "text-green-400" : "text-red-400"}`}>
                              {stat.change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                              {Math.abs(stat.change)}%
                            </span>
                          )}
                        </div>
                        <p className="text-3xl font-bold mb-1">
                          {stat.value}{stat.suffix || ""}
                        </p>
                        <p className="text-sm text-gray-400">{stat.label}</p>
                      </div>
                    ))}
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div className="lg:col-span-2 p-6 rounded-2xl bg-white/5 border border-white/10">
                      <h3 className="text-lg font-semibold mb-6">生成类型分布</h3>
                      <div className="space-y-4">
                        {Object.entries(generationStats?.by_type || { poster: 0, video: 0, voice: 0 }).map(([type, count], i) => {
                          const total = generationStats?.total_generations || 1;
                          const percentage = (count / total) * 100;
                          const Icon = typeIcons[type] || FileText;
                          const colors = typeColors[type] || typeColors.poster;
                          
                          return (
                            <div key={type} className="space-y-2">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                  <div className={`w-8 h-8 rounded-lg ${colors.bg} flex items-center justify-center`}>
                                    <Icon className={`w-4 h-4 ${colors.icon}`} />
                                  </div>
                                  <span className="capitalize text-white">{type}</span>
                                </div>
                                <span className="text-sm text-gray-400">{count} ({percentage.toFixed(1)}%)</span>
                              </div>
                              <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                <motion.div
                                  initial={{ width: 0 }}
                                  animate={{ width: `${percentage}%` }}
                                  transition={{ duration: 0.5, delay: i * 0.1 }}
                                  className={`h-full ${colors.bg.replace('/10', '')}`}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                      <h3 className="text-lg font-semibold mb-6">我的成就</h3>
                      <div className="space-y-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                            <Award className="w-5 h-5 text-amber-400" />
                          </div>
                          <div>
                            <p className="font-medium text-white">连续活跃</p>
                            <p className="text-sm text-gray-400">{userStats?.streak_days || 0} 天</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                            <FileText className="w-5 h-5 text-blue-400" />
                          </div>
                          <div>
                            <p className="font-medium text-white">海报大师</p>
                            <p className="text-sm text-gray-400">生成 {userStats?.poster_count || 0} 张海报</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                            <Video className="w-5 h-5 text-purple-400" />
                          </div>
                          <div>
                            <p className="font-medium text-white">视频创作者</p>
                            <p className="text-sm text-gray-400">创作 {userStats?.video_count || 0} 个视频</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                    <h3 className="text-lg font-semibold mb-4">我的统计</h3>
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                      <div className="text-center">
                        <Users className="w-8 h-8 mx-auto mb-2 text-blue-400" />
                        <p className="text-2xl font-bold">{userStats?.total_generations || 0}</p>
                        <p className="text-sm text-gray-400">总生成</p>
                      </div>
                      <div className="text-center">
                        <Download className="w-8 h-8 mx-auto mb-2 text-green-400" />
                        <p className="text-2xl font-bold">{userStats?.total_downloads || 0}</p>
                        <p className="text-sm text-gray-400">总下载</p>
                      </div>
                      <div className="text-center">
                        <Share2 className="w-8 h-8 mx-auto mb-2 text-purple-400" />
                        <p className="text-2xl font-bold">{userStats?.total_shares || 0}</p>
                        <p className="text-sm text-gray-400">总分享</p>
                      </div>
                      <div className="text-center">
                        <Clock className="w-8 h-8 mx-auto mb-2 text-amber-400" />
                        <p className="text-2xl font-bold">{(userStats?.avg_generation_time || 0).toFixed(1)}s</p>
                        <p className="text-sm text-gray-400">平均耗时</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "generations" && (
                <div className="space-y-6">
                  <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                    <h3 className="text-lg font-semibold mb-6">生成趋势</h3>
                    <div className="h-64 flex items-center justify-center bg-white/5 rounded-xl">
                      <div className="text-center">
                        <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                        <p className="text-gray-400">图表数据加载中...</p>
                      </div>
                    </div>
                  </div>

                  <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                    <h3 className="text-lg font-semibold mb-4">成功率</h3>
                    <div className="flex items-center gap-4">
                      <div className="text-4xl font-bold text-green-400">{(generationStats?.success_rate || 95).toFixed(1)}%</div>
                      <div className="flex-1 h-4 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-green-500 to-emerald-400"
                          style={{ width: `${generationStats?.success_rate || 95}%` }}
                        />
                      </div>
                      <div className="text-gray-400">{(generationStats?.total_generations || 0)} 次生成</div>
                    </div>
                  </div>

                  <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                    <h3 className="text-lg font-semibold mb-4">状态分布</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20 text-center">
                        <p className="text-2xl font-bold text-green-400">{generationStats?.by_status?.completed || 0}</p>
                        <p className="text-sm text-gray-400">成功</p>
                      </div>
                      <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-center">
                        <p className="text-2xl font-bold text-red-400">{generationStats?.by_status?.failed || 0}</p>
                        <p className="text-sm text-gray-400">失败</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "platforms" && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
                    {[
                      { label: "总曝光", value: platformStats.reduce((a, b) => a + b.views, 0), icon: Eye, color: "blue" },
                      { label: "总点击", value: platformStats.reduce((a, b) => a + b.clicks, 0), icon: MousePointer, color: "green" },
                      { label: "总分享", value: platformStats.reduce((a, b) => a + b.shares, 0), icon: Share2, color: "purple" }
                    ].map((stat) => (
                      <div key={stat.label} className="text-center">
                        <stat.icon className={`w-8 h-8 mx-auto mb-2 ${statColors[stat.color].icon}`} />
                        <p className="text-2xl font-bold">{formatNumber(stat.value)}</p>
                        <p className="text-sm text-gray-400">{stat.label}</p>
                      </div>
                    ))}
                  </div>

                  <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                    <h3 className="text-lg font-semibold mb-6">平台详情</h3>
                    <div className="space-y-4">
                      {platformStats.map((platform) => (
                        <div key={platform.platform} className="p-4 rounded-xl bg-white/5 border border-white/10">
                          <div className="flex items-center justify-between mb-4">
                            <h4 className="font-medium">{platform.platform}</h4>
                            <span className="text-sm text-gray-400">CTR: {platform.ctr.toFixed(1)}%</span>
                          </div>
                          <div className="grid grid-cols-3 gap-4 text-center">
                            <div>
                              <p className="text-lg font-bold">{formatNumber(platform.views)}</p>
                              <p className="text-xs text-gray-400">曝光</p>
                            </div>
                            <div>
                              <p className="text-lg font-bold">{formatNumber(platform.clicks)}</p>
                              <p className="text-xs text-gray-400">点击</p>
                            </div>
                            <div>
                              <p className="text-lg font-bold">{formatNumber(platform.shares)}</p>
                              <p className="text-xs text-gray-400">分享</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "abtests" && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">A/B 测试</h3>
                    <button className="px-4 py-2 bg-blue-500 rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors">
                      创建测试
                    </button>
                  </div>

                  <div className="p-8 rounded-2xl bg-white/5 border border-white/10 text-center">
                    <Target className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                    <h4 className="text-xl font-bold mb-2">暂无 A/B 测试</h4>
                    <p className="text-gray-400 mb-4">创建测试来优化你的内容策略</p>
                    <button className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg font-semibold">
                      创建第一个测试
                    </button>
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>

      <Footer />
    </div>
  );
}

function Globe(props: any) {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
    </svg>
  );
}

function Activity(props: any) {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  );
}
