/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: [
      "files.hosting.thmanyah.com",
      "ssl-static.libsyn.com",
      "media.rss.com",
      "pbcdn1.podbean.com",
      "cdn.transistor.fm",
      "storage.buzzsprout.com",
      "images.megaphone.fm",
      "assets.pippa.io",
      "feeds.soundcloud.com",
      "d3t3ozftmdmh3i.cloudfront.net",
      "i1.sndcdn.com",
      "media.blubrry.com",
      "content.production.cdn.art19.com",
      "chrt.fm",
      "pdst.fm",
      "traffic.omny.fm",
      "image.simplecastcdn.com",
    ],
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },
};

module.exports = nextConfig;
