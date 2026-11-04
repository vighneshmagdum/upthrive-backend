"use client";

import { FormEvent, useEffect, useState } from "react";
import { ApiError, apiRequest } from "../lib/api";

type User = {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
};

type Profile = {
  current_role: string;
  experience_level: "beginner" | "intermediate" | "advanced";
  skills: string[];
  interests: string[];
  goals: string[];
  weekly_hours: number;
};

type Account = {
  user: User;
  profile: Profile;
};

type Recommendation = {
  id: string;
  title: string;
  summary: string;
  category: string;
  difficulty: string;
  estimated_weeks: number;
  weekly_hours: number;
  skills: string[];
  steps: string[];
  score: number;
  explanation: string;
  status: "saved" | null;
};

type AuthResponse = { user: User };
type RecommendationResponse = { items: Recommendation[]; model: string };

type ProfileForm = {
  full_name: string;
  current_role: string;
  experience_level: Profile["experience_level"];
  skills: string;
  interests: string;
  goals: string;
  weekly_hours: number;
};

function splitTerms(value: string): string[] {
  return value.split(",").map((item) => item.trim()).filter(Boolean);
}

function Brand({ light = false }: { light?: boolean }) {
  return (
    <div className={"brand" + (light ? " brand-light" : "")}>
      <span className="brand-mark" aria-hidden="true">u</span>
      <span>upthrive</span>
    </div>
  );
}

function LoadingScreen() {
  return (
    <main className="loading-screen">
      <span className="loading-mark">u</span>
      <p>Finding your next step</p>
      <span className="loading-line" />
    </main>
  );
}

