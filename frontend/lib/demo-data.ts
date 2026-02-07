// 演示数据 - 用于黑客松快速展示

export interface DemoProduct {
  name: string;
  description: string;
  features: string;
  target: string;
  template: string;
}

export const demoProducts: DemoProduct[] = [
  {
    name: "PitchCube",
    description: "AI驱动的路演展示自动化平台，帮助黑客松团队和初创公司在10秒内生成专业路演物料，节省90%的设计时间。",
    features: "智能海报生成\n视频脚本创作\n多平台格式适配\n一键导出下载",
    target: "黑客松团队、初创公司、独立开发者",
    template: "tech-modern"
  },
  {
    name: "智链Supply",
    description: "基于区块链的供应链溯源平台，让每一件商品从生产到消费的全流程透明可追溯，保障食品安全。",
    features: "区块链存证\nQR码溯源\n智能合约结算\n数据分析看板",
    target: "食品企业、零售商、消费者",
    template: "startup-bold"
  },
  {
    name: "MindfulAI",
    description: "AI心理健康助手，通过自然语言对话识别情绪状态，提供个性化的心理疏导和正念训练。",
    features: "情绪识别\n语音对话\n正念训练\n个性化建议",
    target: "职场人士、学生、焦虑人群",
    template: "creative-gradient"
  },
  {
    name: "GreenEnergy",
    description: "分布式能源管理平台，帮助家庭和企业实时监控能源消耗，优化用电策略，降低碳排放。",
    features: "实时监控\nAI节能建议\n碳足迹追踪\n智能家居联动",
    target: "家庭用户、企业、园区",
    template: "minimal-clean"
  }
];

// 快速填充函数
export function fillDemoData(index: number): DemoProduct {
  return demoProducts[index % demoProducts.length];
}
