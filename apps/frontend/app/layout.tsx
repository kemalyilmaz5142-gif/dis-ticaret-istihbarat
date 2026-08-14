import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Dış Ticaret İstihbarat",
  description: "Potansiyel yurt dışı müşterileri bulma platformu"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="tr" suppressHydrationWarning>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
