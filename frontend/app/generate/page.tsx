"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Palette, 
  Video, 
  Box, 
  Mic,
  Upload,
  Image as ImageIcon,
  FileText,
  Download,
  Sparkles,
  Check,
  ChevronRight,
  Loader2,
  Wand2,
  RefreshCw,
  Zap
} from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { demoProducts, fillDemoData } from "@/lib/demo-data";

// API配置
const RAW_API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const NORMALIZED_API_BASE_URL = RAW_API_BASE_URL.replace(/\/$/, "");
const API_BASE_URL = NORMALIZED_API_BASE_URL.endsWith("/api/v1")
  ? NORMALIZED_API_BASE_URL
  : `${NORMALIZED_API_BASE_URL}/api/v1`;

type GenerationType = "poster" | "video" | "ip" | "voice";
type GenerationStatus = "pending" | "processing" | "completed" | "failed";

interface ProductInfo {
  name: string;
  description: string;
  features: string;
  target: string;
}

interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  colors: string[];
}

interface VideoTemplate {
  id: string;
  name: string;
  description: string;
  duration_range: string;
  platforms: string[];
}

interface VideoScriptScene {
  scene_number: number;
  duration: number;
  visual_description: string;
  narration: string;
  subtitle: string;
}

interface VideoScriptScene {
  scene_number: number;
  duration: number;
  visual_description: string;
  narration: string;
  subtitle: string;
}

interface VideoScript {
  title?: string;
  total_duration?: number;
  target_platform?: string;
  scenes?: VideoScriptScene[];
  background_music_suggestion?: string;
}

