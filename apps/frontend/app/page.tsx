"use client";

import { FormEvent, useEffect, useState } from "react";

type LeadResult = {
  company_name: string;
  country: string;
  city?: string | null;
  address?: string | null;
  website?: string | null;
  email?: string | null;
  phone?: string | null;
  source: string;
  source_type: string;
  matched_keyword?: string | null;
  site_category: string;
  site_category_reason?: string | null;
  score: number;
  notes?: string | null;
  ai_fit_reason?: string | null;
  suggested_contact_role?: string | null;
  suggested_contact_emails: string[];
  suggested_email_subject?: string | null;
  suggested_email_body?: string | null;
};

type SearchQueryPlanItem = {
  engine: string;
  language: string;
  query: string;
  target_country: string;
  country_domain?: string | null;
  source_type: string;
};

type SearchResponse = {
  request_id: string;
  status: string;
  query_plan: SearchQueryPlanItem[];
  results: LeadResult[];
};

type ImageUploadResponse = {
  image_id: string;
  filename: string;
  content_type?: string | null;
  size_bytes: number;
  sha256: string;
  status: string;
};

type ModuleInfo = {
  code: string;
  name: string;
  description: string;
  setup_price_usd: number;
  monthly_price_usd: number;
  enabled: boolean;
};

type SubscriptionPlan = {
  plan_code: string;
  customer_name: string;
  enabled_modules: string[];
  monthly_query_limit: number;
  used_queries: number;
};

type CustomerProfile = {
  customer_name: string;
  company_name: string;
  website?: string | null;
  catalog_url?: string | null;
  default_sender_email?: string | null;
  target_sector?: string | null;
  profile_products: ProfileProduct[];
  reference_websites: string[];
  potential_customer_websites: string[];
  customer_product_terms: string[];
  excluded_product_terms: string[];
};

type ProfileProduct = {
  name_tr: string;
  name_en: string;
  hs_code: string;
  image_url?: string | null;
};

type IntegrationStatus = {
  code: string;
  name: string;
  status: string;
  detail: string;
};

type SystemStatus = {
  app_name: string;
  app_env: string;
  integrations: IntegrationStatus[];
};

type SearchHistoryItem = {
  request_id: string;
  status: string;
  target_country: string;
  product_name?: string | null;
  result_count: number;
  created_at: string;
};

type VisitorRecord = {
  visitor_id: string;
  consent: boolean;
  country?: string | null;
  city?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  ip_address?: string | null;
  company_guess?: string | null;
  isp?: string | null;
  organization?: string | null;
  lookup_confidence: number;
  lookup_method: string;
  page_url?: string | null;
  notification_title?: string;
  notification_message?: string | null;
  created_at: string;
};

type CampaignPreview = {
  subject: string;
  body: string;
  recipients: Array<{
    company_name: string;
    email: string;
    role?: string | null;
    source: string;
  }>;
  spam_risk_score: number;
  spam_warnings: string[];
  status: string;
};

type CampaignJob = {
  campaign_id: string;
  subject: string;
  recipient_count: number;
  spam_risk_score: number;
  status: string;
  send_enabled: boolean;
  queued_at: string;
  batches: number;
  warnings: string[];
};

type FairParticipantResult = {
  company_name: string;
  country: string;
  city?: string | null;
  booth?: string | null;
  website?: string | null;
  email?: string | null;
  matched_terms: string[];
  score: number;
  source: string;
  notes?: string | null;
};

type FairScanResponse = {
  request_id: string;
  status: string;
  fair_name: string;
  target_country: string;
  participants: FairParticipantResult[];
  created_at: string;
};

type ChatResponse = {
  reply: string;
  suggestions: Array<{
    title: string;
    detail: string;
  }>;
  status: string;
};

type DictionaryValidationResponse = {
  items: Array<{
    term: string;
    normalized_term: string;
    status: string;
    sources_checked: string[];
    suggestion?: string | null;
  }>;
};

type RfqScanResponse = {
  status: string;
  opportunities: Array<{
    platform: string;
    title: string;
    buyer_country: string;
    quantity_hint?: string | null;
    contact_hint?: string | null;
    score: number;
    source_url: string;
    notes: string;
  }>;
};

type DemandShareJob = {
  share_id: string;
  product_name: string;
  target_markets: string[];
  channels: string[];
  status: string;
  queued_at: string;
  notes: string;
};

type TrainingLesson = {
  lesson_id: string;
  title: string;
  duration_minutes: number;
  required_score: number;
};

type TrainingQuizResult = {
  employee_name: string;
  lesson_id: string;
  score: number;
  passed: boolean;
  status: string;
};

type WidgetLeadRecord = {
  visitor_email?: string | null;
  visitor_phone?: string | null;
  message: string;
  page_url?: string | null;
  language: string;
};

type WidgetMessageResponse = {
  reply: string;
  next_question: string;
  lead_captured: boolean;
};

