"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export const dynamic = "force-dynamic";
export default function StudioHome() {
  const router = useRouter();
  
  useEffect(() => {
    // Generate a random thread ID and redirect
    const threadId = Math.random().toString(36).substring(2, 9);
    router.push(`/studio/${threadId}`);
  }, [router]);
  
  return (
    <section style={{ border: "1px dashed #2a2f37", borderRadius: 16, padding: 16, minHeight: 480 }}>
      <h2>Canvas</h2>
      <p style={{ opacity: 0.7 }}>Redirecting to new thread...</p>
    </section>
  );
}