import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "당신의 마흔 번째 계절",
  description: "세상에서 단 한 사람을 위한 마흔 번째 생일 편지",
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
