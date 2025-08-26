// path: web/provenance-client.js
export async function openProvenance(sha, { baseUrl = "", filename = null, purpose = null, userId = null } = {}) {
  const headers = {};
  if (userId) headers["x-user-id"] = userId;
  const qs = new URLSearchParams();
  if (filename) qs.set("filename", filename);
  if (purpose) qs.set("purpose", purpose);

  // 1) fetch link (also emits signed "link_issued" receipt server-side)
  const linkResp = await fetch(`${baseUrl}/provenance/${encodeURIComponent(sha)}/link?${qs.toString()}`, { headers });
  if (!linkResp.ok) {
    const err = await linkResp.text();
    throw new Error(`Failed to get link: ${err}`);
  }
  const data = await linkResp.json();
  const { url } = data.link;

  // 2) open in a new tab (or download via programmatic click)
  const a = document.createElement("a");
  a.href = url;
  a.target = "_blank";
  a.rel = "noopener";
  a.click();

  // 3) best-effort ack back to the server (signed "view_ack" receipt)
  try {
    await fetch(`${baseUrl}/provenance/${encodeURIComponent(sha)}/receipt`, {
      method: "POST",
      headers: { "content-type": "application/json", ...headers },
      body: JSON.stringify({ event: "view_ack", purpose, extras: { from: "web_client" } })
    });
  } catch (e) {
    // swallow; ack is best-effort
  }

  return data;
}
