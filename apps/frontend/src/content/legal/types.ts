export type Inline =
  | { kind: "text"; text: string }
  | { kind: "link"; href: string; label: string };

export type Block =
  | { kind: "p"; parts: Inline[] }
  | { kind: "ul"; items: string[] };

export type LegalSection = {
  id: string;
  heading: string;
  blocks: Block[];
};

export type LegalDocumentCopy = {
  title: string;
  description: string;
  updated: string;
  sections: LegalSection[];
};

export type LegalPageId = "privacy" | "terms" | "security";

export type LegalPack = {
  navLabel: string;
  welcomeLabel: string;
  nav: Record<LegalPageId, string>;
  pages: Record<LegalPageId, LegalDocumentCopy>;
};