type LoginResponse = {
  authenticated: boolean;
  username: string;
  customer_name: string;
  token: string;
  reason: string;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

type DashboardTab = "pricing" | "search" | "operations" | "fairs" | "demand" | "training" | "widget" | "results";
type ResultSiteFilter = "all" | "ecommerce" | "company_website" | "search_page";

const dashboardTabs: Array<{ id: DashboardTab; label: string; hint: string }> = [
  { id: "pricing", label: "Ücretlendirme", hint: "Modüller ve paketler" },
  { id: "search", label: "Arama", hint: "Müşteri bulma" },
  { id: "operations", label: "Operasyon", hint: "Profil ve durum" },
  { id: "fairs", label: "Fuarlar", hint: "Katılımcı tarama" },
  { id: "demand", label: "Talepler", hint: "RFQ ve kampanya" },
  { id: "training", label: "Eğitim", hint: "Personel takibi" },
  { id: "widget", label: "Widget", hint: "Web lead toplama" },
  { id: "results", label: "Sonuçlar", hint: "Excel ve AI" }
];

function splitList(value: FormDataEntryValue | null): string[] {
  return String(value ?? "")
    .split(/[\n,]+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function joinList(items?: string[] | null): string {
  return (items ?? []).join("\n");
}

function profileProductTerms(profile?: CustomerProfile | null): string[] {
  return (profile?.profile_products ?? [])
    .flatMap((product) => [product.name_tr, product.name_en, product.hs_code ? `HS Code ${product.hs_code}` : ""])
    .map((item) => item.trim())
    .filter(Boolean);
}

function parseProfileProducts(form: FormData): ProfileProduct[] {
  return [0, 1, 2]
    .map((index) => ({
      name_tr: String(form.get(`profile_product_name_tr_${index}`) ?? "").trim(),
      name_en: String(form.get(`profile_product_name_en_${index}`) ?? "").trim(),
      hs_code: String(form.get(`profile_product_hs_code_${index}`) ?? "").trim(),
      image_url: String(form.get(`profile_product_image_url_${index}`) ?? "").trim() || null
    }))
    .filter((product) => product.name_tr || product.name_en || product.hs_code || product.image_url);
}

export default function HomePage() {
  const [isMounted, setIsMounted] = useState(false);
  const [session, setSession] = useState<LoginResponse | null>(null);
  const [activeTab, setActiveTab] = useState<DashboardTab>("search");
  const [resultSiteFilter, setResultSiteFilter] = useState<ResultSiteFilter>("all");
  const [results, setResults] = useState<LeadResult[]>([]);
  const [lastSearch, setLastSearch] = useState<SearchResponse | null>(null);
  const [modules, setModules] = useState<ModuleInfo[]>([]);
  const [subscription, setSubscription] = useState<SubscriptionPlan | null>(null);
  const [profile, setProfile] = useState<CustomerProfile | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [history, setHistory] = useState<SearchHistoryItem[]>([]);
  const [visitors, setVisitors] = useState<VisitorRecord[]>([]);
  const [productImage, setProductImage] = useState<ImageUploadResponse | null>(null);
  const [campaign, setCampaign] = useState<CampaignPreview | null>(null);
  const [campaignJobs, setCampaignJobs] = useState<CampaignJob[]>([]);
  const [fairScan, setFairScan] = useState<FairScanResponse | null>(null);
  const [rfqScan, setRfqScan] = useState<RfqScanResponse | null>(null);
  const [demandShares, setDemandShares] = useState<DemandShareJob[]>([]);
  const [trainingLessons, setTrainingLessons] = useState<TrainingLesson[]>([]);
  const [trainingResults, setTrainingResults] = useState<TrainingQuizResult[]>([]);
  const [lastTrainingResult, setLastTrainingResult] = useState<TrainingQuizResult | null>(null);
  const [widgetLeads, setWidgetLeads] = useState<WidgetLeadRecord[]>([]);
  const [widgetReply, setWidgetReply] = useState<WidgetMessageResponse | null>(null);
  const [chatAnswer, setChatAnswer] = useState<ChatResponse | null>(null);
  const [dictionaryValidation, setDictionaryValidation] = useState<DictionaryValidationResponse | null>(null);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [isWidgetLoading, setIsWidgetLoading] = useState(false);
  const [isFairLoading, setIsFairLoading] = useState(false);
  const [isRfqLoading, setIsRfqLoading] = useState(false);
  const [isLoginLoading, setIsLoginLoading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!isMounted) {
      return;
    }
    const savedSession = window.localStorage.getItem("trade_session");
    if (savedSession) {
      setSession(JSON.parse(savedSession) as LoginResponse);
    }
  }, [isMounted]);

  useEffect(() => {
    if (!session?.authenticated) {
      return;
    }

    async function loadModules() {
      try {
        const [modulesResponse, subscriptionResponse, profileResponse, systemResponse, historyResponse, visitorsResponse, campaignsResponse, demandSharesResponse, lessonsResponse, trainingResultsResponse, widgetLeadsResponse] = await Promise.all([
          fetch(`${apiUrl}/modules`),
          fetch(`${apiUrl}/subscription`),
          fetch(`${apiUrl}/customer/profile`),
          fetch(`${apiUrl}/system/status`),
          fetch(`${apiUrl}/searches/history`),
          fetch(`${apiUrl}/visitors`),
          fetch(`${apiUrl}/campaigns`),
          fetch(`${apiUrl}/demand-shares`),
          fetch(`${apiUrl}/training/lessons`),
          fetch(`${apiUrl}/training/results`),
          fetch(`${apiUrl}/widget/leads`)
        ]);
        if (!modulesResponse.ok || !subscriptionResponse.ok) {
          return;
        }
        setModules((await modulesResponse.json()) as ModuleInfo[]);
        setSubscription((await subscriptionResponse.json()) as SubscriptionPlan);
        if (profileResponse.ok) {
          setProfile((await profileResponse.json()) as CustomerProfile);
        }
        if (systemResponse.ok) {
          setSystemStatus((await systemResponse.json()) as SystemStatus);
        }
        if (historyResponse.ok) {
          setHistory((await historyResponse.json()) as SearchHistoryItem[]);
        }
        if (visitorsResponse.ok) {
          setVisitors((await visitorsResponse.json()) as VisitorRecord[]);
        }
        if (campaignsResponse.ok) {
          setCampaignJobs((await campaignsResponse.json()) as CampaignJob[]);
        }
        if (demandSharesResponse.ok) {
          setDemandShares((await demandSharesResponse.json()) as DemandShareJob[]);
        }
        if (lessonsResponse.ok) {
          setTrainingLessons((await lessonsResponse.json()) as TrainingLesson[]);
        }
        if (trainingResultsResponse.ok) {
          setTrainingResults((await trainingResultsResponse.json()) as TrainingQuizResult[]);
        }
        if (widgetLeadsResponse.ok) {
          setWidgetLeads((await widgetLeadsResponse.json()) as WidgetLeadRecord[]);
        }
      } catch {
        setModules([]);
      }
    }

    loadModules();
  }, [session]);

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoginLoading(true);
    setError(null);

    const form = new FormData(event.currentTarget);
    const response = await fetch(`${apiUrl}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: String(form.get("username") ?? ""),
        password: String(form.get("password") ?? "")
      })
    });

    if (response.ok) {
      const data = (await response.json()) as LoginResponse;
      if (data.authenticated) {
        setSession(data);
        window.localStorage.setItem("trade_session", JSON.stringify(data));
      } else {
        setError(data.reason);
      }
    } else {
      setError("Giriş servisine ulaşılamadı.");
    }

    setIsLoginLoading(false);
  }

  function logout() {
    window.localStorage.removeItem("trade_session");
    setSession(null);
    setResults([]);
    setLastSearch(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError(null);

    const form = new FormData(event.currentTarget);
    const file = form.get("product_image");
    let productImageId = productImage?.image_id ?? null;

    if (file instanceof File && file.size > 0) {
      productImageId = await uploadProductImage(file);
    }

    const payload = {
      target_country: String(form.get("target_country") ?? ""),
      country_domain: String(form.get("country_domain") ?? ""),
      product_name_tr: String(form.get("product_name_tr") ?? ""),
      product_name_en: String(form.get("product_name_en") ?? ""),
      product_name_es: String(form.get("product_name_es") ?? ""),
      product_name_ru: String(form.get("product_name_ru") ?? ""),
      product_name_ar: String(form.get("product_name_ar") ?? ""),
      product_name_fr: String(form.get("product_name_fr") ?? ""),
      product_name_de: String(form.get("product_name_de") ?? ""),
      hs_code: String(form.get("hs_code") ?? ""),
      oem_no: String(form.get("oem_no") ?? ""),
      competitors: String(form.get("competitors") ?? "")
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      related_sectors: String(form.get("related_sectors") ?? "")
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      potential_customer_websites: splitList(form.get("potential_customer_websites")).length > 0
        ? splitList(form.get("potential_customer_websites"))
        : [...(profile?.potential_customer_websites ?? []), ...(profile?.reference_websites ?? [])],
      customer_product_terms: splitList(form.get("customer_product_terms")).length > 0
        ? splitList(form.get("customer_product_terms"))
        : [...(profile?.customer_product_terms ?? []), ...profileProductTerms(profile)],
      excluded_product_terms: splitList(form.get("excluded_product_terms")).length > 0
        ? splitList(form.get("excluded_product_terms"))
        : profile?.excluded_product_terms ?? [],
      extra_language_terms: Object.fromEntries(
        String(form.get("extra_language_terms") ?? "")
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean)
          .map((item) => {
            const [language, value] = item.split(":");
            return [language?.trim(), value?.trim()];
          })
          .filter(([language, value]) => language && value)
      ),
      market_strategy: String(form.get("market_strategy") ?? "standard"),
      simulate_search_location: form.get("simulate_search_location") === "on",
      location_provider: String(form.get("location_provider") ?? "valentin_desktop"),
      search_engines: form.getAll("search_engines").map((item) => String(item)),
      search_all_countries: form.get("search_all_countries") === "on",
      country_groups: form.getAll("country_groups").map((item) => String(item)),
      extra_target_countries: String(form.get("extra_target_countries") ?? "")
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      trade_database_sources: form.getAll("trade_database_sources").map((item) => String(item)),
      search_maps: true,
      search_web: true,
      product_image_id: productImageId
    };

    try {
      const response = await fetch(`${apiUrl}/searches`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error("Arama istegi basarisiz oldu.");
      }

      const data = (await response.json()) as SearchResponse;
      setLastSearch(data);
      setResults(data.results);
      setActiveTab("results");
      loadHistory();
      loadSubscription();
    } catch {
      setError("Backend bağlantısı kurulamadı. Projeyi main.py veya main.bat ile başlattığınızdan emin olun.");
    } finally {
      setIsLoading(false);
    }
  }

  async function validateFormTerms(form: HTMLFormElement) {
    const data = new FormData(form);
    const payload = {
      target_country: String(data.get("target_country") ?? ""),
      country_domain: String(data.get("country_domain") ?? ""),
      product_name_tr: String(data.get("product_name_tr") ?? ""),
      product_name_en: String(data.get("product_name_en") ?? ""),
      product_name_es: String(data.get("product_name_es") ?? ""),
      product_name_ru: String(data.get("product_name_ru") ?? ""),
      product_name_ar: String(data.get("product_name_ar") ?? ""),
      product_name_fr: String(data.get("product_name_fr") ?? ""),
      product_name_de: String(data.get("product_name_de") ?? ""),
      hs_code: String(data.get("hs_code") ?? ""),
      oem_no: String(data.get("oem_no") ?? ""),
      competitors: [],
      related_sectors: [],
      search_engines: ["google"]
    };
    const response = await fetch(`${apiUrl}/ai/dictionary/from-search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (response.ok) {
      setDictionaryValidation((await response.json()) as DictionaryValidationResponse);
    }
  }

  async function uploadProductImage(file: File) {
    const form = new FormData();
    form.append("file", file);
    const response = await fetch(`${apiUrl}/images/product`, {
      method: "POST",
      body: form
    });
    if (!response.ok) {
      throw new Error("Ürün resmi yüklenemedi.");
    }
    const data = (await response.json()) as ImageUploadResponse;
    setProductImage(data);
    return data.image_id;
  }

  async function loadHistory() {
    const response = await fetch(`${apiUrl}/searches/history`);
    if (response.ok) {
      setHistory((await response.json()) as SearchHistoryItem[]);
    }
  }

  async function loadSubscription() {
    const response = await fetch(`${apiUrl}/subscription`);
    if (response.ok) {
      setSubscription((await response.json()) as SubscriptionPlan);
    }
  }

  async function resetUsage() {
    const response = await fetch(`${apiUrl}/subscription/reset-usage`, {
      method: "POST"
    });
    if (response.ok) {
      setSubscription((await response.json()) as SubscriptionPlan);
    }
  }

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const form = new FormData(event.currentTarget);
    const payload: CustomerProfile = {
      customer_name: String(form.get("customer_name") ?? ""),
      company_name: String(form.get("company_name") ?? ""),
      website: String(form.get("website") ?? "") || null,
      catalog_url: String(form.get("catalog_url") ?? "") || null,
      default_sender_email: String(form.get("default_sender_email") ?? "") || null,
      target_sector: String(form.get("target_sector") ?? "") || null,
      profile_products: parseProfileProducts(form),
      reference_websites: splitList(form.get("profile_reference_websites")),
      potential_customer_websites: splitList(form.get("profile_potential_customer_websites")),
      customer_product_terms: splitList(form.get("profile_customer_product_terms")),
      excluded_product_terms: splitList(form.get("profile_excluded_product_terms"))
    };

    const response = await fetch(`${apiUrl}/customer/profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      setProfile((await response.json()) as CustomerProfile);
      loadSubscription();
    } else {
      setError("Müşteri profili kaydedilemedi.");
    }
  }

  async function loadVisitors() {
    const response = await fetch(`${apiUrl}/visitors`);
    if (response.ok) {
      setVisitors((await response.json()) as VisitorRecord[]);
    }
  }

  async function recordVisitorConsent(consent: boolean, coords?: GeolocationCoordinates) {
    await fetch(`${apiUrl}/visitors/consent`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        consent,
        latitude: coords?.latitude ?? null,
        longitude: coords?.longitude ?? null,
        page_url: window.location.href
      })
    });
    loadVisitors();
  }

  function allowLocation() {
    if (!navigator.geolocation) {
      recordVisitorConsent(false);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => recordVisitorConsent(true, position.coords),
      () => recordVisitorConsent(false),
      { enableHighAccuracy: false, timeout: 8000 }
    );
  }

  async function downloadExcel() {
    if (!lastSearch) {
      return;
    }

    const response = await fetch(`${apiUrl}/exports/leads.xlsx`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(lastSearch)
    });

    if (!response.ok) {
      setError("Excel dosyasi olusturulamadi.");
      return;
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "potansiyel_musteriler.xlsx";
    link.click();
    window.URL.revokeObjectURL(url);
  }

  async function previewCampaign() {
    if (!lastSearch) {
      return;
    }

    const response = await fetch(`${apiUrl}/campaigns/preview`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        leads: lastSearch.results,
        sender_company: profile?.company_name ?? "Demo Export Company",
        catalog_url: profile?.catalog_url ?? null
      })
    });

    if (response.ok) {
      setCampaign((await response.json()) as CampaignPreview);
    }
  }

  async function loadCampaigns() {
    const response = await fetch(`${apiUrl}/campaigns`);
    if (response.ok) {
      setCampaignJobs((await response.json()) as CampaignJob[]);
    }
  }

  async function queueCampaign() {
    if (!campaign) {
      return;
    }

    const response = await fetch(`${apiUrl}/campaigns/queue`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ preview: campaign })
    });

    if (response.ok) {
      const job = (await response.json()) as CampaignJob;
      setCampaignJobs((current) => [job, ...current]);
    }
  }

  async function scanFair(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsFairLoading(true);
    setError(null);

    const form = new FormData(event.currentTarget);
    const payload = {
      fair_name: String(form.get("fair_name") ?? ""),
      target_country: String(form.get("fair_country") ?? ""),
      product_name: String(form.get("fair_product") ?? ""),
      sector: String(form.get("fair_sector") ?? ""),
      fair_website: String(form.get("fair_website") ?? "")
    };

    try {
      const response = await fetch(`${apiUrl}/fairs/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!response.ok) {
        throw new Error("Fuar tarama istegi basarisiz oldu.");
      }
      setFairScan((await response.json()) as FairScanResponse);
    } catch {
      setError("Fuar tarama servisine ulasilamadi.");
    } finally {
      setIsFairLoading(false);
    }
  }

  async function scanFairList(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsFairLoading(true);
    setError(null);

    const form = new FormData(event.currentTarget);
    const response = await fetch(`${apiUrl}/fairs/list-scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        fair_name: String(form.get("manual_fair_name") ?? ""),
        target_country: String(form.get("manual_fair_country") ?? ""),
        product_name: String(form.get("manual_fair_product") ?? ""),
        sector: String(form.get("manual_fair_sector") ?? ""),
        participant_names: String(form.get("participant_names") ?? "").split("\n").map((item) => item.trim()).filter(Boolean),
        website_urls: String(form.get("website_urls") ?? "").split("\n").map((item) => item.trim()).filter(Boolean)
      })
    });

    if (response.ok) {
      setFairScan((await response.json()) as FairScanResponse);
    } else {
      setError("Fuar liste tarama servisine ulasilamadi.");
    }
    setIsFairLoading(false);
  }

  async function scanRfq(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsRfqLoading(true);
    setError(null);

    const form = new FormData(event.currentTarget);
    const response = await fetch(`${apiUrl}/rfq/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        product_name: String(form.get("rfq_product") ?? ""),
        target_country: String(form.get("rfq_country") ?? "") || null,
        hs_code: String(form.get("rfq_hs_code") ?? "") || null,
        platforms: form.getAll("rfq_platforms").map((item) => String(item))
      })
    });

    if (response.ok) {
      setRfqScan((await response.json()) as RfqScanResponse);
    } else {
      setError("RFQ tarama servisine ulasilamadi.");
    }
    setIsRfqLoading(false);
  }

  async function queueDemandShare(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const response = await fetch(`${apiUrl}/demand-shares`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        product_name: String(form.get("share_product") ?? ""),
        target_markets: String(form.get("share_markets") ?? "").split(",").map((item) => item.trim()).filter(Boolean),
        message: String(form.get("share_message") ?? ""),
        channels: form.getAll("share_channels").map((item) => String(item))
      })
    });
    if (response.ok) {
      const job = (await response.json()) as DemandShareJob;
      setDemandShares((current) => [job, ...current]);
    }
  }

  async function submitTraining(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const response = await fetch(`${apiUrl}/training/quiz`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        employee_name: String(form.get("employee_name") ?? ""),
        lesson_id: String(form.get("lesson_id") ?? ""),
        answers: [
          { question_id: "q1", answer: String(form.get("q1") ?? "").toLowerCase() },
          { question_id: "q2", answer: String(form.get("q2") ?? "").toLowerCase() }
        ]
      })
    });
    if (response.ok) {
      const result = (await response.json()) as TrainingQuizResult;
      setLastTrainingResult(result);
      setTrainingResults((current) => [result, ...current]);
    }
  }

  async function sendWidgetMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsWidgetLoading(true);
    setError(null);

    const form = new FormData(event.currentTarget);
    const response = await fetch(`${apiUrl}/widget/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: String(form.get("widget_message") ?? ""),
        visitor_email: String(form.get("widget_email") ?? "") || null,
        visitor_phone: String(form.get("widget_phone") ?? "") || null,
        page_url: String(form.get("widget_page_url") ?? "") || "https://demo-musteri-site.com",
        language: String(form.get("widget_language") ?? "tr")
      })
    });

    if (response.ok) {
      const reply = (await response.json()) as WidgetMessageResponse;
      setWidgetReply(reply);
      if (reply.lead_captured) {
        const leadsResponse = await fetch(`${apiUrl}/widget/leads`);
        if (leadsResponse.ok) {
          setWidgetLeads((await leadsResponse.json()) as WidgetLeadRecord[]);
        }
      }
    } else {
      setError("Widget mesaj servisine ulaşılamadı.");
    }
    setIsWidgetLoading(false);
  }

  async function downloadFairExcel() {
    if (!fairScan) {
      return;
    }

    const response = await fetch(`${apiUrl}/exports/fair-participants.xlsx`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(fairScan)
    });

    if (!response.ok) {
      setError("Fuar Excel dosyasi olusturulamadi.");
      return;
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "fuar_katilimcilari.xlsx";
    link.click();
    window.URL.revokeObjectURL(url);
  }

  async function downloadOperationReport() {
    const response = await fetch(`${apiUrl}/exports/operation-report.xlsx`);
    if (!response.ok) {
      setError("Operasyon raporu olusturulamadi.");
      return;
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "operasyon_raporu.xlsx";
    link.click();
    window.URL.revokeObjectURL(url);
  }

  async function askAssistant(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsChatLoading(true);
    setError(null);

    const form = new FormData(event.currentTarget);
    const message = String(form.get("chat_message") ?? "");

    try {
      const response = await fetch(`${apiUrl}/chat/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          current_results: results
        })
      });
      if (!response.ok) {
        throw new Error("Chat isteği başarısız oldu.");
      }
      setChatAnswer((await response.json()) as ChatResponse);
    } catch {
      setError("Chat robotu cevap üretemedi.");
    } finally {
      setIsChatLoading(false);
    }
  }

  const filteredResults = results.filter((result) => {
    if (resultSiteFilter === "all") {
      return true;
    }
    return (result.site_category ?? "unknown") === resultSiteFilter;
  });

  function siteCategoryLabel(category: string) {
    if (category === "ecommerce") {
      return "E-ticaret";
    }
    if (category === "company_website") {
      return "Firma web sitesi";
    }
    if (category === "search_page") {
      return "Arama sayfası";
    }
    if (category === "demo_source") {
      return "Demo kaynak";
    }
    return "Belirsiz";
  }

  if (!isMounted) {
    return (
      <main className="shell">
        <section className="loginShell">
          <div className="loginPanel">
            <p className="eyebrow">Dış ticaret istihbarat</p>
            <h1>Panel hazırlanıyor</h1>
            <p className="empty">Güvenli oturum ve arayüz yükleniyor.</p>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="shell">
      {!session?.authenticated ? (
        <section className="loginShell">
          <form className="loginPanel" onSubmit={handleLogin}>
            <p className="eyebrow">Dış ticaret istihbarat</p>
            <h1>Giriş</h1>
            <label>
              Kullanıcı adı
              <input name="username" defaultValue="demo" required />
            </label>
            <label>
              Şifre
              <input name="password" defaultValue="demo123" required type="password" />
            </label>
            <button className="primaryButton" disabled={isLoginLoading}>
              {isLoginLoading ? "Giriş yapılıyor..." : "Giriş yap"}
            </button>
            {error && <p className="error">{error}</p>}
          </form>
        </section>
      ) : (
      <>
      <section className="topbar">
        <div>
          <p className="eyebrow">Dış ticaret istihbarat</p>
          <h1>Potansiyel müşteri arama paneli</h1>
          <p className="topbarCopy">Global pazarlarda alıcı, fuar katılımcısı, RFQ fırsatı ve web lead kaynaklarını tek merkezden yönetin.</p>
        </div>
        <div className="accountBox">
          <strong>{subscription?.customer_name ?? session.customer_name}</strong>
          <small>{session.username}</small>
          <small>{subscription ? `${subscription.used_queries}/${subscription.monthly_query_limit} sorgu` : "Paket yükleniyor"}</small>
          <button className="linkButton" type="button" onClick={resetUsage}>
            Sıfırla
          </button>
          <button className="linkButton" type="button" onClick={logout}>
            Çıkış
          </button>
        </div>
      </section>

      <nav className="tabBar" aria-label="Panel menüsü">
        {dashboardTabs.map((tab) => (
          <button className={activeTab === tab.id ? "tabButton active" : "tabButton"} key={tab.id} type="button" onClick={() => setActiveTab(tab.id)}>
            <span>{tab.label}</span>
            <small>{tab.hint}</small>
          </button>
        ))}
      </nav>

      <section className={activeTab === "pricing" ? "moduleStrip tabPane active" : "moduleStrip tabPane"}>
        {modules.map((module) => {
          const active = subscription?.enabled_modules.includes(module.code) ?? false;
          return (
            <article className={active ? "moduleCard active" : "moduleCard"} key={module.code}>
              <div>
                <h3>{module.name}</h3>
                <p>{module.description}</p>
              </div>
              <small>
                ${module.setup_price_usd} kurulum / ${module.monthly_price_usd} aylık
              </small>
            </article>
          );
        })}
        <article className="moduleCard bundleCard">
          <div>
            <h3>Tüm modüller paketi</h3>
            <p>Word reçetesindeki paket önerisine göre tüm arama, fuar, RFQ, mail, eğitim ve widget modüllerini tek çatı altında toplar.</p>
          </div>
          <small>$4000 kurulum / $100 aylık</small>
        </article>
        {modules.length === 0 && <p className="empty">Paket ve modül bilgileri yükleniyor.</p>}
      </section>

      <section className="workspace">
        <form className={activeTab === "search" ? "searchPanel tabPane active" : "searchPanel tabPane"} onSubmit={handleSubmit}>
          <h2>Arama bilgileri</h2>
          <div className="grid">
            <label>
              Hedef ülke
              <input name="target_country" required placeholder="İngiltere" />
            </label>
            <label>
              Ülke uzantısı
              <input name="country_domain" placeholder=".co.uk" />
            </label>
            <label>
              Pazar paketi
              <select name="market_strategy" defaultValue="standard">
                <option value="standard">Standart</option>
                <option value="china">Çin pazarı</option>
                <option value="usa">ABD pazarı</option>
              </select>
            </label>
            <label>
              Lokasyon sağlayıcı
              <select name="location_provider" defaultValue="valentin_desktop">
                <option value="valentin_desktop">Valentin desktop</option>
                <option value="playwright_geo">Playwright geo</option>
                <option value="manual_country">Manuel ülke hedefi</option>
              </select>
            </label>
            <label>
              Ürün Türkçe adı
              <input name="product_name_tr" placeholder="otomotiv yedek parça" />
            </label>
            <label>
              Ürün İngilizce adı
              <input name="product_name_en" placeholder="automotive spare parts" />
            </label>
            <label>
              Ürün İspanyolca adı
              <input name="product_name_es" placeholder="repuestos de automoción" />
            </label>
            <label>
              Ürün Rusça adı
              <input name="product_name_ru" placeholder="автозапчасти" />
            </label>
            <label>
              Ürün Arapça adı
              <input name="product_name_ar" placeholder="قطع غيار السيارات" />
            </label>
            <label>
              Ürün Fransızca adı
              <input name="product_name_fr" placeholder="pièces automobiles" />
            </label>
            <label>
              Ürün Almanca adı
              <input name="product_name_de" placeholder="autoteile" />
            </label>
            <label>
              GTIP / HS Code
              <input name="hs_code" placeholder="8708" />
            </label>
            <label>
              OEM No
              <input name="oem_no" placeholder="OEM kodu" />
            </label>
            <label className="wide">
              Rakip markalar
              <input name="competitors" placeholder="Marka A, Marka B" />
            </label>
            <label className="wide">
              Bağlı sektörler
              <input name="related_sectors" placeholder="hırdavat, kaynak ekipmanı" />
            </label>
            <label className="wide">
              Müşteri potansiyelime uygun web siteleri
              <textarea name="potential_customer_websites" defaultValue={joinList(profile?.potential_customer_websites)} placeholder={"https://www.example-supplier.com\nhttps://www.example-distributor.com"} />
            </label>
            <label className="wide">
              Müşteride gerçekten olan ürünler
              <textarea name="customer_product_terms" defaultValue={joinList(profile?.customer_product_terms)} placeholder={"ağır vasıta piston\nkamyon pistonu\ndizel motor pistonu"} />
            </label>
            <label className="wide">
              Hariç tutulacak / yanlış ürünler
              <textarea name="excluded_product_terms" defaultValue={joinList(profile?.excluded_product_terms)} placeholder={"küçük araç pistonu\nmotosiklet pistonu\nbenzinli binek piston"} />
            </label>
            <label className="wide">
              Ek dil terimleri
              <input name="extra_language_terms" placeholder="bg:avtochasti, az:ehtiyat hisseleri, ka:natsilebi" />
            </label>
            <label className="wide">
              Ek hedef ülkeler
              <input name="extra_target_countries" placeholder="Bulgaria, Georgia, Azerbaijan" />
            </label>
            <label className="wide">
              Ürün resmi
              <input name="product_image" accept="image/*" type="file" />
            </label>
            <div className="wide optionGroup">
              <span>Arama motorları</span>
              <label className="checkboxLine">
                <input name="search_engines" type="checkbox" value="google" defaultChecked />
                Google
              </label>
              <label className="checkboxLine">
                <input name="search_engines" type="checkbox" value="bing" defaultChecked />
                Bing
              </label>
              <label className="checkboxLine">
                <input name="search_engines" type="checkbox" value="yandex" defaultChecked />
                Yandex
              </label>
              <label className="checkboxLine">
                <input name="search_engines" type="checkbox" value="safari" />
                Safari/Web
              </label>
            </div>
            <div className="wide optionGroup">
              <span>Ülke paketleri</span>
              <label className="checkboxLine">
                <input name="country_groups" type="checkbox" value="europe" />
                Avrupa
              </label>
              <label className="checkboxLine">
                <input name="country_groups" type="checkbox" value="middle_east" />
                Orta Doğu
              </label>
              <label className="checkboxLine">
                <input name="country_groups" type="checkbox" value="turkic" />
                Türk Cumhuriyetleri
              </label>
              <label className="checkboxLine">
                <input name="country_groups" type="checkbox" value="americas" />
                Amerika
              </label>
              <label className="checkboxLine">
                <input name="country_groups" type="checkbox" value="asia" />
                Asya
              </label>
            </div>
            <label className="checkboxLine wide">
              <input name="search_all_countries" type="checkbox" />
              Seçilen ülke paketleriyle toplu arama planı oluştur
            </label>
            <div className="wide optionGroup">
              <span>Dış ticaret kaynakları</span>
              {["tradeatlas", "importgenius", "panjiva", "europages", "kompass", "un_comtrade", "tradekey", "trademap"].map((source) => (
                <label className="checkboxLine" key={source}>
                  <input name="trade_database_sources" type="checkbox" value={source} />
                  {source}
                </label>
              ))}
            </div>
            <label className="checkboxLine wide">
              <input name="simulate_search_location" type="checkbox" />
              Aramayı hedef ülkeden yapılıyormuş gibi planla
            </label>
          </div>
          {productImage && (
            <p className="uploadInfo">
              Yüklenen resim: {productImage.filename} / {Math.round(productImage.size_bytes / 1024)} KB
            </p>
          )}
          <button className="primaryButton" disabled={isLoading}>
            {isLoading ? "Aranıyor..." : "Arama görevi oluştur"}
          </button>
          <button className="secondaryButton inlineAction" type="button" onClick={(event) => validateFormTerms(event.currentTarget.form as HTMLFormElement)}>
            Sözlük doğrula
          </button>
          {dictionaryValidation && (
            <div className="validationList">
              {dictionaryValidation.items.map((item) => (
                <p key={`${item.term}-${item.normalized_term}`}>
                  <strong>{item.term}</strong> / {item.status} {item.suggestion ? `/ önerilen: ${item.suggestion}` : ""}
                </p>
              ))}
            </div>
          )}
          {error && <p className="error">{error}</p>}
        </form>

        <section className={activeTab === "search" ? "historyPanel tabPane active" : "historyPanel tabPane"}>
          <div className="panelHeader">
            <h2>Geçmiş aramalar</h2>
            <button className="secondaryButton" type="button" onClick={loadHistory}>
              Yenile
            </button>
          </div>
          <div className="historyList">
            {history.map((item) => (
              <div className="historyItem" key={item.request_id}>
                <strong>{item.product_name ?? "Ürün bilgisi yok"}</strong>
                <small>
                  {item.target_country} / {item.result_count} sonuç / {item.status}
                </small>
              </div>
            ))}
            {history.length === 0 && <p className="empty">PostgreSQL bağlantısı hazır olduğunda arama geçmişi burada görünecek.</p>}
          </div>
        </section>

        <section className={activeTab === "operations" ? "profilePanel tabPane active" : "profilePanel tabPane"}>
          <div className="panelHeader">
            <h2>Müşteri profili</h2>
            <small className="panelMeta">{profile?.company_name ?? "Profil yükleniyor"}</small>
          </div>
          <form className="profileForm" onSubmit={saveProfile}>
            <div className="grid">
              <label>
                Müşteri adı
                <input name="customer_name" defaultValue={profile?.customer_name ?? "Demo Müşteri"} />
              </label>
              <label>
                Şirket adı
                <input name="company_name" defaultValue={profile?.company_name ?? "Demo Export Company"} />
              </label>
              <label>
                Web sitesi
                <input name="website" defaultValue={profile?.website ?? ""} placeholder="https://..." />
              </label>
              <label>
                Katalog linki
                <input name="catalog_url" defaultValue={profile?.catalog_url ?? ""} placeholder="https://..." />
              </label>
              <label>
                Gönderici e-posta
                <input name="default_sender_email" defaultValue={profile?.default_sender_email ?? ""} placeholder="export@example.com" />
              </label>
              <label>
                Hedef sektör
                <input name="target_sector" defaultValue={profile?.target_sector ?? ""} placeholder="automotive aftermarket" />
              </label>
              <div className="wide profileTableBlock">
                <div className="profileTableHeader">
                  <strong>Profil ürünleri</strong>
                  <small>Ürün adı, İngilizce adı, GTIP ve ürün görseli arama kalitesini artırır.</small>
                </div>
                <div className="profileProductTable">
                  <div className="profileProductHeader">
                    <span>Ürün</span>
                    <span>İsmi</span>
                    <span>İngilizce ismi</span>
                    <span>GTIP numarası</span>
                    <span>Ürünün resmi</span>
                  </div>
                  {[0, 1, 2].map((index) => {
                    const product = profile?.profile_products?.[index];
                    return (
                      <div className="profileProductRow" key={`profile-product-${index}`}>
                        <strong>Ürün {index + 1}</strong>
                        <input name={`profile_product_name_tr_${index}`} defaultValue={product?.name_tr ?? ""} placeholder="Fren balatası" />
                        <input name={`profile_product_name_en_${index}`} defaultValue={product?.name_en ?? ""} placeholder="Brake pads" />
                        <input name={`profile_product_hs_code_${index}`} defaultValue={product?.hs_code ?? ""} placeholder="870830" />
                        <input name={`profile_product_image_url_${index}`} defaultValue={product?.image_url ?? ""} placeholder="https://..." />
                      </div>
                    );
                  })}
                </div>
              </div>
              <label className="wide">
                Referans web siteleri
                <textarea name="profile_reference_websites" defaultValue={joinList(profile?.reference_websites)} placeholder={"https://www.europages.co.uk\nhttps://www.kompass.com\nhttps://www.autodoc.co.uk"} />
              </label>
              <label className="wide">
                Potansiyel müşteri web siteleri
                <textarea name="profile_potential_customer_websites" defaultValue={joinList(profile?.potential_customer_websites)} placeholder={"https://www.truckparts.com\nhttps://www.enginecomponents.com"} />
              </label>
              <label className="wide">
                Müşteride olan ürünler
                <textarea name="profile_customer_product_terms" defaultValue={joinList(profile?.customer_product_terms)} placeholder={"ağır vasıta piston\nkamyon pistonu\ndizel piston"} />
              </label>
              <label className="wide">
                Hariç tutulacak ürünler
                <textarea name="profile_excluded_product_terms" defaultValue={joinList(profile?.excluded_product_terms)} placeholder={"küçük araç pistonu\nmotosiklet pistonu"} />
              </label>
            </div>
            <button className="primaryButton">Profili kaydet</button>
          </form>
        </section>

        <section className={activeTab === "operations" ? "statusPanel tabPane active" : "statusPanel tabPane"}>
          <div className="panelHeader">
            <h2>Entegrasyon durumu</h2>
            <div className="buttonRow">
              <small className="panelMeta">{systemStatus ? `${systemStatus.app_name} / ${systemStatus.app_env}` : "Durum yükleniyor"}</small>
              <button className="secondaryButton" type="button" onClick={downloadOperationReport}>
                Rapor indir
              </button>
            </div>
          </div>
          <div className="statusGrid">
            {systemStatus?.integrations.map((item) => (
              <div className={`statusItem ${item.status}`} key={item.code}>
                <strong>{item.name}</strong>
                <small>{item.status}</small>
                <p>{item.detail}</p>
              </div>
            ))}
            {!systemStatus && <p className="empty">Entegrasyon hazırlık bilgileri burada görünecek.</p>}
          </div>
        </section>

        <section className={activeTab === "operations" ? "visitorPanel tabPane active" : "visitorPanel tabPane"}>
          <div className="panelHeader">
            <h2>Web ziyaretçi tespiti</h2>
            <button className="secondaryButton" type="button" onClick={loadVisitors}>
              Yenile
            </button>
          </div>
          <div className="visitorConsent">
            <p>Size daha iyi hizmet verebilmemiz için konum bilginizi bizimle paylaşır mısınız?</p>
            <div className="buttonRow">
              <button className="primaryButton compact" type="button" onClick={allowLocation}>
                Evet
              </button>
              <button className="secondaryButton" type="button" onClick={() => recordVisitorConsent(false)}>
                Hayır
              </button>
            </div>
          </div>
          <div className="notificationList">
            {visitors.slice(0, 3).map((visitor) => (
              <div className="notificationItem" key={`notification-${visitor.visitor_id}`}>
                <strong>{visitor.notification_title ?? "Yeni web ziyaretçisi"}</strong>
                <small>{visitor.notification_message ?? `${visitor.company_guess ?? "Bilinmeyen ziyaretçi"} / ${visitor.country ?? "konum yok"}`}</small>
              </div>
            ))}
            {visitors.length === 0 && <p className="empty">Ziyaretçi bildirimi geldiğinde burada öne çıkarılacak.</p>}
          </div>
          <div className="historyList">
            {visitors.slice(0, 5).map((visitor) => (
              <div className="historyItem" key={visitor.visitor_id}>
                <strong>{visitor.company_guess ?? "Bilinmeyen ziyaretçi"}</strong>
                <small>
                  {visitor.lookup_method} / {visitor.consent ? "konum izni var" : "IP takibi"} / {visitor.ip_address ?? "IP yok"}
                </small>
                <small>
                  {[visitor.city, visitor.country].filter(Boolean).join(", ") || "Konum yok"} / güven {visitor.lookup_confidence}
                </small>
                {(visitor.organization || visitor.isp) && <small>{visitor.organization ?? visitor.isp}</small>}
              </div>
            ))}
            {visitors.length === 0 && <p className="empty">Ziyaretçi kaydı burada görünecek.</p>}
          </div>
        </section>

        <section className={activeTab === "fairs" ? "fairPanel tabPane active" : "fairPanel tabPane"}>
          <div className="panelHeader">
            <h2>Fuar katılımcı tarama</h2>
            <button className="secondaryButton" type="button" disabled={!fairScan} onClick={downloadFairExcel}>
              Excel indir
            </button>
          </div>
          <form className="fairForm" onSubmit={scanFair}>
            <div className="grid">
              <label>
                Fuar adı
                <input name="fair_name" required placeholder="Automechanika Frankfurt" />
              </label>
              <label>
                Fuar ülkesi
                <input name="fair_country" required placeholder="Germany" />
              </label>
              <label>
                Ürün
                <input name="fair_product" placeholder="automotive spare parts" />
              </label>
              <label>
                Sektör
                <input name="fair_sector" placeholder="automotive aftermarket" />
              </label>
              <label className="wide">
                Fuar web sitesi
                <input name="fair_website" placeholder="https://..." />
              </label>
            </div>
            <button className="primaryButton" disabled={isFairLoading}>
              {isFairLoading ? "Taranıyor..." : "Katılımcı tara"}
            </button>
          </form>
          <div className="historyList">
            {fairScan?.participants.map((participant) => (
              <div className="historyItem" key={`${participant.company_name}-${participant.booth}`}>
                <strong>{participant.company_name}</strong>
                <small>
                  {participant.country} / {participant.city ?? "şehir yok"} / {participant.booth ?? "stand yok"}
                </small>
                <small>
                  {participant.email ?? "e-posta yok"} / puan {participant.score}
                </small>
                {participant.notes && <small>{participant.notes}</small>}
              </div>
            ))}
            {!fairScan && <p className="empty">Fuar katılımcı adayları burada listelenecek.</p>}
          </div>
        </section>

        <section className={activeTab === "fairs" ? "fairPanel tabPane active" : "fairPanel tabPane"}>
          <div className="panelHeader">
            <h2>Fuar liste/link tarama</h2>
            <small className="panelMeta">Katılımcı listesi veya link havuzu</small>
          </div>
          <form className="fairForm" onSubmit={scanFairList}>
            <div className="grid">
              <label>
                Fuar adı
                <input name="manual_fair_name" required placeholder="Automechanika Frankfurt" />
              </label>
              <label>
                Hedef ülke
                <input name="manual_fair_country" required placeholder="Germany" />
              </label>
              <label>
                Ürün
                <input name="manual_fair_product" placeholder="automotive spare parts" />
              </label>
              <label>
                Sektör
                <input name="manual_fair_sector" placeholder="automotive aftermarket" />
              </label>
              <label className="wide">
                Katılımcı firma adları
                <textarea name="participant_names" placeholder={"ABC GmbH\nGlobal Parts LLC"} />
              </label>
              <label className="wide">
                Web sitesi linkleri
                <textarea name="website_urls" placeholder={"https://example.com\nhttps://supplier.com"} />
              </label>
            </div>
            <button className="primaryButton" disabled={isFairLoading}>
              {isFairLoading ? "Taranıyor..." : "Listeyi tara"}
            </button>
          </form>
        </section>

        <section className={activeTab === "widget" ? "widgetPanel tabPane active" : "widgetPanel tabPane"}>
          <div className="panelHeader">
            <h2>Site chat widget deneme alanı</h2>
            <small className="panelMeta">{widgetLeads.length} lead kaydı</small>
          </div>
          <div className="flowGrid">
            <div className="flowCard active">
              <strong>1. Ziyaretçi soru sorar</strong>
              <small>Siteye eklenen widget mesajı backend'e gönderir.</small>
            </div>
            <div className="flowCard">
              <strong>2. Cevap aynı kutuya döner</strong>
              <small>Widget, ziyaretçiye otomatik cevap ve sonraki soruyu gösterir.</small>
            </div>
            <div className="flowCard">
              <strong>3. E-posta/telefon varsa lead olur</strong>
              <small>İletişim bırakan ziyaretçi aşağıdaki lead listesine düşer.</small>
            </div>
          </div>
          <form className="widgetDemoForm" onSubmit={sendWidgetMessage}>
            <div className="grid">
              <label>
                Ziyaretçi mesajı
                <textarea name="widget_message" required placeholder="Merhaba, otomotiv yedek parça kataloğunuzu alabilir miyim?" />
              </label>
              <label>
                Widget dili
                <select name="widget_language" defaultValue="tr">
                  <option value="tr">Türkçe</option>
                  <option value="en">English</option>
                </select>
              </label>
              <label>
                Ziyaretçi e-posta
                <input name="widget_email" placeholder="buyer@example.com" />
              </label>
              <label>
                Ziyaretçi telefon
                <input name="widget_phone" placeholder="+44 7000 000000" />
              </label>
              <label className="wide">
                Mesajın geldiği sayfa
                <input name="widget_page_url" placeholder="https://demo-musteri-site.com/products" />
              </label>
            </div>
            <button className="primaryButton" disabled={isWidgetLoading}>
              {isWidgetLoading ? "Widget cevaplıyor..." : "Widget mesajını dene"}
            </button>
          </form>
          {widgetReply ? (
            <div className="resultCallout">
              <strong>Widget cevabı</strong>
              <p>{widgetReply.reply}</p>
              <small>{widgetReply.next_question}</small>
              <small>{widgetReply.lead_captured ? "Bu mesaj lead listesine kaydedildi." : "İletişim bilgisi olmadığı için sadece cevap döndü, lead oluşmadı."}</small>
            </div>
          ) : (
            <p className="empty">Buradan mesaj gönderince ziyaretçinin göreceği cevap bu sekmede görünecek.</p>
          )}
          <pre className="codeBox">{`<script src="${apiUrl.replace("/api", "")}/chat-widget.js" data-api-url="${apiUrl}" data-language="tr"></script>`}</pre>
          <div className="historyList">
            {widgetLeads.slice(0, 5).map((lead, index) => (
              <div className="historyItem" key={`${lead.message}-${index}`}>
                <strong>{lead.visitor_email ?? lead.visitor_phone ?? "Anonim ziyaretçi"}</strong>
                <small>{lead.message}</small>
                <small>{lead.page_url ?? "sayfa yok"} / {lead.language}</small>
              </div>
            ))}
            {widgetLeads.length === 0 && <p className="empty">Widget üzerinden gelen mesajlar burada listelenecek.</p>}
          </div>
        </section>

        <section className={activeTab === "demand" ? "rfqPanel tabPane active" : "rfqPanel tabPane"}>
          <div className="panelHeader">
            <h2>B2B talep avı</h2>
            <small className="panelMeta">{rfqScan ? `${rfqScan.opportunities.length} fırsat` : "RFQ platformları"}</small>
          </div>
          <form className="rfqForm" onSubmit={scanRfq}>
            <div className="grid">
              <label>
                Ürün
                <input name="rfq_product" required placeholder="automotive spare parts" />
              </label>
              <label>
                Hedef ülke
                <input name="rfq_country" placeholder="United States" />
              </label>
              <label>
                GTIP / HS Code
                <input name="rfq_hs_code" placeholder="8708" />
              </label>
              <div className="wide optionGroup">
                <span>Platformlar</span>
                {["tradekey", "ecplaza", "eworldtrade", "indiamart", "tradeindia", "made_in_china", "dhgate", "ec21", "thomasnet"].map((platform) => (
                  <label className="checkboxLine" key={platform}>
                    <input name="rfq_platforms" type="checkbox" value={platform} />
                    {platform}
                  </label>
                ))}
              </div>
            </div>
            <button className="primaryButton" disabled={isRfqLoading}>
              {isRfqLoading ? "Taranıyor..." : "Talep tara"}
            </button>
          </form>
          <div className="historyList">
            {rfqScan?.opportunities.map((item) => (
              <div className="historyItem" key={`${item.platform}-${item.source_url}`}>
                <strong>{item.platform}: {item.title}</strong>
                <small>{item.buyer_country} / puan {item.score} / {item.quantity_hint ?? "miktar yok"}</small>
                <small>{item.contact_hint}</small>
                <small>{item.notes}</small>
              </div>
            ))}
            {!rfqScan && <p className="empty">B2B pazar yerlerinden RFQ/talep adayları burada listelenecek.</p>}
          </div>
        </section>

        <section className={activeTab === "demand" ? "demandPanel tabPane active" : "demandPanel tabPane"}>
          <div className="panelHeader">
            <h2>Otomatik talep paylaşımı</h2>
            <small className="panelMeta">{demandShares.length} kuyruk kaydı</small>
          </div>
          <form className="demandForm" onSubmit={queueDemandShare}>
            <div className="grid">
              <label>
                Ürün
                <input name="share_product" required placeholder="automotive spare parts" />
              </label>
              <label>
                Hedef pazarlar
                <input name="share_markets" placeholder="Germany, USA, UAE" />
              </label>
              <label className="wide">
                Paylaşım mesajı
                <textarea name="share_message" required placeholder="We can supply..." />
              </label>
              <div className="wide optionGroup">
                <span>Kanallar</span>
                {["manual_review", "email_partner", "b2b_marketplace", "crm_task"].map((channel) => (
                  <label className="checkboxLine" key={channel}>
                    <input name="share_channels" type="checkbox" value={channel} />
                    {channel}
                  </label>
                ))}
              </div>
            </div>
            <button className="primaryButton">Paylaşım kuyruğuna al</button>
          </form>
          <div className="historyList">
            {demandShares.slice(0, 5).map((item) => (
              <div className="historyItem" key={item.share_id}>
                <strong>{item.product_name}</strong>
                <small>{item.status} / {item.channels.join(", ")}</small>
                <small>{item.target_markets.join(", ") || "pazar yok"}</small>
                <small>{item.notes}</small>
              </div>
            ))}
          </div>
        </section>

        <section className={activeTab === "training" ? "trainingPanel tabPane active" : "trainingPanel tabPane"}>
          <div className="panelHeader">
            <h2>Dış ticaret eğitim ve takip</h2>
            <small className="panelMeta">{trainingLessons.length} ders / {trainingResults.length} sonuç</small>
          </div>
          <div className="lessonGrid">
            {trainingLessons.map((lesson) => (
              <article className="lessonCard" key={lesson.lesson_id}>
                <strong>{lesson.title}</strong>
                <small>{lesson.duration_minutes} dakika</small>
                <small>Geçme notu: {lesson.required_score}</small>
              </article>
            ))}
          </div>
          <form className="trainingForm" onSubmit={submitTraining}>
            <div className="flowGrid">
              <div className="flowCard active">
                <strong>1. Personel ders seçer</strong>
                <small>Dersin geçme notu backend'de tutulur.</small>
              </div>
              <div className="flowCard">
                <strong>2. Quiz cevapları gönderilir</strong>
                <small>Sistem cevap anahtarına göre puan hesaplar.</small>
              </div>
              <div className="flowCard">
                <strong>3. Sonuç takip listesine düşer</strong>
                <small>Başarılı/tekrar gerekli durumu anında görünür.</small>
              </div>
            </div>
            <div className="grid">
              <label>
                Personel adı
                <input name="employee_name" required placeholder="Ayşe" />
              </label>
              <label>
                Ders
                <select name="lesson_id" required>
                  {trainingLessons.map((lesson) => (
                    <option key={lesson.lesson_id} value={lesson.lesson_id}>
                      {lesson.title}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Soru 1 cevabı
                <input name="q1" required placeholder="incoterms / website / unsubscribe" />
              </label>
              <label>
                Soru 2 cevabı
                <input name="q2" required placeholder="invoice / buyer / small_batch" />
              </label>
            </div>
            <button className="primaryButton">Quiz kaydet</button>
          </form>
          {lastTrainingResult && (
            <div className={lastTrainingResult.passed ? "resultCallout success" : "resultCallout warning"}>
              <strong>Son quiz sonucu</strong>
              <p>{lastTrainingResult.employee_name} için skor {lastTrainingResult.score}. Durum: {lastTrainingResult.status}</p>
              <small>{lastTrainingResult.passed ? "Personel bu dersi tamamladı." : "Personelin dersi tekrar etmesi gerekiyor."}</small>
            </div>
          )}
          <div className="historyList">
            {trainingResults.slice(0, 5).map((item, index) => (
              <div className="historyItem" key={`${item.employee_name}-${item.lesson_id}-${item.score}-${item.status}-${index}`}>
                <strong>{item.employee_name}</strong>
                <small>{item.lesson_id} / skor {item.score} / {item.status}</small>
              </div>
            ))}
          </div>
        </section>

        <section className={activeTab === "widget" ? "chatPanel tabPane active" : "chatPanel tabPane"}>
          <div className="panelHeader">
            <h2>Web chat robotu</h2>
            <small className="panelMeta">{results.length} sonuç bağlamda</small>
          </div>
          <form className="chatForm" onSubmit={askAssistant}>
            <label>
              Sorunuz
              <textarea name="chat_message" required placeholder="En iyi firmalar hangileri? Mail kampanyasını nasıl başlatayım?" />
            </label>
            <button className="primaryButton" disabled={isChatLoading}>
              {isChatLoading ? "Cevap hazırlanıyor..." : "Soru sor"}
            </button>
          </form>
          {chatAnswer ? (
            <div className="chatAnswer">
              <p>{chatAnswer.reply}</p>
              <div className="historyList">
                {chatAnswer.suggestions.map((suggestion, index) => (
                  <div className="historyItem" key={`${suggestion.title}-${suggestion.detail}-${index}`}>
                    <strong>{suggestion.title}</strong>
                    <small>{suggestion.detail}</small>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="empty">Chat robotu arama, Excel, mail ve fuar adımları için yardımcı cevap verecek.</p>
          )}
        </section>

        <section className={activeTab === "demand" ? "campaignPanel tabPane active" : "campaignPanel tabPane"}>
          <div className="panelHeader">
            <h2>Mail kampanyası</h2>
            <div className="buttonRow">
              <button className="secondaryButton" type="button" disabled={!lastSearch} onClick={previewCampaign}>
                Önizleme
              </button>
              <button className="secondaryButton" type="button" disabled={!campaign} onClick={queueCampaign}>
                Kuyruğa al
              </button>
              <button className="secondaryButton" type="button" onClick={loadCampaigns}>
                Yenile
              </button>
            </div>
          </div>
          {campaign ? (
            <div className="campaignPreview">
              <strong>{campaign.subject}</strong>
              <small>{campaign.recipients.length} alıcı / spam risk {campaign.spam_risk_score}</small>
              <p>{campaign.body}</p>
              {campaign.spam_warnings.length > 0 && <small>{campaign.spam_warnings.join(" | ")}</small>}
            </div>
          ) : (
            <p className="empty">Arama sonuçlarından mail kampanyası önizlemesi oluşturulacak.</p>
          )}
          <div className="historyList">
            {campaignJobs.slice(0, 5).map((job) => (
              <div className="historyItem" key={job.campaign_id}>
                <strong>{job.subject}</strong>
                <small>
                  {job.recipient_count} alıcı / {job.batches} parti / durum: {job.status}
                </small>
                <small>
                  spam risk {job.spam_risk_score} / gönderim {job.send_enabled ? "açık" : "kapalı"}
                </small>
                {job.warnings.length > 0 && <small>{job.warnings.join(" | ")}</small>}
              </div>
            ))}
          </div>
        </section>

        <section className={activeTab === "results" ? "resultsPanel tabPane active" : "resultsPanel tabPane"}>
          <div className="panelHeader">
            <h2>Sonuçlar</h2>
            <button className="secondaryButton" disabled={results.length === 0} onClick={downloadExcel}>
              Excel indir
            </button>
          </div>
          <div className="filterBar">
            {[
              ["all", "Tümü"],
              ["ecommerce", "Sadece e-ticaret"],
              ["company_website", "Sadece firma web siteleri"],
              ["search_page", "Arama sayfaları"]
            ].map(([value, label]) => (
              <button className={resultSiteFilter === value ? "filterButton active" : "filterButton"} key={value} type="button" onClick={() => setResultSiteFilter(value as ResultSiteFilter)}>
                {label}
              </button>
            ))}
            <small>{filteredResults.length}/{results.length} sonuç gösteriliyor</small>
          </div>
          {lastSearch && (
            <div className="queryPlan">
              <h3>Arama planı</h3>
              {lastSearch.query_plan.slice(0, 6).map((item) => (
                <p key={`${item.engine}-${item.language}-${item.query}`}>
                  <strong>{item.engine}</strong> / {item.source_type}: {item.query}
                </p>
              ))}
            </div>
          )}
          <div className="table">
            <div className="row header">
              <span>Firma</span>
              <span>Ülke</span>
              <span>Kaynak</span>
              <span>Eşleşen</span>
              <span>İletişim</span>
              <span>AI</span>
              <span>Puan</span>
            </div>
            {filteredResults.map((result, index) => (
              <div className="row" key={`${result.company_name}-${result.source}-${result.website ?? "no-website"}-${index}`}>
                <span>
                  <strong>{result.company_name}</strong>
                  {result.city && <small>{result.city}</small>}
                </span>
                <span>{result.country}</span>
                <span>
                  {result.source}
                  <small>{result.source_type}</small>
                  <small className={`siteBadge ${result.site_category ?? "unknown"}`}>{siteCategoryLabel(result.site_category ?? "unknown")}</small>
                </span>
                <span>{result.matched_keyword ?? "-"}</span>
                <span>
                  {result.website && (
                    <a className="tableActionLink" href={result.website} rel="noreferrer" target="_blank">
                      {(result.site_category ?? "unknown") === "ecommerce"
                        ? "Ürün sayfasını aç"
                        : (result.site_category ?? "unknown") === "search_page"
                          ? "Tedarikçi aramasını aç"
                          : "Firma / tedarikçi sayfasını aç"}
                    </a>
                  )}
                  {result.email ? (
                    <a className="tableLink" href={`mailto:${result.email}`}>
                      {result.email}
                    </a>
                  ) : result.phone ? (
                    <a className="tableLink" href={`tel:${result.phone}`}>
                      {result.phone}
                    </a>
                  ) : !result.website ? (
                    "-"
                  ) : null}
                  {result.website?.includes(".example.com") && <small>Demo adres, gerçek siteye gitmez.</small>}
                </span>
                <span>
                  {result.suggested_contact_role ?? "-"}
                  {result.ai_fit_reason && <small>{result.ai_fit_reason}</small>}
                  {result.site_category_reason && <small>{result.site_category_reason}</small>}
                  {result.suggested_contact_emails?.length > 0 && <small>{result.suggested_contact_emails.slice(0, 2).join(", ")}</small>}
                  {result.suggested_email_subject && <small>{result.suggested_email_subject}</small>}
                </span>
                <span>{result.score}</span>
              </div>
            ))}
            {results.length === 0 && <p className="empty">Arama sonucu burada listelenecek.</p>}
            {results.length > 0 && filteredResults.length === 0 && <p className="empty">Bu filtreye uygun sonuç yok. Diğer filtreleri deneyebilirsiniz.</p>}
          </div>
        </section>
      </section>
      </>
      )}
    </main>
  );
}
