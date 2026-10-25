"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/** Strips YAML frontmatter (between the first two --- lines) from markdown. */
export function stripFrontmatter(markdown: string): string {
  if (!markdown.startsWith("---")) return markdown;
  const end = markdown.indexOf("---", 3);
  if (end === -1) return markdown;
  return markdown.slice(end + 3).replace(/^\s+/, "");
}

export function Markdown({ children }: { children: string }) {
  return (
    <div className="docs-prose">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1 className="font-serif text-3xl font-bold mt-2 mb-4 tracking-tight">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="font-serif text-xl font-bold mt-8 mb-3 pb-1.5 border-b border-stone-200 dark:border-stone-800">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="font-serif text-base font-bold mt-6 mb-2">{children}</h3>
          ),
          p: ({ children }) => <p className="my-3 leading-7 text-[15px]">{children}</p>,
          ul: ({ children }) => <ul className="my-3 ml-5 list-disc space-y-1.5 text-[15px] leading-7">{children}</ul>,
          ol: ({ children }) => <ol className="my-3 ml-5 list-decimal space-y-1.5 text-[15px] leading-7">{children}</ol>,
          li: ({ children }) => <li className="pl-1">{children}</li>,
          a: ({ href, children }) => {
            const external = href?.startsWith("http");
            return external ? (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer nofollow"
                className="text-green-800 dark:text-green-400 underline underline-offset-2"
              >
                {children}
              </a>
            ) : (
              <span className="text-foreground">{children}</span>
            );
          },
          code: ({ className: cls, children }) => {
            const isBlock = cls?.includes("language-");
            if (isBlock) {
              return (
                <code className="font-mono text-[13px] text-stone-100">{children}</code>
              );
            }
            return (
              <code className="font-mono text-[13px] bg-stone-100 dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded px-1.5 py-0.5">
                {children}
              </code>
            );
          },
          pre: ({ children }) => (
            <pre className="my-4 rounded-md bg-stone-900 dark:bg-stone-950 border border-stone-700 p-4 overflow-x-auto">
              {children}
            </pre>
          ),
          table: ({ children }) => (
            <div className="my-4 overflow-x-auto rounded-md border border-stone-200 dark:border-stone-800">
              <table className="w-full text-sm">{children}</table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-stone-100 dark:bg-stone-800/70">{children}</thead>
          ),
          th: ({ children }) => (
            <th className="px-3 py-2 text-left font-semibold border-b border-stone-200 dark:border-stone-800">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-3 py-2 align-top border-b border-stone-100 dark:border-stone-800/60 leading-6">
              {children}
            </td>
          ),
          blockquote: ({ children }) => (
            <blockquote className="my-4 pl-4 border-l-4 border-stone-300 dark:border-stone-700 text-muted-foreground">
              {children}
            </blockquote>
          ),
          hr: () => <hr className="my-6 border-stone-200 dark:border-stone-800" />,
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}
