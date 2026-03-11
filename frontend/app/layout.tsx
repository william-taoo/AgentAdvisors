import React from "react";

export const metadata = {
  title: "AgentAdvisors",
  description: "Financial multi-agent dashboard"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

