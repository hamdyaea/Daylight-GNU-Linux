// Hamdy Abou El Anein — info@daylightlinux.ch
// Normalise public HTML URLs; leave preview hosts and static assets unchanged.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (["daylightlinux.ch", "www.daylightlinux.ch"].includes(url.hostname)) {
      const target = new URL(url);
      target.protocol = "https:";
      target.hostname = "daylightlinux.ch";
      target.port = "";
      if (target.pathname.endsWith("/index.html")) {
        target.pathname = target.pathname.slice(0, -"index.html".length);
      } else if (target.pathname.endsWith(".html")) {
        target.pathname = target.pathname.slice(0, -".html".length);
      }
      if (target.href !== url.href) {
        return new Response(null, {status: 301, headers: {
          Location: target.href,
          "Cache-Control": "public, max-age=300",
          "X-Content-Type-Options": "nosniff"
        }});
      }
    }
    return env.ASSETS.fetch(request);
  }
};
