"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Settings,
  User,
  Bell,
  Shield,
  CreditCard,
  Palette,
  Globe,
  Key,
  Mail,
  Building2,
  Save,
  Camera,
  ChevronRight,
  Check,
  AlertCircle
} from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("profile");
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const tabs = [
    { id: "profile", name: "个人资料", icon: User },
    { id: "security", name: "安全设置", icon: Shield },
    { id: "notifications", name: "通知设置", icon: Bell },
    { id: "billing", name: "账单管理", icon: CreditCard },
    { id: "appearance", name: "外观设置", icon: Palette },
    { id: "api", name: "API 密钥", icon: Key },
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <Navbar />

      <main className="pt-24 pb-16">
        <div className="max-w-6xl mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h1 className="text-3xl font-bold text-white mb-2">
              <Settings className="inline-block w-8 h-8 mr-2 text-blue-500" />
              设置
            </h1>
            <p className="text-gray-400">管理您的账户和偏好设置</p>
          </motion.div>

          <div className="flex flex-col md:flex-row gap-6">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="w-full md:w-64 flex-shrink-0"
            >
              <div className="bg-[#12121a] rounded-2xl border border-white/10 p-4">
                <nav className="space-y-1">
                  {tabs.map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                          activeTab === tab.id
                            ? 'bg-blue-500/20 text-blue-400'
                            : 'text-gray-400 hover:bg-white/5 hover:text-white'
                        }`}
                      >
                        <Icon className="w-5 h-5" />
                        <span className="font-medium">{tab.name}</span>
                      </button>
                    );
                  })}
                </nav>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex-1"
            >
              {activeTab === "profile" && (
                <div className="bg-[#12121a] rounded-2xl border border-white/10 p-6">
                  <h2 className="text-xl font-semibold text-white mb-6">个人资料</h2>

                  <div className="flex items-center gap-6 mb-8">
                    <div className="relative">
                      <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-2xl font-bold text-white">
                        U
                      </div>
                      <button className="absolute bottom-0 right-0 p-2 bg-blue-500 rounded-full text-white hover:bg-blue-600 transition-colors">
                        <Camera className="w-4 h-4" />
                      </button>
                    </div>
                    <div>
                      <div className="font-medium text-white text-lg">用户名</div>
                      <div className="text-gray-400">user@example.com</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">显示名称</label>
                      <input
                        type="text"
                        defaultValue="用户名"
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">邮箱地址</label>
                      <input
                        type="email"
                        defaultValue="user@example.com"
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">公司名称</label>
                      <input
                        type="text"
                        placeholder="输入公司名称"
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">个人简介</label>
                      <input
                        type="text"
                        placeholder="简单介绍一下自己"
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <button
                      onClick={handleSave}
                      className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all flex items-center gap-2"
                    >
                      {saved ? <Check className="w-5 h-5" /> : <Save className="w-5 h-5" />}
                      {saved ? '已保存' : '保存更改'}
                    </button>
                  </div>
                </div>
              )}

              {activeTab === "security" && (
                <div className="bg-[#12121a] rounded-2xl border border-white/10 p-6">
                  <h2 className="text-xl font-semibold text-white mb-6">安全设置</h2>

                  <div className="space-y-6">
                    <div className="p-4 bg-white/5 rounded-xl">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <Key className="w-5 h-5 text-blue-400" />
                          <div>
                            <div className="font-medium text-white">密码</div>
                            <div className="text-sm text-gray-400">最后修改于 30 天前</div>
                          </div>
                        </div>
                        <button className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors">
                          修改密码
                        </button>
                      </div>
                    </div>

                    <div className="p-4 bg-white/5 rounded-xl">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <Shield className="w-5 h-5 text-green-400" />
                          <div>
                            <div className="font-medium text-white">两步验证</div>
                            <div className="text-sm text-gray-400">为账户添加额外安全保障</div>
                          </div>
                        </div>
                        <button className="px-4 py-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors">
                          立即启用
                        </button>
                      </div>
                    </div>

                    <div className="p-4 bg-white/5 rounded-xl">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <AlertCircle className="w-5 h-5 text-red-400" />
                          <div>
                            <div className="font-medium text-white">会话管理</div>
                            <div className="text-sm text-gray-400">管理您所有活跃的登录会话</div>
                          </div>
                        </div>
                        <button className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors">
                          查看会话
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "notifications" && (
                <div className="bg-[#12121a] rounded-2xl border border-white/10 p-6">
                  <h2 className="text-xl font-semibold text-white mb-6">通知设置</h2>

                  <div className="space-y-4">
                    {[
                      { title: "生成完成通知", desc: "海报、视频等生成完成时通知", default: true },
                      { title: "协作邀请", desc: "收到协作邀请时通知", default: true },
                      { title: "订阅提醒", desc: "订阅即将到期时提醒", default: true },
                      { title: "产品更新", desc: "产品有重大更新时通知", default: false },
                      { title: "营销邮件", desc: "接收最新的产品资讯和优惠", default: false },
                    ].map((item, index) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                        <div>
                          <div className="font-medium text-white">{item.title}</div>
                          <div className="text-sm text-gray-400">{item.desc}</div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            defaultChecked={item.default}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                        </label>
                      </div>
                    ))}
                  </div>

                  <div className="flex justify-end mt-6">
                    <button
                      onClick={handleSave}
                      className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all flex items-center gap-2"
                    >
                      {saved ? <Check className="w-5 h-5" /> : <Save className="w-5 h-5" />}
                      {saved ? '已保存' : '保存更改'}
                    </button>
                  </div>
                </div>
              )}

              {activeTab === "billing" && (
                <div className="bg-[#12121a] rounded-2xl border border-white/10 p-6">
                  <h2 className="text-xl font-semibold text-white mb-6">账单管理</h2>

                  <div className="p-4 bg-gradient-to-r from-blue-500/20 to-purple-600/20 rounded-xl border border-blue-500/20 mb-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm text-gray-400">当前订阅</div>
                        <div className="text-2xl font-bold text-white">专业版</div>
                        <div className="text-sm text-gray-400">有效期至 2024-02-15</div>
                      </div>
                      <button className="px-4 py-2 bg-blue-500/20 text-blue-400 rounded-lg hover:bg-blue-500/30 transition-colors">
                        升级套餐
                      </button>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="p-4 bg-white/5 rounded-xl">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <CreditCard className="w-5 h-5 text-blue-400" />
                          <div>
                            <div className="font-medium text-white">•••• •••• •••• 4242</div>
                            <div className="text-sm text-gray-400">有效期至 12/2025</div>
                          </div>
                        </div>
                        <button className="text-blue-400 hover:text-blue-300 transition-colors">
                          修改
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "appearance" && (
                <div className="bg-[#12121a] rounded-2xl border border-white/10 p-6">
                  <h2 className="text-xl font-semibold text-white mb-6">外观设置</h2>

                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm text-gray-400 mb-3">主题模式</label>
                      <div className="grid grid-cols-3 gap-4">
                        {['dark', 'light', 'system'].map((theme) => (
                          <button
                            key={theme}
                            className={`p-4 rounded-xl border-2 transition-all ${
                              theme === 'dark'
                                ? 'border-blue-500 bg-blue-500/10'
                                : 'border-white/10 hover:border-white/20'
                            }`}
                          >
                            <div className="text-center">
                              <div className="text-white capitalize mb-1">{theme}</div>
                              <div className="text-xs text-gray-400">
                                {theme === 'dark' ? '深色主题' : theme === 'light' ? '浅色主题' : '跟随系统'}
                              </div>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm text-gray-400 mb-3">语言</label>
                      <select className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-blue-500">
                        <option value="zh">简体中文</option>
                        <option value="en">English</option>
                        <option value="ja">日本語</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "api" && (
                <div className="bg-[#12121a] rounded-2xl border border-white/10 p-6">
                  <h2 className="text-xl font-semibold text-white mb-6">API 密钥</h2>

                  <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-xl mb-6">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 text-yellow-400 mt-0.5" />
                      <div className="text-sm text-yellow-200">
                        请妥善保管您的 API 密钥，不要将其分享给他人或提交到公开的代码仓库中。
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="p-4 bg-white/5 rounded-xl">
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-medium text-white">默认 API 密钥</div>
                        <button className="text-red-400 hover:text-red-300 text-sm transition-colors">
                          重新生成
                        </button>
                      </div>
                      <div className="font-mono text-sm text-gray-400 bg-black/30 px-3 py-2 rounded-lg">
                        pc_sk_•••••••••••••••••••••
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
