import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "UpThrive — Your next step, made clearer",
  description: "Build a career growth plan around your skills, interests, and goals.",
  icons: { icon: "/mark.svg" }
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
