import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "ratemyNUS",
  description: "2-minute course reviews for NUS students",
  openGraph: {
    title: "ratemyNUS",
    description: "2-minute course reviews for NUS students",
    siteName: "ratemyNUS",
    locale: "en_SG",
    type: "website",
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        {children}
      </body>
    </html>
  );
}