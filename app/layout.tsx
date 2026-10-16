import type { Metadata } from "next";
import "./globals.css";

const title = "당신의 마흔 번째 계절";
const description = "마흔 개의 별, 여섯 고양이, 촛불과 1분 영화로 전하는 특별한 생일 편지";
const publicOrigin = process.env.NEXT_PUBLIC_SITE_URL ?? "https://jbh-mine.github.io/birthday_event_card/";
const socialImage = new URL("og.png", publicOrigin.endsWith("/") ? publicOrigin : `${publicOrigin}/`).href;

export const metadata: Metadata = {
  metadataBase: new URL(publicOrigin),
  title,
  description,
  icons: { icon: "/favicon.svg" },
  openGraph: {
    title: `${title} | Forty & Forever`,
    description,
    type: "website",
    locale: "ko_KR",
    url: publicOrigin,
    images: [{ url: socialImage, width: 1536, height: 1024, alt: "하트 별자리와 촛불로 표현한 마흔 번째 생일 축하 카드" }],
  },
  twitter: {
    card: "summary_large_image",
    title: `${title} | Forty & Forever`,
    description,
    images: [socialImage],
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
