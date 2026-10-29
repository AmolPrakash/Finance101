/* Finance101 interactive textbook.
 *
 * Chapters are Markdown files in chapters/. Fenced blocks tagged ```python run
 * become editable, runnable cells. Math uses \( inline \) and \[ display \]
 * delimiters so dollar signs stay dollar signs. Python runs in a Web Worker
 * (assets/py-worker.js) using Pyodide, entirely in the browser.
 */
(() => {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);
  const el = (tag, attrs = {}, children = []) => {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") node.className = v;
      else if (k === "text") node.textContent = v;
      else if (k === "html") node.innerHTML = v;
      else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
      else node.setAttribute(k, v);
    }
    for (const child of [].concat(children)) if (child != null) node.append(child);
    return node;
  };
  const escapeHtml = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  // ---------- Small persistence helpers (never required for the page to work) ----------
  const store = {
    get(key, fallback) {
      try { const v = localStorage.getItem("f101-" + key); return v == null ? fallback : JSON.parse(v); } catch (e) { return fallback; }
    },
    set(key, value) {
      try { localStorage.setItem("f101-" + key, JSON.stringify(value)); } catch (e) { /* private mode */ }
    },
  };

  const state = {
    toc: null,
    chapters: [],     // flat list: {slug, title, num, course}
    manifest: null,
    done: new Set(store.get("done", [])),
    route: null,
    cells: [],
  };

  // ---------- Python runtime client ----------
  const statusEl = $("#py-status");
  function setStatus(kind, label) {
    statusEl.dataset.state = kind;
    $(".label", statusEl).textContent = label;
  }

  const Py = {
    worker: null,
    ready: null,
    seq: 0,
    pending: new Map(),
    busy: 0,

    start() {
      if (this.ready) return this.ready;
      setStatus("loading", "Loading Python…");
      this.worker = new Worker("assets/py-worker.js");
      this.worker.onmessage = (e) => {
        const resolve = this.pending.get(e.data.id);
        this.pending.delete(e.data.id);
        if (resolve) resolve(e.data);
      };
      this.worker.onerror = (e) => {
        setStatus("error", "Python failed to load");
        this.failAll("Python could not start: " + (e.message || "network error") + "\nCheck your connection and reload the page.");
        this.ready = null;
      };
      this.ready = this.call({ type: "init", baseUrl: new URL(".", location.href).href }).then((r) => {
        if (!r.ok) { setStatus("error", "Python failed to load"); this.ready = null; throw new Error(r.text); }
        setStatus("ready", "Python ready");
        return r;
      });
      return this.ready;
    },

    call(msg) {
      return new Promise((resolve) => {
        const id = ++this.seq;
        this.pending.set(id, resolve);
        this.worker.postMessage({ ...msg, id });
      });
    },

    failAll(text) {
      for (const resolve of this.pending.values()) resolve({ ok: false, text, images: [] });
      this.pending.clear();
    },

    async exec(msg) {
      try { await this.start(); } catch (err) { return { ok: false, text: String(err.message || err), images: [] }; }
      this.busy++;
      setStatus("busy", "Running…");
      try {
        return await this.call(msg);
      } finally {
        if (--this.busy === 0 && statusEl.dataset.state !== "error") setStatus("ready", "Python ready");
      }
    },

    restart() {
      if (this.worker) this.worker.terminate();
      this.failAll("Python was restarted.");
      this.worker = null;
      this.ready = null;
      this.busy = 0;
      return this.start();
    },
  };

  // ---------- Output rendering ----------
  function showResult(outEl, result) {
    outEl.replaceChildren();
    outEl.classList.toggle("has-error", !result.ok);
    if (result.text) {
      outEl.append(el("span", { class: result.ok ? "" : "err", text: result.text.replace(/\n$/, "") }));
    }
    for (const img of result.images || []) {
      outEl.append(el("img", { src: "data:image/png;base64," + img, alt: "Chart produced by the code above" }));
    }
    if (!result.text && !(result.images || []).length) {
      outEl.append(el("span", { class: "muted", text: "✓ Ran with no output" }));
    }
  }

  // ---------- Editors ----------
  function makeEditor(parent, code, onRun, opts = {}) {
    return CodeMirror(parent, {
      value: code,
      mode: "python",
      indentUnit: 4,
      tabSize: 4,
      lineNumbers: !!opts.lineNumbers,
      matchBrackets: true,
      viewportMargin: opts.fixedHeight ? 10 : Infinity,
      lineWrapping: !opts.fixedHeight || !!opts.wrap,   // wrap in narrow reading columns
      extraKeys: {
        "Shift-Enter": onRun,
        "Ctrl-Enter": onRun,
        "Cmd-Enter": onRun,
        Tab: (cm) => cm.somethingSelected() ? cm.indentSelection("add") : cm.replaceSelection("    ", "end"),
        "Shift-Tab": (cm) => cm.indentSelection("subtract"),
      },
    });
  }

  // ---------- Markdown + math ----------
  const CALLOUTS = { NOTE: "Note", TIP: "Try it", IMPORTANT: "Key idea", WARNING: "Watch out", CAUTION: "Caution" };

  function renderMarkdown(src) {
    const cells = [];
    const math = [];
    const fence = /(^```[^\n]*\n[\s\S]*?^```[ \t]*$)/m;
    const protectedSrc = src.split(fence).map((part) => {
      if (part.startsWith("```")) return part;
      return part
        .replace(/\\\[([\s\S]+?)\\\]/g, (_, tex) => { math.push({ tex, display: true }); return `\n\nMATHTOKEN${math.length - 1}X\n\n`; })
        .replace(/\\\(([\s\S]+?)\\\)/g, (_, tex) => { math.push({ tex, display: false }); return `MATHTOKEN${math.length - 1}X`; });
    }).join("");

    const renderer = new marked.Renderer();
    renderer.code = function (code, info) {
      if (typeof code === "object") { info = code.lang; code = code.text; }   // marked >= 13 passes a token
      const lang = (info || "").trim();
      if (/^python\s+run\b/.test(lang)) {
        cells.push(code.replace(/\n$/, ""));
        return `<div class="cell" data-cell="${cells.length - 1}"></div>`;
      }
      return `<pre><code>${escapeHtml(code)}</code></pre>`;
    };
    let html = marked.parse(protectedSrc, { renderer, gfm: true });

    html = html.replace(/<p>MATHTOKEN(\d+)X<\/p>|MATHTOKEN(\d+)X/g, (_, a, b) => {
      const m = math[a ?? b];
      try {
        return katex.renderToString(m.tex, { displayMode: m.display, throwOnError: false });
      } catch (e) {
        return escapeHtml(m.tex);
      }
    });
    return { html, cells };
  }

  function decorateArticle(root) {
    for (const bq of root.querySelectorAll("blockquote")) {
      const p = bq.firstElementChild;
      const m = p && p.innerHTML.match(/^\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*(?:<br>)?/);
      if (!m) continue;
      p.innerHTML = p.innerHTML.slice(m[0].length);
      bq.classList.add("callout", "callout-" + m[1].toLowerCase());
      bq.prepend(el("span", { class: "callout-title", text: CALLOUTS[m[1]] }));
    }
    for (const li of root.querySelectorAll("li")) {
      const first = li.firstChild;
      if (!first || first.nodeType !== Node.TEXT_NODE) continue;
      const m = first.textContent.match(/^\s*\[(watch|read|course|data|tool)\]\s*/i);
      if (!m) continue;
      first.textContent = first.textContent.slice(m[0].length);
      li.prepend(el("span", { class: "resource-tag " + m[1].toLowerCase(), text: m[1] }));
    }
    for (const a of root.querySelectorAll("a[href^='http']")) {
      a.target = "_blank";
      a.rel = "noopener";
    }
  }

  // ---------- Cells ----------
  function mountCell(host, code, namespace) {
    host.replaceChildren();
    const editorHost = el("div", { class: "cell-editor" });
    const out = el("div", { class: "output", "aria-live": "polite" });
    const status = el("span", { class: "status" });
    const runBtn = el("button", { class: "btn btn-run", text: "▶ Run" });
    const cell = { code, cm: null, run: null };

    cell.run = async () => {
      runBtn.disabled = true;
      status.textContent = Py.ready ? "Running…" : "Starting Python (first run takes a few seconds)…";
      const result = await Py.exec({ type: "run", code: cell.cm.getValue(), namespace });
      showResult(out, result);
      status.textContent = "";
      runBtn.disabled = false;
      return result;
    };
    runBtn.addEventListener("click", cell.run);

    const bar = el("div", { class: "cell-bar" }, [
      runBtn,
      el("span", { class: "hint", text: "Shift+Enter" }),
      status,
      el("span", { class: "spacer" }),
      el("button", { class: "btn btn-ghost", text: "Reset", title: "Restore the original code", onclick: () => { cell.cm.setValue(code); out.replaceChildren(); } }),
      el("button", { class: "btn btn-ghost", text: "Open in scratchpad", onclick: () => Scratch.open(cell.cm.getValue()) }),
    ]);
    host.append(editorHost, bar, out);
    cell.cm = makeEditor(editorHost, code, cell.run);
    return cell;
  }

  // ---------- Scratchpad ----------
  const Scratch = {
    cm: null,
    namespace: "scratch",
    ensure() {
      if (this.cm) return;
      const run = () => this.run();
      this.cm = makeEditor($("#scratch-editor"), store.get("scratch", "# Try anything here. Variables from this chapter's cells are available.\nfrom finance101 import time_value as tv\n\ntv.future_value(1000, 0.07, 10)\n"), run, { lineNumbers: true, fixedHeight: true, wrap: true });
      this.cm.on("change", () => store.set("scratch", this.cm.getValue()));
      $("#scratch-run").addEventListener("click", run);
      $("#scratch-clear").addEventListener("click", () => $("#scratch-output").replaceChildren());
    },
    isOpen() { return document.body.classList.contains("scratch-open"); },
    open(code, focus = true) {
      document.body.classList.add("scratch-open");
      $("#scratch-btn").setAttribute("aria-pressed", "true");
      this.ensure();
      if (code != null) this.cm.setValue(code);
      setTimeout(() => { this.cm.refresh(); if (focus) this.cm.focus(); }, 0);
      store.set("scratch-open", true);
    },
    close() {
      document.body.classList.remove("scratch-open");
      $("#scratch-btn").setAttribute("aria-pressed", "false");
      store.set("scratch-open", false);
    },
    toggle() { this.isOpen() ? this.close() : this.open(); },
    async run() {
      const out = $("#scratch-output");
      const result = await Py.exec({ type: "run", code: this.cm.getValue(), namespace: this.namespace });
      showResult(out, result);
    },
    setScope(namespace, label) {
      this.namespace = namespace;
      $("#scratch-scope").textContent = label;
      // The editor may have been created while hidden (e.g. on the home page); re-measure it.
      if (this.cm) setTimeout(() => this.cm.refresh(), 0);
    },
  };

  // ---------- Sidebar ----------
  function renderSidebar() {
    const side = $("#sidebar");
    side.replaceChildren();
    for (const course of state.toc.courses) {
      const block = el("div", { class: "toc-course", style: `--course-color: var(--c-${course.id})` }, [
        el("div", { class: "toc-course-head" }, [el("span", { class: "code", text: course.code }), el("span", { class: "name", text: course.title })]),
      ]);
      for (const ch of course.chapters) {
        block.append(el("a", { class: "toc-link", href: `#/ch/${ch.slug}`, "data-slug": ch.slug }, [
          el("span", { class: "num", text: chapterNum(ch.slug) }),
          el("span", { text: ch.title }),
          state.done.has(ch.slug) ? el("span", { class: "done", text: "✓", title: "Completed" }) : null,
        ]));
      }
      side.append(block);
    }
    side.append(el("div", { class: "toc-extra" }, [
      el("a", { class: "toc-link", href: "#/lab", "data-slug": "lab" }, [el("span", { class: "num", text: "▶" }), el("span", { text: "Code Lab: run every .py file" })]),
      el("a", { class: "toc-link", href: "#/resources", "data-slug": "resources" }, [el("span", { class: "num", text: "★" }), el("span", { text: "Free resources library" })]),
    ]));
    highlightSidebar();
  }

  function highlightSidebar() {
    const active = state.route && (state.route.slug || state.route.page);
    for (const a of document.querySelectorAll(".toc-link")) a.classList.toggle("active", a.dataset.slug === active);
    for (const a of document.querySelectorAll(".top-links a")) a.classList.toggle("active", a.getAttribute("href") === location.hash || (a.getAttribute("href") === "#/" && (!location.hash || location.hash === "#/")));
  }

  const chapterNum = (slug) => slug.split("-")[0];

  // ---------- Pages ----------
  async function fetchText(path) {
    const res = await fetch(path, { cache: "no-cache" });
    if (!res.ok) throw new Error(`${path}: ${res.status}`);
    return res.text();
  }

  function renderHome() {
    document.body.classList.add("no-sidebar", "is-home");
    document.title = "Finance101: an interactive finance textbook";
    Scratch.setScope("scratch", "a free-form Python session");
    const content = $("#content");
    const first = state.chapters[0];
    const totalDone = state.chapters.filter((c) => state.done.has(c.slug)).length;
    const home = el("div", { class: "home" }, [
      el("section", { class: "hero" }, [
        el("h1", { text: "Learn finance by running it." }),
        el("p", { text: `Four courses (FIN 101, 102, 201 and 202) in ${state.chapters.length} chapters. Every formula is explained, then implemented in Python you can edit and run right here in your browser. Nothing to install, nothing to pay.` }),
        el("div", { class: "hero-actions" }, [
          el("a", { class: "btn btn-run", href: `#/ch/${first.slug}`, text: totalDone ? "Continue reading →" : "Start chapter 00 →" }),
          el("a", { class: "btn", href: "#/lab", text: "Open the Code Lab" }),
          el("a", { class: "btn btn-ghost", href: "#/resources", text: "Free resources" }),
        ]),
      ]),
      el("div", { class: "how" }, [
        el("div", {}, [el("h3", { text: "Read" }), el("p", { text: "Each chapter builds intuition first, then the formula, then a worked example, with links to free lectures and readings." })]),
        el("div", {}, [el("h3", { text: "Run & tweak" }), el("p", { text: "Code cells run real Python (Pyodide) in your browser. Change a number, press Shift+Enter, see what happens." })]),
        el("div", {}, [el("h3", { text: "Try it side by side" }), el("p", { text: "The scratchpad sits next to the text and shares the chapter's variables, so you can experiment while you read." })]),
      ]),
      el("h2", { class: "section-title", text: "Courses" }),
      el("div", { class: "courses" }, state.toc.courses.map((course) => {
        const done = course.chapters.filter((c) => state.done.has(c.slug)).length;
        return el("article", { class: "course-card", style: `--course-color: var(--c-${course.id})` }, [
          el("div", { class: "code", text: course.code }),
          el("h2", { text: course.title }),
          el("p", { text: course.summary }),
          el("div", { class: "progress", title: `${done} of ${course.chapters.length} chapters complete` }, [el("span", { style: `width:${(100 * done) / course.chapters.length}%` })]),
          el("ol", {}, course.chapters.map((ch) => el("li", {}, [el("a", { href: `#/ch/${ch.slug}` }, [
            el("span", { class: "num", text: chapterNum(ch.slug) }),
            el("span", { text: ch.title }),
            state.done.has(ch.slug) ? el("span", { class: "done", text: "✓" }) : null,
          ])]))),
        ]);
      })),
    ]);
    content.replaceChildren(home);
  }

  async function renderChapter(slug) {
    const idx = state.chapters.findIndex((c) => c.slug === slug);
    if (idx < 0) return renderHome();
    document.body.classList.remove("no-sidebar");
    const ch = state.chapters[idx];
    document.title = `${chapterNum(slug)} · ${ch.title} | Finance101`;
    Scratch.setScope(slug, `shares variables with chapter ${chapterNum(slug)}`);

    const content = $("#content");
    content.replaceChildren(el("div", { class: "article" }, [el("p", { class: "muted", text: "Loading…" })]));
    let src;
    try { src = await fetchText(`chapters/${slug}.md`); } catch (e) {
      content.replaceChildren(el("div", { class: "article" }, [el("p", { text: "Could not load this chapter. " + e.message })]));
      return;
    }
    if (!state.route || state.route.slug !== slug) return; // user navigated away meanwhile

    const { html, cells } = renderMarkdown(src);
    const article = el("article", { class: "article", style: `--course-color: var(--c-${ch.course.id})` });
    article.innerHTML = html;
    decorateArticle(article);

    // Kicker + tools go right after the H1.
    const h1 = $("h1", article);
    const kicker = el("div", { class: "chapter-kicker", text: `${ch.course.code} · Chapter ${chapterNum(slug)}` });
    const runAll = el("button", { class: "btn", text: "▶ Run all cells" });
    const tools = el("div", { class: "chapter-tools" }, [
      runAll,
      el("button", { class: "btn btn-ghost", text: "Restart Python", title: "Use this if code is stuck in a loop", onclick: () => { Py.restart(); } }),
      el("button", { class: "btn btn-ghost", text: "Scratchpad", onclick: () => Scratch.toggle() }),
      el("span", { class: "muted", text: cells.length ? `${cells.length} runnable cells · edit anything, Shift+Enter to run` : "" }),
    ]);
    if (h1) { h1.before(kicker); h1.after(tools); } else { article.prepend(kicker, tools); }

    // Footer: completion + pager.
    const isDone = state.done.has(slug);
    const doneBtn = el("button", { class: "btn" + (isDone ? "" : " btn-run"), text: isDone ? "✓ Completed" : "Mark chapter complete" });
    doneBtn.addEventListener("click", () => {
      state.done.has(slug) ? state.done.delete(slug) : state.done.add(slug);
      store.set("done", [...state.done]);
      const nowDone = state.done.has(slug);
      doneBtn.textContent = nowDone ? "✓ Completed" : "Mark chapter complete";
      doneBtn.className = "btn" + (nowDone ? "" : " btn-run");
      renderSidebar();
    });
    const prev = state.chapters[idx - 1];
    const next = state.chapters[idx + 1];
    article.append(el("footer", { class: "chapter-footer" }, [
      el("div", { class: "complete-row" }, [doneBtn, el("span", { class: "muted", text: "Progress is saved in this browser." })]),
      el("nav", { class: "pager" }, [
        prev ? el("a", { class: "prev", href: `#/ch/${prev.slug}` }, [el("span", { class: "dir", text: "← Previous" }), `${chapterNum(prev.slug)} · ${prev.title}`]) : el("span"),
        next ? el("a", { class: "next", href: `#/ch/${next.slug}` }, [el("span", { class: "dir", text: "Next →" }), `${chapterNum(next.slug)} · ${next.title}`]) : null,
      ]),
    ]));

    content.replaceChildren(article);
    state.cells = [...article.querySelectorAll(".cell[data-cell]")].map((host) => mountCell(host, cells[+host.dataset.cell], slug));

    runAll.addEventListener("click", async () => {
      runAll.disabled = true;
      for (const cell of state.cells) {
        const r = await cell.run();
        if (!r.ok) break;
      }
      runAll.disabled = false;
    });
  }

  async function renderResources() {
    document.body.classList.remove("no-sidebar");
    document.title = "Free resources | Finance101";
    Scratch.setScope("scratch", "a free-form Python session");
    const src = await fetchText("chapters/resources.md");
    const { html, cells } = renderMarkdown(src);
    const article = el("article", { class: "article resources" });
    article.innerHTML = html;
    decorateArticle(article);
    $("#content").replaceChildren(article);
    state.cells = [...article.querySelectorAll(".cell[data-cell]")].map((host) => mountCell(host, cells[+host.dataset.cell], "resources"));
  }

  // ---------- Code Lab ----------
  const Lab = { files: new Map(), current: null, cm: null };

  function labKind(path) {
    if (path.startsWith("examples/")) return "example";
    if (path.startsWith("tests/")) return "test";
    return "module";
  }

  async function labOpen(path) {
    if (!Lab.files.has(path)) {
      const original = await fetchText(path);
      Lab.files.set(path, { original, current: original });
    }
    Lab.current = path;
    const file = Lab.files.get(path);
    Lab.cm.setValue(file.current);
    Lab.cm.clearHistory();
    $("#lab-path").textContent = path;
    for (const b of document.querySelectorAll(".file-list button")) b.classList.toggle("active", b.dataset.path === path);
    const kind = labKind(path);
    $("#lab-run").textContent = { example: "▶ Run file", test: "▶ Run these tests", module: "Save & reload module" }[kind];
    const testFor = `tests/test_${path.split("/").pop()}`;
    const testBtn = $("#lab-test-module");
    testBtn.hidden = !(kind === "module" && state.manifest.files.tests.includes(testFor));
    testBtn.dataset.path = testFor;
    $("#lab-output").replaceChildren();
    store.set("lab-file", path);
  }

  async function labRun() {
    const path = Lab.current;
    const code = Lab.cm.getValue();
    Lab.files.get(path).current = code;
    const kind = labKind(path);
    const out = $("#lab-output");
    out.replaceChildren(el("span", { class: "muted", text: Py.ready ? "Running…" : "Starting Python…" }));
    const msg = kind === "example" ? { type: "runFile", path, code }
      : kind === "test" ? { type: "test", path, code }
      : { type: "saveModule", path, code };
    showResult(out, await Py.exec(msg));
  }

  async function labRunAllExamples() {
    const out = $("#lab-output");
    out.replaceChildren(el("span", { class: "muted", text: "Running every example…" }));
    const results = [];
    for (const path of state.manifest.files.examples) {
      const file = Lab.files.get(path);
      const code = file ? file.current : await fetchText(path);
      const r = await Py.exec({ type: "runFile", path, code });
      results.push({ path, ...r });
    }
    out.replaceChildren();
    for (const r of results) {
      out.append(el("strong", { text: `${r.ok ? "✓" : "✗"} ${r.path}\n` }));
      const block = el("div");
      showResult(block, r);
      out.append(...block.childNodes, "\n\n");
    }
  }

  async function renderLab() {
    document.body.classList.remove("no-sidebar");
    document.title = "Code Lab | Finance101";
    Scratch.setScope("lab", "a free-form Python session");
    const groups = [["examples", "Examples"], ["finance101", "Library (finance101)"], ["tests", "Tests"]];
    const list = el("div", { class: "file-list" }, groups.flatMap(([key, label]) => [
      el("h4", { text: label }),
      ...state.manifest.files[key].map((path) => el("button", { "data-path": path, text: path.split("/").pop(), onclick: () => labOpen(path) })),
    ]));
    const editorHost = el("div", { class: "cell-editor" });
    const page = el("div", { class: "lab" }, [
      el("h1", { text: "Code Lab" }),
      el("p", { class: "lead", text: "Every Python file in the repository, runnable in your browser. Edit a library module and press “Save & reload”; examples and tests then use your version. Changes live only in this tab." }),
      el("div", { class: "lab-actions" }, [
        el("button", { class: "btn", text: "▶ Run all examples", onclick: labRunAllExamples }),
        el("button", { class: "btn", text: "▶ Run full test suite", onclick: async () => {
          const out = $("#lab-output");
          out.replaceChildren(el("span", { class: "muted", text: "Running pytest (loads pytest on first use)…" }));
          showResult(out, await Py.exec({ type: "test" }));
        } }),
        el("button", { class: "btn btn-ghost", text: "Restart Python", onclick: () => Py.restart() }),
      ]),
      list,
      el("div", { class: "lab-editor" }, [
        el("p", { class: "path", id: "lab-path" }),
        el("div", { class: "cell" }, [
          editorHost,
          el("div", { class: "cell-bar" }, [
            el("button", { class: "btn btn-run", id: "lab-run", text: "▶ Run file", onclick: labRun }),
            el("button", { class: "btn", id: "lab-test-module", text: "Run this module's tests", hidden: "", onclick: (e) => labOpen(e.target.dataset.path) }),
            el("span", { class: "hint", text: "Shift+Enter" }),
            el("span", { class: "spacer" }),
            el("button", { class: "btn btn-ghost", text: "Revert changes", onclick: () => { const f = Lab.files.get(Lab.current); f.current = f.original; Lab.cm.setValue(f.original); } }),
          ]),
          el("div", { class: "output", id: "lab-output", "aria-live": "polite" }),
        ]),
      ]),
    ]);
    $("#content").replaceChildren(page);
    Lab.cm = makeEditor(editorHost, "", labRun, { lineNumbers: true, fixedHeight: true });
    Lab.cm.on("change", () => { if (Lab.current) Lab.files.get(Lab.current).current = Lab.cm.getValue(); });
    const saved = store.get("lab-file", null);
    const all = Object.values(state.manifest.files).flat();
    await labOpen(all.includes(saved) ? saved : state.manifest.files.examples[0]);
  }

  // ---------- Router ----------
  function parseRoute() {
    const hash = location.hash.replace(/^#\/?/, "");
    const [page, slug] = hash.split("/");
    if (page === "ch" && slug) return { page: "chapter", slug };
    if (page === "lab") return { page: "lab" };
    if (page === "resources") return { page: "resources" };
    return { page: "home" };
  }

  async function route() {
    state.route = parseRoute();
    state.cells = [];
    document.body.classList.remove("is-home");
    document.body.classList.remove("menu-open");
    highlightSidebar();
    const r = state.route;
    if (r.page === "chapter") await renderChapter(r.slug);
    else if (r.page === "lab") await renderLab();
    else if (r.page === "resources") await renderResources();
    else renderHome();
    highlightSidebar();
    window.scrollTo(0, 0);
    $("#content").focus({ preventScroll: true });
  }

  // ---------- Boot ----------
  async function boot() {
    const [toc, manifest] = await Promise.all([
      fetch("toc.json").then((r) => r.json()),
      fetch("manifest.json").then((r) => r.json()).catch(() => ({ files: { examples: [], finance101: [], tests: [] } })),
    ]);
    state.toc = toc;
    state.manifest = manifest;
    state.chapters = toc.courses.flatMap((course) => course.chapters.map((ch) => ({ ...ch, course })));
    renderSidebar();

    $("#theme-btn").addEventListener("click", () => {
      const dark = document.documentElement.dataset.theme
        ? document.documentElement.dataset.theme === "dark"
        : matchMedia("(prefers-color-scheme: dark)").matches;
      document.documentElement.dataset.theme = dark ? "light" : "dark";
      try { localStorage.setItem("f101-theme", document.documentElement.dataset.theme); } catch (e) { /* ignore */ }
    });
    $("#scratch-btn").addEventListener("click", () => Scratch.toggle());
    $("#scratch-close").addEventListener("click", () => Scratch.close());
    $("#menu-btn").addEventListener("click", () => document.body.classList.toggle("menu-open"));
    $("#backdrop").addEventListener("click", () => document.body.classList.remove("menu-open"));
    document.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === ".") { e.preventDefault(); Scratch.toggle(); }
    });

    if (store.get("scratch-open", matchMedia("(min-width: 1280px)").matches)) Scratch.open(null, false);
    window.addEventListener("hashchange", route);
    await route();
  }

  boot().catch((err) => {
    $("#content").replaceChildren(el("div", { class: "article" }, [el("h1", { text: "Something went wrong" }), el("p", { text: String(err) })]));
  });
})();