export default function Home() {
  const [account, setAccount] = useState<Account | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [modelName, setModelName] = useState("");
  const [booting, setBooting] = useState(true);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [form, setForm] = useState<ProfileForm>({
    full_name: "",
    current_role: "",
    experience_level: "beginner",
    skills: "",
    interests: "",
    goals: "",
    weekly_hours: 4
  });
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  async function loadDashboard() {
    const nextAccount = await apiRequest<Account>("/users/me");
    const nextRecommendations = await apiRequest<RecommendationResponse>("/recommendations?limit=6");
    setAccount(nextAccount);
    setRecommendations(nextRecommendations.items);
    setModelName(nextRecommendations.model);
  }

  useEffect(() => {
    let active = true;
    apiRequest<Account>("/users/me")
      .then(async (nextAccount) => {
        if (!active) return;
        const results = await apiRequest<RecommendationResponse>("/recommendations?limit=6");
        if (!active) return;
        setAccount(nextAccount);
        setRecommendations(results.items);
        setModelName(results.model);
      })
      .catch((reason: unknown) => {
        if (!active) return;
        if (!(reason instanceof ApiError) || reason.status !== 401) {
          setError("The UpThrive service could not be reached. Please try again in a moment.");
        }
      })
      .finally(() => {
        if (active) setBooting(false);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!account) return;
    setForm({
      full_name: account.user.full_name,
      current_role: account.profile.current_role,
      experience_level: account.profile.experience_level,
      skills: account.profile.skills.join(", "),
      interests: account.profile.interests.join(", "),
      goals: account.profile.goals.join(", "),
      weekly_hours: account.profile.weekly_hours
    });
  }, [account]);

  async function submitAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const path = authMode === "register" ? "/auth/register" : "/auth/login";
      const body = authMode === "register"
        ? { full_name: name, email, password }
        : { email, password };
      await apiRequest<AuthResponse>(path, { method: "POST", body });
      setPassword("");
      await loadDashboard();
      setNotice("You’re signed in. Your growth plan is ready.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to sign in.");
    } finally {
      setBusy(false);
    }
  }

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const updated = await apiRequest<Account>("/users/me/profile", {
        method: "PATCH",
        body: {
          full_name: form.full_name,
          current_role: form.current_role,
          experience_level: form.experience_level,
          skills: splitTerms(form.skills),
          interests: splitTerms(form.interests),
          goals: splitTerms(form.goals),
          weekly_hours: Number(form.weekly_hours)
        }
      });
      setAccount(updated);
      const refreshed = await apiRequest<RecommendationResponse>("/recommendations?limit=6");
      setRecommendations(refreshed.items);
      setModelName(refreshed.model);
      setNotice("Your profile and recommendations are updated.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not save your profile.");
    } finally {
      setBusy(false);
    }
  }

  async function updatePath(item: Recommendation, status: "saved" | "completed") {
    setError("");
    setNotice("");
    try {
      await apiRequest<void>("/recommendations/" + item.id + "/status", {
        method: "PATCH",
        body: { status }
      });
      const refreshed = await apiRequest<RecommendationResponse>("/recommendations?limit=6");
      setRecommendations(refreshed.items);
      setModelName(refreshed.model);
      setNotice(status === "saved" ? "Added to your saved paths." : "Path marked as complete.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not update this path.");
    }
  }

  async function signOut() {
    setError("");
    try {
      await apiRequest<{ message: string }>("/auth/logout", { method: "POST" });
      setAccount(null);
      setRecommendations([]);
      setNotice("You’ve signed out.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to sign out.");
    }
  }

  if (booting) return <LoadingScreen />;

  if (!account) {
    return (
      <main className="auth-page">
        <section className="auth-visual">
          <div className="auth-visual-inner">
            <Brand light />
            <div className="hero-copy">
              <p className="eyebrow">A clearer way forward</p>
              <h1>Your next chapter starts with one good step.</h1>
              <p className="hero-intro">
                Turn your interests and current skills into a career path you can actually move toward.
              </p>
              <div className="hero-steps">
                <div className="hero-step"><span>01</span><p>Tell us where you are</p></div>
                <div className="hero-step"><span>02</span><p>See paths that fit</p></div>
                <div className="hero-step"><span>03</span><p>Make progress at your pace</p></div>
              </div>
            </div>
            <div className="visual-note"><span className="note-dot" /> Your growth, your rhythm</div>
          </div>
          <div className="visual-orbit orbit-one" />
          <div className="visual-orbit orbit-two" />
        </section>

        <section className="auth-panel">
          <div className="auth-panel-content">
            <div className="mobile-brand"><Brand /></div>
            <div className="auth-heading">
              <p className="eyebrow">Start growing</p>
              <h2>{authMode === "login" ? "Welcome back" : "Create your account"}</h2>
              <p>{authMode === "login" ? "Sign in to pick up where you left off." : "A few details are all we need to get started."}</p>
            </div>
            {error && <div className="alert alert-error" role="alert">{error}</div>}
            {notice && <div className="alert alert-success" role="status">{notice}</div>}
            <form className="auth-form" onSubmit={submitAuth}>
              {authMode === "register" && (
                <label className="field">
                  <span>Your name</span>
                  <input autoComplete="name" value={name} onChange={(event) => setName(event.target.value)} required minLength={2} maxLength={120} placeholder="e.g. Alex Morgan" />
                </label>
              )}
              <label className="field">
                <span>Email address</span>
                <input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required placeholder="you@example.com" />
              </label>
              <label className="field">
                <span>Password</span>
                <input type="password" autoComplete={authMode === "login" ? "current-password" : "new-password"} value={password} onChange={(event) => setPassword(event.target.value)} required minLength={authMode === "register" ? 10 : 1} maxLength={128} placeholder={authMode === "register" ? "At least 10 characters" : "Enter your password"} />
              </label>
              <button className="button button-primary button-wide" type="submit" disabled={busy}>
                {busy ? "Please wait…" : authMode === "login" ? "Sign in" : "Create account"}
                {!busy && <span aria-hidden="true">↗</span>}
              </button>
            </form>
            <p className="auth-switch">
              {authMode === "login" ? "New to UpThrive?" : "Already have an account?"}
              <button type="button" onClick={() => { setAuthMode(authMode === "login" ? "register" : "login"); setError(""); }}>
                {authMode === "login" ? "Create an account" : "Sign in"}
              </button>
            </p>
            <div className="security-note"><span aria-hidden="true">⌑</span> Your account details stay private and protected.</div>
          </div>
        </section>
      </main>
    );
  }

  const firstName = account.user.full_name.trim().split(/\s+/)[0];

  return (
    <main className="dashboard-shell">
      <aside className="sidebar">
        <Brand />
        <div className="sidebar-section">
          <p className="sidebar-label">Workspace</p>
          <a className="nav-link nav-link-active" href="#overview"><span>◫</span> Overview</a>
          <a className="nav-link" href="#pathways"><span>⌁</span> Career paths</a>
          <a className="nav-link" href="#profile"><span>◉</span> My profile</a>
        </div>
        <div className="sidebar-spacer" />
        <div className="sidebar-card">
          <span className="sidebar-spark">✳</span>
          <p>Small steps build momentum.</p>
          <span>Your plan is yours to shape.</span>
        </div>
        <button className="sidebar-user" type="button" onClick={signOut}>
          <span className="avatar">{firstName.slice(0, 1).toUpperCase()}</span>
          <span className="sidebar-user-copy"><strong>{account.user.full_name}</strong><small>Sign out</small></span>
          <span className="signout-icon" aria-hidden="true">↗</span>
        </button>
      </aside>

      <section className="dashboard-main" id="overview">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> Overview</div>
          <div className="topbar-right"><span className="live-indicator" /> Your plan is up to date <span className="topbar-avatar">{firstName.slice(0, 1).toUpperCase()}</span></div>
        </header>

        <div className="dashboard-content">
          <section className="welcome-row">
            <div>
              <p className="eyebrow">Your growth dashboard</p>
              <h1>Good to see you, {firstName}<span className="welcome-period">.</span></h1>
              <p className="welcome-subtitle">Here are a few directions that fit what you want to build next.</p>
            </div>
            <div className="date-chip"><span className="date-icon">◷</span> Personal plan <span className="chip-divider" /> Updated now</div>
          </section>

          {(error || notice) && <div className={"alert " + (error ? "alert-error" : "alert-success")} role={error ? "alert" : "status"}>{error || notice}</div>}

          <section className="stats-grid" aria-label="Profile overview">
            <div className="stat-card stat-card-featured">
              <div className="stat-top"><span>Profile readiness</span><span className="stat-symbol">✳</span></div>
              <strong>{Math.min(100, 35 + account.profile.skills.length * 8 + account.profile.goals.length * 6)}<small>%</small></strong>
              <div className="progress-track"><span style={{ width: Math.min(100, 35 + account.profile.skills.length * 8 + account.profile.goals.length * 6) + "%" }} /></div>
              <p>Add skills and goals to make matches more specific.</p>
            </div>
            <div className="stat-card">
              <div className="stat-top"><span>Paths to explore</span><span className="stat-symbol muted-symbol">⌁</span></div>
              <strong>{recommendations.length}<small> paths</small></strong>
              <p>Matched to your current direction and interests.</p>
            </div>
            <div className="stat-card">
              <div className="stat-top"><span>Weekly study time</span><span className="stat-symbol muted-symbol">◷</span></div>
              <strong>{account.profile.weekly_hours}<small> hrs</small></strong>
              <p>Small, steady sessions add up over time.</p>
            </div>
          </section>

          <div className="content-grid">
            <section className="recommendations-section" id="pathways">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">Picked for you</p>
                  <h2>Paths worth exploring</h2>
                </div>
                <span className="match-label"><span>✳</span> Profile matched</span>
              </div>
              <p className="section-intro">A starting point, not a fixed route. Save the paths that feel right and adjust your profile any time.</p>
              {recommendations.length === 0 ? (
                <div className="empty-state"><span>✳</span><h3>Your next set of paths is taking shape.</h3><p>Update your profile with a few skills or goals to get more focused matches.</p></div>
              ) : (
                <div className="path-list">
                  {recommendations.map((item, index) => (
                    <article className="path-card" key={item.id}>
                      <div className="path-index">{String(index + 1).padStart(2, "0")}</div>
                      <div className="path-content">
                        <div className="path-heading-row">
                          <div><div className="path-category">{item.category}<span>·</span>{item.difficulty}</div><h3>{item.title}</h3></div>
                          <div className="match-score"><strong>{item.score}%</strong><span>fit</span></div>
                        </div>
                        <p className="path-summary">{item.summary}</p>
                        <p className="match-reason"><span aria-hidden="true">✳</span> {item.explanation}</p>
                        <div className="path-tags">{item.skills.slice(0, 4).map((skill) => <span key={skill}>{skill}</span>)}</div>
                        <details className="path-plan">
                          <summary>View learning plan <span aria-hidden="true">⌄</span></summary>
                          <ol>{item.steps.map((step) => <li key={step}>{step}</li>)}</ol>
                        </details>
                        <div className="path-footer">
                          <div className="path-time"><span>◷</span> {item.estimated_weeks} weeks <i /> {item.weekly_hours} hrs / week</div>
                          <div className="path-actions">
                            <button className="button button-quiet" type="button" onClick={() => updatePath(item, "completed")}>Mark complete</button>
                            <button className={"button " + (item.status === "saved" ? "button-saved" : "button-outline")} type="button" onClick={() => updatePath(item, "saved")}>
                              {item.status === "saved" ? "✓ Saved" : "Save path"}
                            </button>
                          </div>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              )}
              <div className="model-note"><span className="model-dot" /> Matching model: {modelName || "profile-fit-v1"} <span>·</span> Recommendations use the profile details you provide.</div>
            </section>

            <aside className="profile-column" id="profile">
              <div className="profile-panel">
                <div className="profile-heading">
                  <div><p className="eyebrow">Your starting point</p><h2>Growth profile</h2></div>
                  <span className="profile-icon">◉</span>
                </div>
                <p className="profile-hint">A little context helps us make better suggestions.</p>
                <form className="profile-form" onSubmit={saveProfile}>
                  <label className="field">
                    <span>Name</span>
                    <input value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} required minLength={2} maxLength={120} />
                  </label>
                  <label className="field">
                    <span>Current role or focus</span>
                    <input value={form.current_role} onChange={(event) => setForm({ ...form, current_role: event.target.value })} maxLength={120} placeholder="e.g. Junior developer" />
                  </label>
                  <label className="field">
                    <span>Experience level</span>
                    <select value={form.experience_level} onChange={(event) => setForm({ ...form, experience_level: event.target.value as ProfileForm["experience_level"] })}>
                      <option value="beginner">Just getting started</option>
                      <option value="intermediate">Building experience</option>
                      <option value="advanced">Experienced</option>
                    </select>
                  </label>
                  <label className="field">
                    <span>Skills <small>Separate with commas</small></span>
                    <textarea rows={2} value={form.skills} onChange={(event) => setForm({ ...form, skills: event.target.value })} placeholder="Python, communication, SQL" />
                  </label>
                  <label className="field">
                    <span>Interests</span>
                    <textarea rows={2} value={form.interests} onChange={(event) => setForm({ ...form, interests: event.target.value })} placeholder="Building products, data, design" />
                  </label>
                  <label className="field">
                    <span>Career goals</span>
                    <textarea rows={2} value={form.goals} onChange={(event) => setForm({ ...form, goals: event.target.value })} placeholder="Move into backend engineering" />
                  </label>
                  <label className="field">
                    <span>Study time per week <strong>{form.weekly_hours} hrs</strong></span>
                    <input className="range-input" type="range" min="1" max="20" value={form.weekly_hours} onChange={(event) => setForm({ ...form, weekly_hours: Number(event.target.value) })} />
                    <span className="range-labels"><small>1 hour</small><small>20 hours</small></span>
                  </label>
                  <button className="button button-primary button-wide" type="submit" disabled={busy}>
                    {busy ? "Saving…" : "Update my plan"} <span aria-hidden="true">↗</span>
                  </button>
                </form>
              </div>
              <div className="privacy-card"><span aria-hidden="true">⌑</span><p><strong>Your information stays yours.</strong><br />Your profile is used to personalize your plan and is not shared with employers.</p></div>
            </aside>
          </div>
          <footer className="dashboard-footer"><span>UpThrive</span><span>Make growth feel possible.</span><a href="#pathways">How matches work</a></footer>
        </div>
      </section>
    </main>
  );
}
