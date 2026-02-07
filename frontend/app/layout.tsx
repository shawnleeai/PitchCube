import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/components/QueryProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PitchCube - AI驱动的路演展示智能魔方",
  description: "为黑客松团队和初创公司自动生成专业展示物料，包括海报、视频脚本、3D打印IP形象和智能语音讲解。",
  keywords: ["AI", "路演", "展示", "海报生成", "视频生成", "黑客松", "初创公司"],
  authors: [{ name: "PitchCube Team" }],
  openGraph: {
    title: "PitchCube - 路演魔方",
    description: "AI驱动的路演展示智能魔方平台",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" className="dark">
      <body className={`${inter.className} antialiased`}>
        <QueryProvider>
          {children}
        </QueryProvider>
      </body>
    </html>
  );
}
