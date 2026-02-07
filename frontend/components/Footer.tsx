"use client";

import { Sparkles, Github, Twitter, Linkedin, Mail } from "lucide-react";
import Link from "next/link";

const footerLinks = {
  product: {
    title: "产品",
    links: [
      { name: "海报工坊", href: "/generate?type=poster" },
      { name: "视频演播室", href: "/generate?type=video" },
      { name: "IP铸造厂", href: "/generate?type=3d" },
      { name: "定价", href: "/pricing" },
    ],
  },
  resources: {
    title: "资源",
    links: [
      { name: "使用文档", href: "/docs" },
      { name: "API文档", href: "/docs/api" },
      { name: "示例模板", href: "/templates" },
      { name: "更新日志", href: "/changelog" },
    ],
  },
  company: {
    title: "公司",
    links: [
      { name: "关于我们", href: "/about" },
      { name: "博客", href: "/blog" },
      { name: "加入我们", href: "/careers" },
      { name: "联系我们", href: "/contact" },
    ],
  },
  legal: {
    title: "法律",
    links: [
      { name: "隐私政策", href: "/privacy" },
      { name: "服务条款", href: "/terms" },
      { name: "Cookie政策", href: "/cookies" },
    ],
  },
};

const socialLinks = [
  { icon: Github, href: "https://github.com/yourusername/pitchcube", label: "GitHub" },
  { icon: Twitter, href: "https://twitter.com/pitchcube", label: "Twitter" },
  { icon: Linkedin, href: "https://linkedin.com/company/pitchcube", label: "LinkedIn" },
  { icon: Mail, href: "mailto:hello@pitchcube.app", label: "Email" },
];

export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-[#0a0a0f]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-2 md:grid-cols-6 gap-8 lg:gap-12">
          {/* Brand */}
          <div className="col-span-2">
            <Link href="/" className="flex items-center gap-2 mb-6">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold gradient-text">PitchCube</span>
            </Link>
            <p className="text-gray-400 text-sm mb-6 max-w-xs">
              AI驱动的路演展示智能魔方平台，为黑客松团队和初创公司提供专业展示物料生成服务。
            </p>
            <div className="flex items-center gap-4">
              {socialLinks.map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
                  aria-label={social.label}
                >
                  <social.icon className="w-5 h-5" />
                </a>
              ))}
            </div>
          </div>

          {/* Links */}
          {Object.values(footerLinks).map((section) => (
            <div key={section.title}>
              <h3 className="text-sm font-semibold text-white mb-4">{section.title}</h3>
              <ul className="space-y-3">
                {section.links.map((link) => (
                  <li key={link.name}>
                    <Link
                      href={link.href}
                      className="text-sm text-gray-400 hover:text-white transition-colors"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom */}
        <div className="border-t border-white/10 mt-12 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-gray-500">
            © {new Date().getFullYear()} PitchCube. All rights reserved.
          </p>
          <p className="text-sm text-gray-500">
            Made with ❤️ for hackers and startups
          </p>
        </div>
      </div>
    </footer>
  );
}
