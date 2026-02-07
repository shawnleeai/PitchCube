"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Users,
  Plus,
  Settings,
  MessageSquare,
  MousePointer2,
  Lock,
  Unlock,
  Send,
  Crown,
  Edit,
  Eye,
  MoreVertical,
  Trash2,
  Share2,
  Clock,
  ChevronRight,
  UserPlus,
  Copy,
  Check,
  X
} from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface Project {
  id: string;
  name: string;
  description: string;
  project_type: string;
  status: string;
  owner_id: string;
  collaborators: { user_id: string; role: string; username: string }[];
  updated_at: string;
}

interface ActiveUser {
  user_id: string;
  username: string;
  cursor?: { x: number; y: number };
  last_activity: string;
}

interface ChatMessage {
  user_id: string;
  username: string;
  message: string;
  timestamp: string;
}

const projectStatusConfig: Record<string, { label: string; bgClass: string; textClass: string }> = {
  draft: { label: "草稿", bgClass: "bg-gray-500/20", textClass: "text-gray-400" },
  in_progress: { label: "进行中", bgClass: "bg-blue-500/20", textClass: "text-blue-400" },
  completed: { label: "已完成", bgClass: "bg-green-500/20", textClass: "text-green-400" }
};

export default function CollabPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [activeUsers, setActiveUsers] = useState<ActiveUser[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [isConnected, setIsConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectDesc, setNewProjectDesc] = useState("");
  const [newProjectType, setNewProjectType] = useState("poster");
  const [copiedLink, setCopiedLink] = useState(false);
  const [cursorPositions, setCursorPositions] = useState<Record<string, { x: number; y: number }>>({});

  const userId = "user_123";
  const username = "演示用户";

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/collab/projects`);
      if (response.ok) {
        const data = await response.json();
        setProjects(data);
      }
    } catch (error) {
      console.error("Failed to fetch projects:", error);
      setProjects([
        {
          id: "proj_demo_1",
          name: "产品路演项目",
          description: "黑客松路演海报设计",
          project_type: "poster",
          status: "in_progress",
          owner_id: "user_123",
          collaborators: [
            { user_id: "user_456", role: "editor", username: "设计师小王" },
            { user_id: "user_789", role: "viewer", username: "产品经理" }
          ],
          updated_at: new Date().toISOString()
        },
        {
          id: "proj_demo_2",
          name: "品牌宣传视频",
          description: "产品介绍视频制作",
          project_type: "video",
          status: "draft",
          owner_id: "user_123",
          collaborators: [],
          updated_at: new Date().toISOString()
        }
      ]);
    }
  };

  const connectToProject = useCallback((projectId: string) => {
    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/collab/${projectId}?user_id=${userId}&username=${username}`;
    
    try {
      const websocket = new WebSocket(wsUrl);
      
      websocket.onopen = () => {
        setIsConnected(true);
        console.log("Connected to collaboration");
      };
      
      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === "project_update") {
          if (data.user_joined) {
            setActiveUsers(prev => [...prev, { user_id: data.user_id, username: data.username, last_activity: new Date().toISOString() }]);
          } else if (data.user_left) {
            setActiveUsers(prev => prev.filter(u => u.user_id !== data.user_id));
          } else if (data.active_users) {
            setActiveUsers(data.active_users);
          } else if (data.action === "content_changed") {
            console.log("Content changed:", data.changes);
          }
        } else if (data.type === "cursor_update") {
          setCursorPositions(prev => ({
            ...prev,
            [data.user_id]: { x: data.position?.x || 0, y: data.position?.y || 0 }
          }));
        } else if (data.type === "chat") {
          setChatMessages(prev => [...prev, {
            user_id: data.user_id,
            username: data.username,
            message: data.message,
            timestamp: data.timestamp
          }]);
        }
      };
      
      websocket.onclose = () => {
        setIsConnected(false);
        console.log("Disconnected from collaboration");
      };
      
      websocket.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
      
      setWs(websocket);
    } catch (error) {
      console.error("Failed to connect to WebSocket:", error);
    }
  }, []);

  const disconnectFromProject = useCallback(() => {
    if (ws) {
      ws.close();
      setWs(null);
      setIsConnected(false);
      setActiveUsers([]);
      setChatMessages([]);
    }
  }, [ws]);

  useEffect(() => {
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [ws]);

  const sendMessage = () => {
    if (ws && newMessage.trim()) {
      ws.send(JSON.stringify({
        type: "chat",
        message: newMessage,
        user_id: userId,
        username: username,
        timestamp: new Date().toISOString()
      }));
      
      setChatMessages(prev => [...prev, {
        user_id: userId,
        username: username,
        message: newMessage,
        timestamp: new Date().toISOString()
      }]);
      
      setNewMessage("");
    }
  };

  const createProject = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/collab/projects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: newProjectName,
          description: newProjectDesc,
          project_type: newProjectType
        })
      });
      
      if (response.ok) {
        const project = await response.json();
        setProjects(prev => [...prev, project]);
        setShowCreateModal(false);
        setNewProjectName("");
        setNewProjectDesc("");
        setNewProjectType("poster");
      }
    } catch (error) {
      console.error("Failed to create project:", error);
      const newProject: Project = {
        id: `proj_${Date.now()}`,
        name: newProjectName,
        description: newProjectDesc,
        project_type: newProjectType,
        status: "draft",
        owner_id: userId,
        collaborators: [],
        updated_at: new Date().toISOString()
      };
      setProjects(prev => [...prev, newProject]);
      setShowCreateModal(false);
      setNewProjectName("");
      setNewProjectDesc("");
      setNewProjectType("poster");
    }
  };

  const copyInviteLink = () => {
    if (activeProject) {
      navigator.clipboard.writeText(`${window.location.origin}/collab/${activeProject.id}`);
      setCopiedLink(true);
      setTimeout(() => setCopiedLink(false), 2000);
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
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
                <span className="gradient-text">协作空间</span>
              </h1>
              <p className="text-gray-400">与团队成员实时协作，共同创作</p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/25 transition-all"
            >
              <Plus className="w-5 h-5" />
              新建项目
            </button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-6 p-4 rounded-xl bg-white/5 border border-white/10 flex items-center gap-4"
          >
            <div className={`w-3 h-3 rounded-full ${isConnected ? "bg-green-500 animate-pulse" : "bg-yellow-500"}`} />
            <span className="text-sm text-gray-400">
              {isConnected ? "已连接到实时协作服务" : "未连接 - 请选择一个项目"}
            </span>
            <div className="ml-auto flex items-center gap-2">
              <Users className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-400">
                {activeUsers.length} 位用户在线
              </span>
            </div>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="lg:col-span-1 space-y-4"
            >
              <h2 className="text-lg font-semibold mb-4">我的项目</h2>
              
              {projects.map((project) => {
                const statusConf = projectStatusConfig[project.status] || projectStatusConfig.draft;
                return (
                  <button
                    key={project.id}
                    onClick={() => {
                      setActiveProject(project);
                      connectToProject(project.id);
                      setChatMessages([]);
                    }}
                    className={`w-full p-4 rounded-xl border text-left transition-all ${
                      activeProject?.id === project.id
                        ? "bg-blue-500/10 border-blue-500/50"
                        : "bg-white/5 border-white/10 hover:border-white/20"
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-medium text-white">{project.name}</h3>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${statusConf.bgClass} ${statusConf.textClass}`}>
                        {statusConf.label}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400 mb-2">{project.description}</p>
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Users className="w-3 h-3" />
                        {project.collaborators.length + 1}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(project.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </button>
                );
              })}
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="lg:col-span-2"
            >
              {activeProject ? (
                <div className="space-y-6">
                  <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-white/10">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h2 className="text-2xl font-bold mb-2 text-white">{activeProject.name}</h2>
                        <p className="text-gray-400">{activeProject.description}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={copyInviteLink}
                          className="flex items-center gap-2 px-3 py-1.5 bg-white/10 rounded-lg text-sm hover:bg-white/20 transition-colors text-white"
                        >
                          {copiedLink ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                          {copiedLink ? "已复制" : "复制链接"}
                        </button>
                        <button className="p-1.5 bg-white/10 rounded-lg hover:bg-white/20 transition-colors text-white">
                          <Settings className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="flex -space-x-2">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xs font-medium text-white ring-2 ring-[#0a0a0f]">
                          你
                        </div>
                        {activeUsers.filter(u => u.user_id !== userId).slice(0, 3).map((user) => (
                          <div
                            key={user.user_id}
                            className="w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center text-xs font-medium text-white ring-2 ring-[#0a0a0f]"
                          >
                            {user.username[0]}
                          </div>
                        ))}
                        {activeUsers.length > 4 && (
                          <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center text-xs font-medium text-white ring-2 ring-[#0a0a0f]">
                            +{activeUsers.length - 4}
                          </div>
                        )}
                      </div>
                      <span className="text-sm text-gray-400">
                        {activeUsers.length} 位协作者
                      </span>
                    </div>
                  </div>

                  <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                    <h3 className="text-lg font-semibold mb-4 text-white">实时协作画布</h3>
                    <div className="aspect-video bg-white/5 rounded-xl flex items-center justify-center relative overflow-hidden">
                      <div className="absolute inset-0 grid grid-cols-12 grid-rows-6 gap-1 opacity-10">
                        {Array.from({ length: 72 }).map((_, i) => (
                          <div key={i} className="border border-gray-500" />
                        ))}
                      </div>
                      <div className="text-center z-10">
                        <MousePointer2 className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                        <p className="text-gray-400 mb-4">实时协作画布加载中...</p>
                        <p className="text-sm text-gray-500">选择工具开始协作</p>
                      </div>
                      {Object.entries(cursorPositions).map(([userId, pos]) => (
                        <div
                          key={userId}
                          className="absolute pointer-events-none transition-all duration-100"
                          style={{ left: pos.x, top: pos.y }}
                        >
                          <MousePointer2 className="w-5 h-5 text-blue-400" />
                          <span className="text-xs text-blue-400 bg-blue-400/20 px-1 rounded">{userId}</span>
                        </div>
                      ))}
                    </div>
                    <div className="flex items-center gap-2 mt-4">
                      <button className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors text-white">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors text-white">
                        <Eye className="w-4 h-4" />
                      </button>
                      <div className="flex-1" />
                      <button className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg text-sm font-medium hover:shadow-lg transition-all text-white">
                        保存更改
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-12 rounded-2xl bg-white/5 border border-white/10 text-center">
                  <Users className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                  <h3 className="text-xl font-semibold mb-2 text-white">选择一个项目开始协作</h3>
                  <p className="text-gray-400">从左侧选择一个项目，或创建一个新项目</p>
                </div>
              )}
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
              className="lg:col-span-1"
            >
              <div className="bg-white/5 border border-white/10 rounded-2xl p-4">
                <div className="flex items-center gap-2 mb-4">
                  <MessageSquare className="w-5 h-5 text-blue-400" />
                  <h3 className="font-semibold text-white">聊天</h3>
                </div>
                
                <div className="space-y-3 mb-4 max-h-64 overflow-y-auto">
                  {chatMessages.length === 0 ? (
                    <p className="text-sm text-gray-500 text-center py-8">暂无消息</p>
                  ) : (
                    chatMessages.map((msg, i) => (
                      <div key={i} className={`${msg.user_id === userId ? 'text-right' : 'text-left'}`}>
                        <div className={`inline-block max-w-[80%] px-3 py-2 rounded-xl ${
                          msg.user_id === userId
                            ? 'bg-blue-500/20 text-blue-400'
                            : 'bg-white/10 text-gray-300'
                        }`}>
                          {msg.user_id !== userId && (
                            <p className="text-xs text-gray-500 mb-1">{msg.username}</p>
                          )}
                          <p className="text-sm">{msg.message}</p>
                        </div>
                        <p className="text-xs text-gray-600 mt-1">{formatTime(msg.timestamp)}</p>
                      </div>
                    ))
                  )}
                </div>
                
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="输入消息..."
                    className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!newMessage.trim()}
                    className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed text-white"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {activeProject && (
                <div className="mt-4 bg-white/5 border border-white/10 rounded-2xl p-4">
                  <h3 className="font-semibold mb-4 text-white">项目成员</h3>
                  <div className="space-y-2">
                    <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xs font-medium text-white">
                        你
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-white">{username}</p>
                        <p className="text-xs text-gray-500">所有者</p>
                      </div>
                      <Crown className="w-4 h-4 text-amber-400" />
                    </div>
                    {activeProject.collaborators.map((collab) => (
                      <div key={collab.user_id} className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center text-xs font-medium text-white">
                          {collab.username[0]}
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-white">{collab.username}</p>
                          <p className="text-xs text-gray-500">{collab.role === 'editor' ? '编辑者' : '查看者'}</p>
                        </div>
                        {collab.role === 'editor' && <Edit className="w-4 h-4 text-blue-400" />}
                      </div>
                    ))}
                    <button className="w-full flex items-center gap-2 p-2 rounded-lg border border-dashed border-white/20 text-gray-400 hover:text-white hover:border-white/40 transition-colors">
                      <UserPlus className="w-4 h-4" />
                      <span className="text-sm">邀请成员</span>
                    </button>
                  </div>
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </div>

      <Footer />

      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-[#1a1a24] rounded-2xl border border-white/10 p-6 max-w-md mx-4 w-full"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-white">新建协作项目</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-1 text-gray-400 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">项目名称</label>
                  <input
                    type="text"
                    value={newProjectName}
                    onChange={(e) => setNewProjectName(e.target.value)}
                    placeholder="输入项目名称"
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">项目描述</label>
                  <textarea
                    value={newProjectDesc}
                    onChange={(e) => setNewProjectDesc(e.target.value)}
                    placeholder="简单描述项目内容"
                    rows={3}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">项目类型</label>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { id: 'poster', name: '海报', icon: FileText },
                      { id: 'video', name: '视频', icon: Video },
                      { id: 'voice', name: '语音', icon: Mic },
                      { id: 'ip', name: 'IP形象', icon: Box }
                    ].map((type) => (
                      <button
                        key={type.id}
                        onClick={() => setNewProjectType(type.id)}
                        className={`p-3 rounded-xl border transition-all flex items-center gap-2 ${
                          newProjectType === type.id
                            ? 'bg-blue-500/20 border-blue-500 text-blue-400'
                            : 'bg-white/5 border-white/10 text-gray-400 hover:border-white/20'
                        }`}
                      >
                        <type.icon className="w-4 h-4" />
                        <span className="text-sm">{type.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="flex gap-3">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
                >
                  取消
                </button>
                <button
                  onClick={createProject}
                  disabled={!newProjectName.trim()}
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  创建项目
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function FileText(props: any) {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  );
}

function Video(props: any) {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
  );
}

function Mic(props: any) {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
    </svg>
  );
}

function Box(props: any) {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
    </svg>
  );
}
