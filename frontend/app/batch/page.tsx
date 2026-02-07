"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Layers,
  Play,
  Pause,
  Trash2,
  Download,
  Plus,
  Check,
  Clock,
  AlertCircle,
  FileText,
  Video,
  Mic,
  Box,
  RefreshCw
} from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { useBatchGenerate, useBatchStatus, useCancelBatch, useProducts } from "@/hooks/usePitchCube";

interface BatchStatus {
  batch_id: string;
  status: string;
  total: number;
  completed: number;
  progress: number;
  results: Array<{
    type: string;
    status: string;
    url?: string;
    message?: string;
  }>;
}

interface Product {
  id: string;
  name: string;
  description: string;
}

const typeOptions = [
  { id: "poster", name: "海报", icon: FileText, description: "产品宣传海报" },
  { id: "video", name: "视频", icon: Video, description: "产品介绍视频脚本" },
  { id: "voice", name: "语音", icon: Mic, description: "产品宣传语音" },
  { id: "ip", name: "IP", icon: Box, description: "IP形象概念设计" },
];

export default function BatchPage() {
  const [selectedProduct, setSelectedProduct] = useState("");
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [batchId, setBatchId] = useState<string | null>(null);
  const [showConfirm, setShowConfirm] = useState(false);

  const { data: products } = useProducts({ limit: 100 }) as { data: Product[] | undefined };
  const { mutate: generate, isPending } = useBatchGenerate();
  const { data: batchStatus, isFetching: isRefreshing } = useBatchStatus(batchId) as { data: BatchStatus | undefined; isFetching: boolean };
  const { mutate: cancel } = useCancelBatch();

  const handleTypeToggle = (typeId: string) => {
    setSelectedTypes(prev =>
      prev.includes(typeId)
        ? prev.filter(t => t !== typeId)
        : [...prev, typeId]
    );
  };

  const handleGenerate = () => {
    if (!selectedProduct || selectedTypes.length === 0) return;
    setShowConfirm(true);
  };

  const confirmGenerate = () => {
    generate(
      {
        product_id: selectedProduct,
        types: selectedTypes,
        options: {},
      },
      {
        onSuccess: (data: any) => {
          setBatchId(data.batch_id);
          setShowConfirm(false);
        },
      }
    );
  };

  const handleCancel = () => {
    if (batchId) {
      cancel(batchId);
      setBatchId(null);
    }
  };

  const getStatusIcon = () => {
    if (!batchStatus) return <Clock className="w-5 h-5 text-gray-400" />;
    switch (batchStatus.status) {
      case 'completed':
        return <Check className="w-5 h-5 text-green-400" />;
      case 'processing':
        return <RefreshCw className="w-5 h-5 text-blue-400 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      default:
        return <Clock className="w-5 h-5 text-yellow-400" />;
    }
  };

  const getStatusText = () => {
    if (!batchStatus) return '等待开始';
    switch (batchStatus.status) {
      case 'completed':
        return '全部完成';
      case 'processing':
        return `处理中 (${batchStatus.completed}/${batchStatus.total})`;
      case 'failed':
        return '部分失败';
      case 'pending':
        return '等待处理';
      default:
        return batchStatus.status;
    }
  };

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
              <Layers className="inline-block w-8 h-8 mr-2 text-blue-500" />
              批量生成
            </h1>
            <p className="text-gray-400">一次选择多个资产类型，快速生成完整的产品宣传材料</p>
          </motion.div>

          {!batchId ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-[#12121a] rounded-2xl border border-white/10 p-6 mb-6"
            >
              <h2 className="text-xl font-semibold text-white mb-4">选择产品</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {products?.map((product: any) => (
                  <button
                    key={product.id}
                    onClick={() => setSelectedProduct(product.id)}
                    className={`p-4 rounded-xl text-left transition-all ${
                      selectedProduct === product.id
                        ? 'bg-blue-500/20 border-2 border-blue-500'
                        : 'bg-white/5 border-2 border-transparent hover:border-white/20'
                    }`}
                  >
                    <div className="font-medium text-white">{product.name}</div>
                    <div className="text-sm text-gray-400 truncate">{product.description}</div>
                  </button>
                ))}
              </div>
            </motion.div>
          ) : null}

          {!batchId ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-[#12121a] rounded-2xl border border-white/10 p-6 mb-6"
            >
              <h2 className="text-xl font-semibold text-white mb-4">选择生成类型</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {typeOptions.map((type) => {
                  const Icon = type.icon;
                  const isSelected = selectedTypes.includes(type.id);
                  return (
                    <button
                      key={type.id}
                      onClick={() => handleTypeToggle(type.id)}
                      className={`p-4 rounded-xl text-center transition-all ${
                        isSelected
                          ? 'bg-blue-500/20 border-2 border-blue-500'
                          : 'bg-white/5 border-2 border-transparent hover:border-white/20'
                      }`}
                    >
                      <Icon className={`w-8 h-8 mx-auto mb-2 ${isSelected ? 'text-blue-400' : 'text-gray-400'}`} />
                      <div className="font-medium text-white">{type.name}</div>
                      <div className="text-xs text-gray-400">{type.description}</div>
                    </button>
                  );
                })}
              </div>
            </motion.div>
          ) : null}

          {batchId ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-[#12121a] rounded-2xl border border-white/10 p-6 mb-6"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  {getStatusIcon()}
                  <div>
                    <div className="font-medium text-white">{getStatusText()}</div>
                    <div className="text-sm text-gray-400">Batch ID: {batchId}</div>
                  </div>
                </div>
                <button
                  onClick={handleCancel}
                  className="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors"
                >
                  取消任务
                </button>
              </div>

              <div className="space-y-3">
                {batchStatus?.results?.map((result: any, index: number) => {
                  const typeInfo = typeOptions.find(t => t.id === result.type);
                  const Icon = typeInfo?.icon || FileText;
                  return (
                    <div
                      key={index}
                      className={`p-4 rounded-xl flex items-center justify-between ${
                        result.status === 'completed'
                          ? 'bg-green-500/10 border border-green-500/20'
                          : result.status === 'failed'
                          ? 'bg-red-500/10 border border-red-500/20'
                          : 'bg-blue-500/10 border border-blue-500/20'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <Icon className={`w-5 h-5 ${
                          result.status === 'completed'
                            ? 'text-green-400'
                            : result.status === 'failed'
                            ? 'text-red-400'
                            : 'text-blue-400'
                        }`} />
                        <div>
                          <div className="font-medium text-white">{typeInfo?.name}</div>
                          <div className="text-sm text-gray-400">{result.message || result.status}</div>
                        </div>
                      </div>
                      {result.status === 'completed' && result.url && (
                        <a
                          href={result.url}
                          download
                          className="p-2 bg-blue-500/20 text-blue-400 rounded-lg hover:bg-blue-500/30 transition-colors"
                        >
                          <Download className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                  );
                })}
              </div>
            </motion.div>
          ) : null}

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex justify-end gap-4"
          >
            {batchId ? (
              <button
                onClick={() => {
                  setBatchId(null);
                  setSelectedTypes([]);
                  setSelectedProduct("");
                }}
                className="px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
              >
                开始新任务
              </button>
            ) : (
              <>
                <button
                  onClick={() => {
                    setSelectedProduct("");
                    setSelectedTypes([]);
                  }}
                  className="px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
                >
                  重置选择
                </button>
                <button
                  onClick={handleGenerate}
                  disabled={!selectedProduct || selectedTypes.length === 0 || isPending}
                  className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {isPending ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      提交中...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      开始批量生成
                    </>
                  )}
                </button>
              </>
            )}
          </motion.div>
        </div>
      </main>

      <Footer />

      {showConfirm && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-[#1a1a24] rounded-2xl border border-white/10 p-6 max-w-md mx-4"
          >
            <h3 className="text-xl font-semibold text-white mb-4">确认批量生成</h3>
            <div className="space-y-2 mb-6">
              <div className="text-gray-400">
                产品: <span className="text-white">
                  {products?.find((p: any) => p.id === selectedProduct)?.name}
                </span>
              </div>
              <div className="text-gray-400">
                将生成: <span className="text-white">
                  {selectedTypes.map(t => typeOptions.find(x => x.id === t)?.name).join(', ')}
                </span>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowConfirm(false)}
                className="flex-1 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
              >
                取消
              </button>
              <button
                onClick={confirmGenerate}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors"
              >
                确认生成
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