interface GenerationResponse {
  id: string;
  status: GenerationStatus;
  product_name: string;
  template_id?: string;
  preview_url?: string;
  download_urls: {
    png?: string;
    jpg?: string;
  };
  audio_url?: string;
  video_url?: string;
  script?: VideoScript;
  voice_id?: string;
  voice_name?: string;
  duration_estimate?: number;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

interface VoiceInfo {
  id: string;
  name: string;
  gender: string;
  style: string;
  description: string;
  tags: string[];
}

interface VoiceRecommendation {
  scenario: string;
  scenario_name: string;
  description: string;
  recommended_voices: VoiceInfo[];
}

const generationTypes = [
  {
    id: "poster" as GenerationType,
    title: "海报工坊",
    description: "生成专业路演海报",
    icon: Palette,
    color: "from-blue-500 to-cyan-500",
    available: true,
  },
  {
    id: "video" as GenerationType,
    title: "视频演播室",
    description: "生成视频脚本与演示",
    icon: Video,
    color: "from-purple-500 to-pink-500",
    available: true,
  },
  {
    id: "ip" as GenerationType,
    title: "IP铸造厂",
    description: "生成3D打印IP形象",
    icon: Box,
    color: "from-amber-500 to-orange-500",
    available: false,
  },
  {
    id: "voice" as GenerationType,
    title: "语音解说员",
    description: "生成语音讲解",
    icon: Mic,
    color: "from-emerald-500 to-teal-500",
    available: true,
  },
];

export default function GeneratePage() {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [selectedType, setSelectedType] = useState<GenerationType | null>(null);
  const [productInfo, setProductInfo] = useState<ProductInfo>({
    name: "",
    description: "",
    features: "",
    target: "",
  });
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>("tech-modern");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationId, setGenerationId] = useState<string | null>(null);
  const [generationStatus, setGenerationStatus] = useState<GenerationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // 语音生成相关状态
  const [voices, setVoices] = useState<VoiceInfo[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<string>("zhengpaiqingnian");
  const [voiceSpeed, setVoiceSpeed] = useState<number>(1.0);
  const [voiceRecommendations, setVoiceRecommendations] = useState<VoiceRecommendation[]>([]);
  const [voiceText, setVoiceText] = useState<string>("");

  // 视频生成相关状态
  const [videoTemplates, setVideoTemplates] = useState<VideoTemplate[]>([]);
  const [selectedVideoTemplate, setSelectedVideoTemplate] = useState<string>("product-demo");
  const [videoScriptStyle, setVideoScriptStyle] = useState<string>("professional");
  const [videoTargetPlatform, setVideoTargetPlatform] = useState<string>("youtube");
  const [videoTargetDuration, setVideoTargetDuration] = useState<number>(60);

  // 加载模板列表和音色列表
  useEffect(() => {
    fetchTemplates();
    fetchVoices();
    fetchVoiceRecommendations();
    fetchVideoTemplates();
  }, []);

  const fetchVoices = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/voice/voices`);
      if (response.ok) {
        const data = await response.json();
        setVoices(data);
        if (data.length > 0) {
          setSelectedVoice(data[0].id);
        }
      }
    } catch (err) {
      console.error("Failed to fetch voices:", err);
    }
  };

  const fetchVoiceRecommendations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/voice/recommendations`);
      if (response.ok) {
        const data = await response.json();
        setVoiceRecommendations(data);
      }
    } catch (err) {
      console.error("Failed to fetch voice recommendations:", err);
    }
  };

  const fetchVideoTemplates = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/videos/templates`);
      if (response.ok) {
        const data = await response.json();
        setVideoTemplates(data);
      }
    } catch (err) {
      console.error("Failed to fetch video templates:", err);
    }
  };

  // 轮询生成状态
  useEffect(() => {
    if (!generationId || generationStatus?.status === "completed" || generationStatus?.status === "failed") {
      return;
    }

    const interval = setInterval(async () => {
      try {
        let endpoint;
        if (selectedType === "voice") {
          endpoint = `${API_BASE_URL}/voice/generations/${generationId}`;
        } else if (selectedType === "video") {
          endpoint = `${API_BASE_URL}/videos/generations/${generationId}`;
        } else {
          endpoint = `${API_BASE_URL}/posters/generations/${generationId}`;
        }
        
        const response = await fetch(endpoint);
        if (response.ok) {
          const data = await response.json();
          setGenerationStatus(data);
          
          if (data.status === "completed" || data.status === "failed") {
            setIsGenerating(false);
            if (data.status === "completed") {
              setStep(3);
            }
          }
        }
      } catch (err) {
        console.error("Failed to check status:", err);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [generationId, generationStatus, selectedType]);

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/posters/templates`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      }
    } catch (err) {
      console.error("Failed to fetch templates:", err);
    }
  };

  const handleGenerate = async () => {
    if (selectedType === "poster") {
      await generatePoster();
    } else if (selectedType === "voice") {
      await generateVoice();
    } else if (selectedType === "video") {
      await generateVideo();
    } else {
      // 其他类型暂未实现
      setError("该功能即将推出，敬请期待");
    }
  };

  const generatePoster = async () => {
    if (!productInfo.name.trim()) {
      setError("请填写产品名称");
      return;
    }

    if (productInfo.description.trim().length < 10) {
      setError("产品描述至少需要 10 个字符");
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/posters/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          product_name: productInfo.name,
          product_description: productInfo.description,
          key_features: productInfo.features.split("\n").filter(f => f.trim()),
          target_audience: productInfo.target,
          template_id: selectedTemplate,
        }),
      });

      if (!response.ok) {
        let message = "生成失败，请重试";
        try {
          const errorBody = await response.json();
          if (typeof errorBody?.detail === "string") {
            message = errorBody.detail;
          } else if (Array.isArray(errorBody?.detail)) {
            message = errorBody.detail
              .map((item: any) => item?.msg || item?.message)
              .filter(Boolean)
              .join("；") || message;
          }
        } catch {
          // ignore parse errors
        }
        throw new Error(message);
      }

      const data = await response.json();
      setGenerationId(data.id);
      setGenerationStatus(data);
    } catch (err: any) {
      setError(err.message);
      setIsGenerating(false);
    }
  };

  const generateVoice = async () => {
    const textToGenerate = voiceText.trim() || productInfo.description.trim();

    if (!textToGenerate) {
      setError("请输入要转换的文本");
      return;
    }

    if (textToGenerate.length < 5) {
      setError("文本至少需要 5 个字符");
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/voice/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: textToGenerate,
          voice_style: voices.find(v => v.id === selectedVoice)?.style || "professional",
          speed: voiceSpeed,
        }),
      });

      if (!response.ok) {
        let message = "语音生成失败";
        try {
          const errorBody = await response.json();
          message = errorBody.detail || message;
        } catch {}
        throw new Error(message);
      }

      const data = await response.json();
      setGenerationId(data.id);
      setGenerationStatus(data);
    } catch (err: any) {
      setError(err.message);
      setIsGenerating(false);
    }
  };

  const generateVideo = async () => {
    if (!productInfo.name.trim()) {
      setError("请填写产品名称");
      return;
    }

    if (productInfo.description.trim().length < 10) {
      setError("产品描述至少需要 10 个字符");
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/videos/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          product_id: Date.now().toString(),
          product_name: productInfo.name,
          product_description: productInfo.description,
          key_features: productInfo.features.split("\n").filter(f => f.trim()),
          script_style: videoScriptStyle,
          target_duration: videoTargetDuration,
          target_platform: videoTargetPlatform,
          include_subtitles: true,
        }),
      });

      if (!response.ok) {
        let message = "视频生成失败";
        try {
          const errorBody = await response.json();
          if (typeof errorBody?.detail === "string") {
            message = errorBody.detail;
          } else if (Array.isArray(errorBody?.detail)) {
            message = errorBody.detail
              .map((item: any) => item?.msg || item?.message)
              .filter(Boolean)
              .join("；") || message;
          }
        } catch {
          // ignore parse errors
        }
        throw new Error(message);
      }

      const data = await response.json();
      setGenerationId(data.id);
      setGenerationStatus(data);
    } catch (err: any) {
      setError(err.message);
      setIsGenerating(false);
    }
  };

  const handleDownload = (url: string, filename: string) => {
    const fullUrl = `${API_BASE_URL.replace("/api/v1", "")}${url}`;
    const link = document.createElement("a");
    link.href = fullUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const resetForm = () => {
    setStep(1);
    setSelectedType(null);
    setProductInfo({ name: "", description: "", features: "", target: "" });
    setGenerationId(null);
    setGenerationStatus(null);
    setError(null);
    setVoiceText("");
    setVoiceSpeed(1.0);
    setSelectedVoice(voices.length > 0 ? voices[0].id : "zhengpaiqingnian");
    setSelectedVideoTemplate("product-demo");
    setVideoScriptStyle("professional");
    setVideoTargetPlatform("youtube");
    setVideoTargetDuration(60);
  };

  return (
    <main className="min-h-screen bg-[#0a0a0f] text-white">
      <Navbar />
      
      <div className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="gradient-text">生成路演物料</span>
            </h1>
            <p className="text-gray-400 text-lg">
              选择生成类型，输入产品信息，AI 将为你生成专业展示物料
            </p>
          </motion.div>

          {/* 步骤指示器 */}
          <div className="flex items-center justify-center gap-4 mb-12">
            {[1, 2, 3].map((s) => (
              <div key={s} className="flex items-center gap-4">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-colors ${
                    step >= s
                      ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white"
                      : "bg-white/10 text-gray-500"
                  }`}
                >
                  {step > s ? <Check className="w-5 h-5" /> : s}
                </div>
                {s < 3 && (
                  <div
                    className={`w-16 h-0.5 transition-colors ${
                      step > s ? "bg-gradient-to-r from-blue-500 to-purple-600" : "bg-white/10"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>

          {/* 错误提示 */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400"
            >
              {error}
            </motion.div>
          )}

          <AnimatePresence mode="wait">
            {/* 步骤1: 选择类型 */}
            {step === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                <h2 className="text-2xl font-bold text-center mb-8">选择生成类型</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {generationTypes.map((type) => (
                    <button
                      key={type.id}
                      onClick={() => type.available && setSelectedType(type.id)}
                      disabled={!type.available}
                      className={`relative p-6 rounded-2xl border transition-all duration-300 text-left ${
                        selectedType === type.id
                          ? "border-blue-500 bg-blue-500/10"
                          : type.available
                          ? "border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/[0.07]"
                          : "border-white/5 bg-white/[0.02] opacity-50 cursor-not-allowed"
                      }`}
                    >
                      <div
                        className={`w-12 h-12 rounded-xl bg-gradient-to-br ${type.color} flex items-center justify-center mb-4`}
                      >
                        <type.icon className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="text-lg font-semibold mb-1">{type.title}</h3>
                      <p className="text-sm text-gray-400">{type.description}</p>
                      {!type.available && (
                        <span className="absolute top-4 right-4 px-2 py-1 text-xs bg-white/10 rounded-full">
                          即将推出
                        </span>
                      )}
                      {selectedType === type.id && (
                        <div className="absolute top-4 right-4 w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center">
                          <Check className="w-4 h-4 text-white" />
                        </div>
                      )}
                    </button>
                  ))}
                </div>

                <div className="flex justify-end pt-6">
                  <button
                    onClick={() => setStep(2)}
                    disabled={!selectedType}
                    className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-blue-500/25 transition-all"
                  >
                    下一步
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </motion.div>
            )}

            {/* 步骤2: 输入信息 */}
            {step === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                <h2 className="text-2xl font-bold text-center mb-8">输入产品信息</h2>
                
                {/* 快速演示按钮 */}
                <div className="p-4 rounded-xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Zap className="w-5 h-5 text-amber-400" />
                      <span className="text-sm text-amber-200">快速体验？选择演示产品一键填充</span>
                    </div>
                    <div className="flex gap-2">
                      {demoProducts.map((_, index) => (
                        <button
                          key={index}
                          onClick={() => {
                            const data = fillDemoData(index);
                            setProductInfo({
                              name: data.name,
                              description: data.description,
                              features: data.features,
                              target: data.target,
                            });
                            setSelectedTemplate(data.template);
                          }}
                          className="px-3 py-1.5 text-xs rounded-lg bg-amber-500/20 text-amber-300 hover:bg-amber-500/30 transition-colors"
                        >
                          示例 {index + 1}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* 海报类型：模板选择 */}
                {selectedType === "poster" && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-3">
                      选择模板风格
                    </label>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      {templates.map((template) => (
                        <button
                          key={template.id}
                          onClick={() => setSelectedTemplate(template.id)}
                          className={`p-3 rounded-xl border text-left transition-all ${
                            selectedTemplate === template.id
                              ? "border-blue-500 bg-blue-500/10"
                              : "border-white/10 bg-white/5 hover:border-white/20"
                          }`}
                        >
                          <div className="flex gap-1 mb-2">
                            {template.colors.slice(0, 3).map((color, i) => (
                              <div
                                key={i}
                                className="w-4 h-4 rounded-full"
                                style={{ backgroundColor: color }}
                              />
                            ))}
                          </div>
                          <p className="text-sm font-medium">{template.name}</p>
                          <p className="text-xs text-gray-500">{template.category}</p>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* 视频类型：参数配置 */}
                {selectedType === "video" && (
                  <div className="space-y-4">
                    {/* 视频模板选择 */}
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-3">
                        选择视频模板
                      </label>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {videoTemplates.map((template) => (
                          <button
                            key={template.id}
                            onClick={() => setSelectedVideoTemplate(template.id)}
                            className={`p-4 rounded-xl border text-left transition-all ${
                              selectedVideoTemplate === template.id
                                ? "border-purple-500 bg-purple-500/10"
                                : "border-white/10 bg-white/5 hover:border-white/20"
                            }`}
                          >
                            <div className="flex items-center gap-2 mb-2">
                              <Video className="w-5 h-5 text-purple-400" />
                              <span className="font-medium">{template.name}</span>
                            </div>
                            <p className="text-xs text-gray-400 mb-2">{template.description}</p>
                            <div className="flex flex-wrap gap-1">
                              {template.platforms.map((platform) => (
                                <span
                                  key={platform}
                                  className="px-2 py-0.5 text-xs bg-white/10 rounded"
                                >
                                  {platform}
                                </span>
                              ))}
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* 脚本风格 */}
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        脚本风格
                      </label>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        {[
                          { id: "professional", name: "专业商务", color: "blue" },
                          { id: "casual", name: "轻松亲切", color: "green" },
                          { id: "energetic", name: "活力激情", color: "orange" },
                          { id: "storytelling", name: "故事叙述", color: "purple" },
                        ].map((style) => (
                          <button
                            key={style.id}
                            onClick={() => setVideoScriptStyle(style.id)}
                            className={`p-3 rounded-xl border text-left transition-all ${
                              videoScriptStyle === style.id
                                ? "border-purple-500 bg-purple-500/10"
                                : "border-white/10 bg-white/5 hover:border-white/20"
                            }`}
                          >
                            <p className="text-sm font-medium">{style.name}</p>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* 目标平台 */}
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        目标平台
                      </label>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        {[
                          { id: "youtube", name: "YouTube", icon: "▶️" },
                          { id: "bilibili", name: "Bilibili", icon: "📺" },
                          { id: "douyin", name: "抖音", icon: "🎵" },
                          { id: "xiaohongshu", name: "小红书", icon: "📕" },
                        ].map((platform) => (
                          <button
                            key={platform.id}
                            onClick={() => setVideoTargetPlatform(platform.id)}
                            className={`p-3 rounded-xl border text-left transition-all ${
                              videoTargetPlatform === platform.id
                                ? "border-purple-500 bg-purple-500/10"
                                : "border-white/10 bg-white/5 hover:border-white/20"
                            }`}
                          >
                            <p className="text-lg mb-1">{platform.icon}</p>
                            <p className="text-xs font-medium">{platform.name}</p>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* 视频时长 */}
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        视频时长: {videoTargetDuration}秒
                      </label>
                      <input
                        type="range"
                        min="15"
                        max="180"
                        step="15"
                        value={videoTargetDuration}
                        onChange={(e) => setVideoTargetDuration(parseInt(e.target.value))}
                        className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-purple-500"
                      />
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>15秒</span>
                        <span>60秒</span>
                        <span>120秒</span>
                        <span>180秒</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* 语音类型：音色选择 */}
                {selectedType === "voice" && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-3">
                        选择音色
                      </label>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-60 overflow-y-auto">
                        {voices.map((voice) => (
                          <button
                            key={voice.id}
                            onClick={() => setSelectedVoice(voice.id)}
                            className={`p-3 rounded-xl border text-left transition-all ${
                              selectedVoice === voice.id
                                ? "border-emerald-500 bg-emerald-500/10"
                                : "border-white/10 bg-white/5 hover:border-white/20"
                            }`}
                          >
                            <div className="flex items-center gap-2 mb-1">
                              <span className={`text-xs px-2 py-0.5 rounded ${
                                voice.gender === "male" ? "bg-blue-500/20 text-blue-300" : "bg-pink-500/20 text-pink-300"
                              }`}>
                                {voice.gender === "male" ? "男声" : "女声"}
                              </span>
                              <span className="text-xs text-gray-400 capitalize">{voice.style}</span>
                            </div>
                            <p className="text-sm font-medium">{voice.name}</p>
                            <p className="text-xs text-gray-500">{voice.description}</p>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* 语速调节 */}
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        语速: {voiceSpeed.toFixed(1)}x
                      </label>
                      <input
                        type="range"
                        min="0.5"
                        max="2.0"
                        step="0.1"
                        value={voiceSpeed}
                        onChange={(e) => setVoiceSpeed(parseFloat(e.target.value))}
                        className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                      />
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>慢速 0.5x</span>
                        <span>正常 1.0x</span>
                        <span>快速 2.0x</span>
                      </div>
                    </div>

                    {/* 语音文本输入 */}
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        解说文本 <span className="text-gray-500 text-xs">（可选，默认使用产品描述）</span>
                      </label>
                      <textarea
                        value={voiceText}
                        onChange={(e) => setVoiceText(e.target.value)}
                        placeholder={`在此输入要转换为语音的文本...

或留空使用产品描述：
${productInfo.description || "（请先填写产品描述）"}`}
                        rows={5}
                        className="input-glass resize-none"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        {voiceText.length > 0 ? voiceText.length : productInfo.description.length} / 2000 字符
                      </p>
                    </div>
                  </div>
                )}

                {/* 通用产品信息表单 */}
                {selectedType !== "voice" && (
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        产品名称 <span className="text-red-400">*</span>
                      </label>
                      <input
                        type="text"
                        value={productInfo.name}
                        onChange={(e) => setProductInfo({ ...productInfo, name: e.target.value })}
                        placeholder="例如：AI智能客服助手"
                        className="input-glass"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        产品描述 <span className="text-red-400">*</span>
                      </label>
                      <textarea
                        value={productInfo.description}
                        onChange={(e) => setProductInfo({ ...productInfo, description: e.target.value })}
                        placeholder="简要描述你的产品是什么，解决了什么问题..."
                        rows={4}
                        className="input-glass resize-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        核心功能 <span className="text-gray-500 text-xs">（每行一个）</span>
                      </label>
                      <textarea
                        value={productInfo.features}
                        onChange={(e) => setProductInfo({ ...productInfo, features: e.target.value })}
                        placeholder="智能对话&#10;多语言支持&#10;数据分析"
                        rows={3}
                        className="input-glass resize-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        目标受众
                      </label>
                      <input
                        type="text"
                        value={productInfo.target}
                        onChange={(e) => setProductInfo({ ...productInfo, target: e.target.value })}
                        placeholder="例如：中小企业、开发者、教育机构..."
                        className="input-glass"
                      />
                    </div>
                  </div>
                )}

                <div className="flex justify-between pt-6">
                  <button
                    onClick={() => setStep(1)}
                    className="px-6 py-3 rounded-xl bg-white/5 border border-white/10 text-white font-semibold hover:bg-white/10 transition-colors"
                  >
                    上一步
                  </button>
                  <button
                    onClick={handleGenerate}
                    disabled={
                      (selectedType === "poster" && (!productInfo.name || !productInfo.description)) ||
                      (selectedType === "voice" && !voiceText.trim() && !productInfo.description.trim()) ||
                      (selectedType === "video" && (!productInfo.name || !productInfo.description)) ||
                      isGenerating
                    }
                    className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-blue-500/25 transition-all"
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        {generationStatus?.status === "processing" ? "生成中..." : "排队中..."}
                      </>
                    ) : (
                      <>
                        <Wand2 className="w-5 h-5" />
                        开始生成
                      </>
                    )}
                  </button>
                </div>
              </motion.div>
            )}

            {/* 步骤3: 结果展示 */}
            {step === 3 && generationStatus?.status === "completed" && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="text-center"
              >
                <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-green-500/20 flex items-center justify-center">
                  <Check className="w-8 h-8 text-green-400" />
                </div>
                <h2 className="text-2xl font-bold mb-2">生成完成！</h2>
                <p className="text-gray-400 mb-8">
                  {selectedType === "voice" ? "你的语音解说已生成完毕" : "你的路演海报已生成完毕"}
                </p>

                {/* 视频预览 */}
                {selectedType === "video" && generationStatus.video_url && (
                  <div className="max-w-2xl mx-auto mb-8">
                    <div className="p-6 rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30">
                      <div className="flex items-center gap-3 mb-4">
                        <Video className="w-6 h-6 text-purple-400" />
                        <div className="text-left">
                          <p className="font-medium">视频生成完成</p>
                          <p className="text-sm text-gray-400">
                            时长: {generationStatus.script?.total_duration || "--"} 秒
                          </p>
                        </div>
                      </div>

                      {/* 视频播放器或缩略图 */}
                      <div className="relative rounded-xl overflow-hidden bg-black aspect-video mb-4">
                        {generationStatus?.video_url && (
                          generationStatus.video_url.endsWith('.jpg') || generationStatus.video_url.endsWith('.png') ? (
                            // 显示缩略图（fallback模式）
                            <img
                              src={`${API_BASE_URL.replace("/api/v1", "")}${generationStatus.video_url}`}
                              alt="Video Thumbnail"
                              className="w-full h-full object-contain"
                            />
                          ) : (
                            // 显示视频播放器
                            <video
                              controls
                              className="w-full h-full"
                              src={`${API_BASE_URL.replace("/api/v1", "")}${generationStatus.video_url}`}
                            >
                              你的浏览器不支持视频播放
                            </video>
                          )
                        )}
                      </div>

                      {/* 脚本预览 */}
                      {generationStatus.script && (
                        <div className="mt-4 p-4 rounded-xl bg-white/5">
                          <p className="text-sm font-medium text-gray-300 mb-2">视频脚本预览</p>
                          <div className="space-y-2">
                            {generationStatus.script?.scenes?.slice(0, 3).map((scene: any, idx: number) => (
                              <div key={idx} className="text-xs text-gray-400">
                                <p className="font-medium text-gray-300">场景 {scene.scene_number}</p>
                                <p className="truncate">{scene.subtitle}</p>
                              </div>
                            ))}
                            {(generationStatus.script?.scenes?.length || 0) > 3 && (
                              <p className="text-xs text-gray-500">
                                还有 {(generationStatus.script?.scenes?.length || 0) - 3} 个场景...
                              </p>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* 海报预览 */}
                {selectedType !== "voice" && selectedType !== "video" && (
                  <div className="relative max-w-md mx-auto mb-8">
                    <div className="aspect-[3/4] rounded-2xl overflow-hidden bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-white/10">
                      {generationStatus.preview_url ? (
                        <img
                          src={`${API_BASE_URL.replace("/api/v1", "")}${generationStatus.preview_url}`}
                          alt="Generated Poster"
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <ImageIcon className="w-16 h-16 text-gray-600" />
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* 语音播放器 */}
                {selectedType === "voice" && generationStatus.audio_url && (
                  <div className="max-w-md mx-auto mb-8">
                    <div className="p-6 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-500/30">
                      <div className="flex items-center gap-3 mb-4">
                        <Mic className="w-6 h-6 text-emerald-400" />
                        <div className="text-left">
                          <p className="font-medium">{generationStatus.voice_name || "AI 语音"}</p>
                          <p className="text-sm text-gray-400">
                            预计时长: {generationStatus.duration_estimate?.toFixed(1) || "--"} 秒
                          </p>
                        </div>
                      </div>
                      <audio 
                        controls 
                        className="w-full"
                        src={`${API_BASE_URL.replace("/api/v1", "")}${generationStatus.audio_url}`}
                      >
                        你的浏览器不支持音频播放
                      </audio>
                    </div>
                  </div>
                )}

                {/* 下载按钮 */}
                <div className="flex flex-wrap justify-center gap-4 mb-8">
{selectedType === "video" && generationStatus?.video_url && (
                    <button
                      onClick={() => {
                        const videoUrl = generationStatus?.video_url;
                        if (!videoUrl) return;
                        const fullUrl = `${API_BASE_URL.replace("/api/v1", "")}${videoUrl}`;
                        const link = document.createElement("a");
                        link.href = fullUrl;
                        link.download = `${productInfo.name}_视频.${videoUrl.endsWith('.jpg') ? 'jpg' : 'mp4'}`;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                      }}
                      className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all"
                    >
                      <Download className="w-5 h-5" />
                      <span>下载视频</span>
                    </button>
                  )}
                  {selectedType === "poster" && (
                    <>
                      {generationStatus.download_urls?.png && (
                        <button
                          onClick={() => handleDownload(generationStatus.download_urls.png!, `${productInfo.name}_海报.png`)}
                          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all"
                        >
                          <Download className="w-5 h-5" />
                          <span>下载 PNG</span>
                        </button>
                      )}
                      {generationStatus.download_urls?.jpg && (
                        <button
                          onClick={() => handleDownload(generationStatus.download_urls.jpg!, `${productInfo.name}_海报.jpg`)}
                          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all"
                        >
                          <Download className="w-5 h-5" />
                          <span>下载 JPG</span>
                        </button>
                      )}
                    </>
                  )}
                  {selectedType === "voice" && generationStatus.audio_url && (
                    <button
                      onClick={() => handleDownload(generationStatus.audio_url!, `${productInfo.name || "语音解说"}.mp3`)}
                      className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all"
                    >
                      <Download className="w-5 h-5" />
                      <span>下载 MP3</span>
                    </button>
                  )}
                </div>

                <div className="flex justify-center gap-4">
                  <button
                    onClick={resetForm}
                    className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold hover:shadow-lg hover:shadow-blue-500/25 transition-all"
                  >
                    <RefreshCw className="w-5 h-5" />
                    {selectedType === "voice" ? "生成新的语音" : "生成新的海报"}
                  </button>
                </div>
              </motion.div>
            )}

            {/* 生成失败 */}
            {step === 3 && generationStatus?.status === "failed" && (
              <motion.div
                key="step3-failed"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-center"
              >
                <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-red-500/20 flex items-center justify-center">
                  <span className="text-3xl">😢</span>
                </div>
                <h2 className="text-2xl font-bold mb-2">生成失败</h2>
                <p className="text-gray-400 mb-4">{generationStatus.error_message || "请重试"}</p>
                <button
                  onClick={() => setStep(2)}
                  className="px-6 py-3 rounded-xl bg-white/5 border border-white/10 text-white font-semibold hover:bg-white/10 transition-colors"
                >
                  返回重试
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <Footer />
    </main>
  );
}
