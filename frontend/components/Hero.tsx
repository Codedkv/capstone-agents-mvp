"use client";
import { useTranslations, useLocale } from "next-intl";
import { routing, useRouter, usePathname, Link } from "@/i18n/routing";

export function Hero() {
  const t = useTranslations("hero");
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const switchTo = (loc: (typeof routing.locales)[number]) => {
    router.replace(pathname, { locale: loc });
  };

  return (
    <section className="min-h-screen flex items-center">
      <div className="pl-[10vw] pr-6 max-w-4xl flex flex-col">
        <div className="font-mono text-[11px] uppercase tracking-[0.15em] flex items-center gap-2">
          <span className="text-[var(--muted)]">{t("brand")}</span>
          <span className="text-[var(--muted)]">·</span>
          {routing.locales.map((loc) => (
            <button
              key={loc}
              type="button"
              onClick={() => switchTo(loc)}
              className={
                "px-2 py-0.5 rounded border transition-colors " +
                (locale === loc
                  ? "border-[rgb(var(--accent-rgb)/0.5)] bg-[rgb(var(--accent-rgb)/0.12)] text-[rgb(var(--accent-rgb))] hover:bg-[rgb(var(--accent-rgb)/0.2)]"
                  : "border-transparent text-[var(--muted)] hover:text-[var(--foreground)]")
              }
            >
              {loc}
            </button>
          ))}
        </div>

        <h1
          className="mt-8 font-medium leading-[1.15]"
          style={{ fontSize: "clamp(36px, 5.5vw, 64px)" }}
        >
          {t("title_line_1")}
          <br />
          <span style={{ color: "var(--accent)" }}>{t("title_line_2")}</span>
        </h1>

        <p
          className="mt-6 font-normal leading-[1.6] text-[var(--muted)] max-w-2xl"
          style={{ fontSize: "clamp(15px, 1.6vw, 18px)" }}
        >
          {t("subtitle")}
        </p>

        <div className="mt-10 flex items-center gap-4">
          <Link href="/app" className="btn-accent">
            {t("cta")}
          </Link>
        </div>

        <p className="mt-12 label-mono">{t("kaggle_note")}</p>
      </div>
    </section>
  );
}
