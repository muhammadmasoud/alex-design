import { useEffect } from "react";

interface SEOProps {
  title: string;
  description?: string;
  canonical?: string;
  keywords?: string;
  ogImage?: string;
  ogType?: string;
  structuredData?: object;
}

export const SEO = ({ 
  title, 
  description, 
  canonical, 
  keywords,
  ogImage = "/placeholder.svg",
  ogType = "website",
  structuredData 
}: SEOProps) => {
  useEffect(() => {
    // Update page title
    document.title = title;

    const setMeta = (name: string, content: string, isProperty = false) => {
      const attribute = isProperty ? "property" : "name";
      let el = document.querySelector(`meta[${attribute}="${name}"]`) as HTMLMetaElement | null;
      if (!el) {
        el = document.createElement("meta");
        el.setAttribute(attribute, name);
        document.head.appendChild(el);
      }
      el.setAttribute("content", content);
    };

    // Basic meta tags
    if (description) {
      setMeta("description", description);
      setMeta("og:description", description, true);
      setMeta("twitter:description", description, true);
    }

    if (keywords) {
      setMeta("keywords", keywords);
    }

    // Open Graph tags
    setMeta("og:title", title, true);
    setMeta("og:type", ogType, true);
    setMeta("og:image", `https://alxdesigns.net${ogImage}`, true);
    setMeta("og:url", `https://alxdesigns.net${canonical || window.location.pathname}`, true);

    // Twitter Card tags
    setMeta("twitter:card", "summary_large_image", true);
    setMeta("twitter:title", title, true);
    setMeta("twitter:image", `https://alxdesigns.net${ogImage}`, true);

    // Canonical URL
    if (canonical) {
      let link = document.querySelector('link[rel="canonical"]') as HTMLLinkElement | null;
      if (!link) {
        link = document.createElement("link");
        link.setAttribute("rel", "canonical");
        document.head.appendChild(link);
      }
      link.setAttribute("href", `https://alxdesigns.net${canonical}`);
    }

    // Structured Data
    if (structuredData) {
      let script = document.querySelector('script[type="application/ld+json"]') as HTMLScriptElement | null;
      if (!script) {
        script = document.createElement("script");
        script.setAttribute("type", "application/ld+json");
        document.head.appendChild(script);
      }
      script.textContent = JSON.stringify(structuredData);
    }
  }, [title, description, canonical, keywords, ogImage, ogType, structuredData]);

  return null;
};

export default SEO;
