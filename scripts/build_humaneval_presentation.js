const pptxgen = require("/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/pptxgenjs");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Xiaoyang Cao, Supriya Lall";
pptx.company = "6.C011 Final Project";
pptx.subject = "HumanEval and BCB-Hard decomposition routing study";
pptx.title = "When Does Task Decomposition Help?";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-US",
};
pptx.defineLayout({ name: "CUSTOM_WIDE", width: 13.333, height: 7.5 });
pptx.layout = "CUSTOM_WIDE";
pptx.margin = 0;

const C = {
  ink: "16202A",
  muted: "667085",
  grid: "D6DEE8",
  paper: "F7F9FB",
  white: "FFFFFF",
  blue: "2F6FED",
  cyan: "18A7B5",
  green: "36A269",
  amber: "E5A11A",
  red: "D9534F",
  violet: "6E57D2",
  navy: "243B53",
};

function addHeader(slide, eyebrow, title, section = "HumanEval decomposition routing") {
  slide.background = { color: C.paper };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.18, fill: { color: C.blue }, line: { color: C.blue } });
  slide.addText(eyebrow.toUpperCase(), {
    x: 0.65, y: 0.38, w: 4.8, h: 0.22,
    fontFace: "Aptos", fontSize: 8.5, bold: true, color: C.blue, charSpace: 1.1,
    margin: 0,
  });
  slide.addText(title, {
    x: 0.65, y: 0.68, w: 9.9, h: 0.52,
    fontFace: "Aptos Display", fontSize: 24, bold: true, color: C.ink,
    margin: 0, breakLine: false, fit: "shrink",
  });
  slide.addText(section, {
    x: 9.85, y: 0.42, w: 2.8, h: 0.24,
    fontSize: 8.5, color: C.muted, align: "right", margin: 0,
  });
}

function footer(slide, n, tag = "Presented") {
  slide.addText(tag, { x: 0.65, y: 7.12, w: 2.1, h: 0.2, fontSize: 8, color: C.muted, margin: 0 });
  slide.addText(String(n), { x: 12.35, y: 7.12, w: 0.35, h: 0.2, fontSize: 8, color: C.muted, align: "right", margin: 0 });
}

function card(slide, x, y, w, h, opts = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: opts.fill || C.white },
    line: { color: opts.line || C.grid, transparency: opts.lineTransparency || 0 },
    shadow: opts.shadow ? { type: "outer", color: "CDD6E2", opacity: 0.16, blur: 1.2, angle: 45, distance: 1 } : undefined,
  });
}

function label(slide, text, x, y, w, color = C.blue) {
  slide.addText(text.toUpperCase(), {
    x, y, w, h: 0.22, fontSize: 8.5, bold: true, color, charSpace: 1, margin: 0,
  });
}

function bodyText(slide, text, x, y, w, h, size = 14, color = C.ink) {
  slide.addText(text, {
    x, y, w, h, fontSize: size, color, breakLine: false,
    fit: "shrink", margin: 0.02, valign: "top",
    paraSpaceAfterPt: 4,
  });
}

function metric(slide, value, labelText, x, y, w, color) {
  slide.addText(value, {
    x, y, w, h: 0.42, fontSize: 23, bold: true, color, margin: 0,
    fit: "shrink",
  });
  slide.addText(labelText, {
    x, y: y + 0.5, w, h: 0.3, fontSize: 9.5, color: C.muted, margin: 0,
    fit: "shrink",
  });
}

function bulletList(slide, items, x, y, w, h, size = 12.5) {
  const rich = [];
  items.forEach((item, idx) => {
    rich.push({ text: item, options: { bullet: { type: "ul" }, breakLine: idx < items.length - 1 } });
  });
  slide.addText(rich, {
    x, y, w, h, fontSize: size, color: C.ink, margin: 0.05,
    fit: "shrink", breakLine: false, valign: "top",
    paraSpaceAfterPt: 6,
  });
}

function addMiniTable(slide, rows, x, y, w, h, headerColor = C.navy) {
  const table = rows.map((row, r) => row.map((cell) => ({
    text: cell,
    options: {
      fontSize: r === 0 ? 9.5 : 10,
      bold: r === 0,
      color: r === 0 ? C.white : C.ink,
      fill: r === 0 ? headerColor : C.white,
      margin: 0.06,
      border: { type: "solid", color: C.grid, pt: 0.7 },
      valign: "mid",
      fit: "shrink",
    },
  })));
  slide.addTable(table, {
    x, y, w, h,
    border: { type: "solid", color: C.grid, pt: 0.7 },
    autoFit: false,
  });
}

function pill(slide, text, x, y, w, fill, color = C.white) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h: 0.28, rectRadius: 0.08,
    fill: { color: fill }, line: { color: fill },
  });
  slide.addText(text, { x, y: y + 0.045, w, h: 0.13, fontSize: 7.8, bold: true, color, align: "center", margin: 0, fit: "shrink" });
}

function notes(slide, lines) {
  if (slide.addNotes) slide.addNotes(lines);
}

// Slide 1
{
  const s = pptx.addSlide();
  s.background = { color: "F3F7FC" };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 7.5, fill: { color: "F3F7FC" }, line: { color: "F3F7FC" } });
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.24, fill: { color: C.blue }, line: { color: C.blue } });
  s.addText("When Does Task Decomposition Help?", {
    x: 0.72, y: 1.05, w: 10.6, h: 0.76,
    fontFace: "Aptos Display", fontSize: 34, bold: true, color: C.ink, margin: 0,
    fit: "shrink",
  });
  s.addText("Feature-based routing for plan-then-code prompting on HumanEval and BCB-Hard", {
    x: 0.75, y: 1.93, w: 9.7, h: 0.34,
    fontSize: 15, color: C.navy, margin: 0,
  });
  card(s, 0.75, 2.75, 5.75, 1.45, { fill: C.white, shadow: true });
  label(s, "Team", 1.05, 3.0, 1.3, C.cyan);
  bodyText(s, "Xiaoyang Cao | [insert email]\nSupriya Lall | [insert email]", 1.05, 3.35, 4.9, 0.58, 14);
  card(s, 7.1, 2.75, 4.95, 1.45, { fill: "EAF2FF", line: "C9DAFF" });
  label(s, "Study scope", 7.4, 3.0, 1.5, C.blue);
  bodyText(s, "HumanEval model routing\nBCB-Hard baseline failure audit", 7.4, 3.35, 4.2, 0.55, 13);
  s.addShape(pptx.ShapeType.line, { x: 0.75, y: 5.15, w: 11.5, h: 0, line: { color: C.grid, pt: 1.2 } });
  metric(s, "164", "HumanEval tasks", 0.75, 5.48, 2.2, C.blue);
  metric(s, "9", "task-level features", 3.15, 5.48, 2.3, C.cyan);
  metric(s, "10", "decomposition-only wins", 5.65, 5.48, 2.5, C.green);
  metric(s, "110", "BCB baseline failures", 8.35, 5.48, 2.5, C.violet);
  footer(s, 1);
  notes(s, [
    "Timing: 0:00-0:55.",
    "Hi, we are presenting our project, When Does Task Decomposition Help? The broad motivation is that decomposition sounds obviously useful for coding agents: ask the model to plan first, then code. But in practice it also costs more tokens and latency, and it can sometimes introduce extra mistakes. So our project treats decomposition as a routing problem rather than a universal prompting rule.",
    "My focus was the HumanEval and BigCodeBench-Hard analysis. Xiaoyang focused on the SWE-Bench side of the project. In this deck I will explain the formalization, the model, the evaluation, and what we found about where decomposition actually beats a direct baseline.",
    "The headline is: on HumanEval, decomposition helps a small but real subset of tasks, and a conservative router can capture that. On BCB-Hard, the direct baseline fails much more often, but decomposition only fixes a few of those failures."
  ]);
}

// Slide 2
{
  const s = pptx.addSlide();
  addHeader(s, "Problem and formalization", "When should an LLM decompose a coding task?");
  card(s, 0.75, 1.6, 4.1, 4.6, { fill: C.white, shadow: true });
  label(s, "Decision", 1.05, 1.9, 1.2, C.blue);
  bodyText(s, "For each task, choose either the direct baseline prompt or a decomposition prompt before running the model.", 1.05, 2.28, 3.45, 0.75, 13.5);
  s.addShape(pptx.ShapeType.line, { x: 1.2, y: 3.5, w: 3.1, h: 0, line: { color: C.grid, pt: 1 } });
  bodyText(s, "Input: task-level structural features x\nLabel: y = 1 iff decomposition passes and baseline fails\nPolicy: route to decomposition when P(y=1 | x) >= threshold", 1.05, 3.85, 3.5, 1.15, 12.6);
  card(s, 5.35, 1.6, 6.95, 4.6, { fill: "FDFEFE", shadow: true });
  label(s, "Formalization", 5.65, 1.9, 1.8, C.cyan);
  const steps = [
    ["Task", "HumanEval prompt"],
    ["Features", "size, AST, coupling, lexical decomposability"],
    ["Classifier", "XGBoost predicts decomposition benefit"],
    ["Routing", "baseline unless predicted benefit is high"],
    ["Outcome", "Pass@1 and estimated prompt cost"],
  ];
  addMiniTable(s, steps, 5.65, 2.32, 6.1, 2.75, 0.48, C.navy);
  pill(s, "Binary classification over tasks", 5.65, 5.48, 2.35, C.blue);
  pill(s, "Routing policy", 8.25, 5.48, 1.55, C.cyan);
  pill(s, "Cost-aware evaluation", 10.05, 5.48, 1.7, C.green);
  footer(s, 2);
  notes(s, [
    "Timing: 0:55-1:55.",
    "The central problem is: given a coding task, should the system use the original direct prompt, or should it use a decomposition-style prompt? We formalize this as binary classification at the task level.",
    "For each task, we extract a feature vector x. The label y is one only when decomposition passes and the baseline fails. If both pass, we treat the baseline as sufficient, because it is cheaper. That choice matters: we are not just asking which prompt can solve the task, we are asking whether decomposition adds enough value to justify using it.",
    "Once we have probabilities from the classifier, the policy is simple: route to decomposition only when predicted benefit is above a threshold. Evaluation then compares that routed policy against two fixed policies: always use the direct baseline, or always use decomposition."
  ]);
}

// Slide 3
{
  const s = pptx.addSlide();
  addHeader(s, "ML challenges", "The target is rare, noisy, and structurally indirect");
  const items = [
    ["Rare positives", "Only 10 of 164 tasks are decomposition-only wins, so accuracy can look good even for weak classifiers."],
    ["Proxy features", "Concepts like subtask independence are not directly observable; we approximate them with static and lexical features."],
    ["Confounding", "Difficulty, code size, and decomposability can move together, making causal interpretation difficult."],
    ["Small data", "HumanEval is useful for controlled Pass@1 evaluation, but the sample is too small for high-capacity semantic models."],
  ];
  items.forEach((it, i) => {
    const x = i % 2 === 0 ? 0.75 : 6.7;
    const y = i < 2 ? 1.65 : 4.15;
    card(s, x, y, 5.25, 1.65, { fill: C.white, shadow: true });
    s.addText(String(i + 1).padStart(2, "0"), { x: x + 0.28, y: y + 0.28, w: 0.55, h: 0.28, fontSize: 13, bold: true, color: i === 0 ? C.red : C.blue, margin: 0 });
    s.addText(it[0], { x: x + 1.0, y: y + 0.26, w: 3.7, h: 0.28, fontSize: 15, bold: true, color: C.ink, margin: 0 });
    bodyText(s, it[1], x + 1.0, y + 0.68, 3.85, 0.62, 11.5, C.navy);
  });
  footer(s, 3);
  notes(s, [
    "Timing: 1:55-2:55.",
    "There are a few machine learning challenges that make this nontrivial. First, the positive class is rare. In HumanEval, only 10 of 164 tasks are decomposition-only wins. So a classifier can get high accuracy by almost never predicting the positive class. That is why we report AUPRC and routing outcomes, not accuracy alone.",
    "Second, the features are proxies. Decomposability is not directly measured. We approximate it using task length, AST size, external calls, imports, and lexical hints of compositionality or independence.",
    "Third, there are confounds. Difficulty and decomposability may be correlated, and code size may sometimes behave like a dataset or benchmark identity signal.",
    "Finally, the data are small. That pushes us toward a tabular model and away from a high-capacity neural model as the primary method."
  ]);
}

// Slide 4
{
  const s = pptx.addSlide();
  addHeader(s, "Approach 1", "Run paired HumanEval experiments, then learn from task features");
  card(s, 0.75, 1.6, 11.75, 4.9, { fill: C.white, shadow: true });
  const xs = [1.15, 3.45, 5.75, 8.05, 10.35];
  const labels = ["HumanEval task", "Direct baseline", "Plan-then-code", "Paired label", "Router eval"];
  const sub = ["164 prompts", "original prompt", "planning appendix", "decomp pass, base fail", "success + cost"];
  xs.forEach((x, i) => {
    s.addShape(pptx.ShapeType.roundRect, {
      x, y: 2.55, w: 1.55, h: 1.05, rectRadius: 0.08,
      fill: { color: i === 0 ? "EEF4FF" : i === 3 ? "E9F8F0" : C.white },
      line: { color: i === 3 ? "A7D8BC" : "C9D6E5", pt: 1 },
    });
    s.addText(labels[i], { x: x + 0.12, y: 2.75, w: 1.31, h: 0.22, fontSize: 9.5, bold: true, color: C.ink, align: "center", margin: 0, fit: "shrink" });
    s.addText(sub[i], { x: x + 0.1, y: 3.08, w: 1.35, h: 0.18, fontSize: 7.5, color: C.muted, align: "center", margin: 0, fit: "shrink" });
    if (i < xs.length - 1) {
      s.addShape(pptx.ShapeType.line, { x: x + 1.68, y: 3.07, w: 0.52, h: 0, line: { color: C.blue, pt: 1.2, beginArrowType: "none", endArrowType: "triangle" } });
    }
  });
  label(s, "Labeling rule", 1.15, 4.55, 1.7, C.green);
  bodyText(s, "Positive iff decomposition passes and the baseline fails. Both-pass cases are treated as baseline-sufficient because the direct prompt has lower overhead.", 1.15, 4.9, 4.7, 0.72, 12.3);
  label(s, "Why paired?", 6.55, 4.55, 1.2, C.blue);
  bodyText(s, "Every task has both outcomes, so routing can be compared against fixed policies on exactly the same tasks.", 6.55, 4.9, 4.7, 0.65, 12.3);
  footer(s, 4);
  notes(s, [
    "Timing: 2:55-4:00.",
    "Our experimental unit is a paired task. For each HumanEval task, we run the baseline prompt and the plan-then-code prompt. Then we compare their pass or fail outcomes under the benchmark tests.",
    "The plan-then-code condition is not a separate agent architecture. It is a prompt appendix that asks the model to write a plan and then code. This keeps the intervention simple: the base model, task, and scoring harness stay the same, while the prompt strategy changes.",
    "The label is positive only for a clean flip: baseline fails, decomposition passes. If both pass, that is not a decomposition win for our routing objective, because the direct prompt solved the task with lower overhead.",
    "This paired setup gives us a fair downstream comparison. The classifier-routed policy chooses per task, and we compare its total success rate and estimated cost against always-baseline and always-decomposition on the same task set."
  ]);
}

// Slide 5
{
  const s = pptx.addSlide();
  addHeader(s, "Approach 2", "Use a low-dimensional XGBoost router because the data are tabular");
  card(s, 0.75, 1.55, 3.75, 4.9, { fill: C.white, shadow: true });
  label(s, "Feature groups", 1.05, 1.88, 1.5, C.blue);
  bulletList(s, [
    "Difficulty and scale: statement length, code length, AST nodes, functions, cyclomatic proxy",
    "Structure: imports, external calls, compositionality hints, independence hints",
    "Total feature vector: 9 features per task",
  ], 1.02, 2.3, 3.05, 2.0, 11.5);
  metric(s, "9", "features per task", 1.05, 5.35, 1.35, C.blue);
  metric(s, "164", "training examples", 2.55, 5.35, 1.45, C.cyan);
  card(s, 4.9, 1.55, 3.2, 4.9, { fill: "F8FBFF", line: "D7E5FF", shadow: true });
  label(s, "Model choice", 5.2, 1.88, 1.5, C.violet);
  bodyText(s, "XGBoost captures nonlinear feature interactions without needing a large dataset. It also preserves post-hoc interpretability through feature importance and ablation.", 5.2, 2.32, 2.45, 1.35, 12.5);
  s.addShape(pptx.ShapeType.line, { x: 5.25, y: 4.05, w: 2.35, h: 0, line: { color: "CBD8EA", pt: 1 } });
  bodyText(s, "Class imbalance is handled with scale_pos_weight = n_negative / n_positive.", 5.2, 4.4, 2.45, 0.85, 12);
  card(s, 8.55, 1.55, 3.75, 4.9, { fill: C.white, shadow: true });
  label(s, "Alternative considered", 8.85, 1.88, 2.15, C.amber);
  bodyText(s, "A transformer encoder such as CodeBERT could capture richer semantics from prompt text and code context.", 8.85, 2.32, 2.9, 0.85, 12.2);
  bodyText(s, "We did not use it as the primary method because HumanEval is small and interpretability is central to the research question.", 8.85, 3.65, 2.9, 1.0, 12.2);
  pill(s, "Feature-based first", 8.85, 5.45, 1.7, C.green);
  footer(s, 5);
  notes(s, [
    "Timing: 4:00-5:05.",
    "Our primary model is XGBoost over nine task-level features. Five are difficulty or scale proxies: statement length, code length, AST node count, number of functions, and a cyclomatic complexity approximation. Four are structural proxies: imports, external calls, compositionality hints, and lexical independence hints.",
    "This model matches the problem structure because our input is low-dimensional tabular data. XGBoost can capture nonlinear interactions, but it does not require the amount of data a transformer classifier would need. It also gives feature importances and supports ablation by feature group.",
    "We considered a transformer approach, such as CodeBERT over the prompt and code context. That could capture richer semantics, but it is less interpretable and more data-hungry. Since our goal is not just prediction but understanding what properties predict decomposition benefit, the feature-based model is a better fit for the first pass."
  ]);
}

// Slide 6
{
  const s = pptx.addSlide();
  addHeader(s, "Evaluation", "We evaluate both prediction quality and downstream routing value");
  card(s, 0.75, 1.55, 5.25, 4.95, { fill: C.white, shadow: true });
  label(s, "Classification metrics", 1.05, 1.88, 2.2, C.blue);
  addMiniTable(s, [
    ["Metric", "Why it matters"],
    ["AUROC", "Ranks positive tasks above negatives"],
    ["AUPRC", "More informative under rare positives"],
    ["F1", "Checks positive prediction quality"],
    ["Accuracy", "Reported, but can be misleading"],
  ], 1.05, 2.3, 4.55, 2.8, 0.48, C.navy);
  card(s, 6.55, 1.55, 5.75, 4.95, { fill: C.white, shadow: true });
  label(s, "Routing metrics", 6.85, 1.88, 1.7, C.green);
  bodyText(s, "Compare classifier-routed behavior against two fixed policies:", 6.85, 2.28, 4.7, 0.35, 12.4);
  bulletList(s, [
    "Always-baseline: direct prompt for every task",
    "Always-decomposition: plan-then-code for every task",
    "Classifier-routed: decompose only when predicted useful",
  ], 6.85, 2.78, 4.75, 1.25, 12);
  s.addShape(pptx.ShapeType.line, { x: 6.85, y: 4.35, w: 4.75, h: 0, line: { color: C.grid, pt: 1 } });
  bodyText(s, "Success rate is Pass@1. Estimated cost uses baseline = 1.0 and decomposition = 2.0.", 6.85, 4.7, 4.65, 0.72, 12.5);
  footer(s, 6);
  notes(s, [
    "Timing: 5:05-5:55.",
    "We evaluate in two layers. The first layer is ordinary classification: AUROC, AUPRC, F1, and accuracy. AUROC tells us whether the model ranks decomposition-beneficial tasks above others. AUPRC is especially important because positives are rare.",
    "The second layer is the more important one for this project: routing value. We ask whether the classifier-routed policy improves or preserves Pass@1 while decomposing fewer tasks. We compare against always-baseline and always-decomposition.",
    "We also track estimated cost. In the checked-in evaluation, baseline cost is one and decomposition cost is two. That is a simple proxy for additional prompting and inference overhead. So a useful router should either improve success rate, reduce cost, or ideally do both."
  ]);
}

// Slide 7
{
  const s = pptx.addSlide();
  addHeader(s, "Results", "Routing matches the intuition: decompose rarely, but not never");
  card(s, 0.75, 1.45, 4.15, 4.95, { fill: C.white, shadow: true });
  label(s, "Policy outcomes", 1.05, 1.8, 1.6, C.blue);
  addMiniTable(s, [
    ["Policy", "Success", "Cost"],
    ["Always-baseline", "85.98%", "1.00"],
    ["Always-decomp", "89.02%", "2.00"],
    ["XGBoost-routed", "92.07%", "1.06"],
  ], 1.05, 2.23, 3.5, 2.25, 0.48, C.navy);
  metric(s, "6.10%", "tasks routed to decomposition", 1.05, 5.1, 2.9, C.green);
  card(s, 5.25, 1.45, 3.15, 4.95, { fill: "F8FBFF", line: "D7E5FF", shadow: true });
  label(s, "Classifier quality", 5.55, 1.8, 1.9, C.violet);
  metric(s, "0.480", "AUROC", 5.55, 2.35, 1.35, C.violet);
  metric(s, "0.076", "AUPRC", 6.95, 2.35, 1.15, C.violet);
  bodyText(s, "Classification is near chance because the positive class is very small: 10 positive tasks out of 164.", 5.55, 3.75, 2.2, 0.85, 11.4);
  pill(s, "Interpret with caution", 5.55, 5.45, 1.8, C.amber, C.ink);
  card(s, 8.75, 1.45, 3.55, 4.95, { fill: C.white, shadow: true });
  label(s, "Interpretation", 9.05, 1.8, 1.6, C.green);
  bulletList(s, [
    "Decomposition helps a small subset of HumanEval tasks",
    "Routing is mainly a cost-control policy",
    "Code-size features carry the strongest signal",
    "Current structural proxies miss some semantic cues",
  ], 9.05, 2.28, 2.75, 2.35, 11.2);
  footer(s, 7);
  notes(s, [
    "Timing: 5:55-7:05.",
    "On HumanEval, the always-baseline strategy solves 85.98 percent of tasks, while always-decomposition solves 89.02 percent. So decomposition has a small net gain of about three percentage points.",
    "The fitted XGBoost router reaches 92.07 percent success with an estimated cost of 1.06. It routes only 6.10 percent of tasks to decomposition. This suggests the value of decomposition is sparse: it is helpful sometimes, but not worth applying universally.",
    "At the same time, the classification metrics are modest. AUROC is about 0.48 and AUPRC is about 0.076. That means we should be careful about overclaiming predictive quality. With only 10 positive HumanEval examples, the metric estimates are noisy.",
    "The interpretation is: decomposition benefit is real on a subset of tasks, and routing can act as a cost-control mechanism, but the current features do not fully capture the underlying semantic signal."
  ]);
}

// Slide 8
{
  const s = pptx.addSlide();
  addHeader(s, "BCB-Hard stress test", "The direct baseline mostly fails on harder library/API tasks");
  card(s, 0.75, 1.45, 3.55, 4.95, { fill: C.white, shadow: true });
  label(s, "Outcome counts", 1.05, 1.8, 1.75, C.blue);
  metric(s, "110 / 148", "baseline failures", 1.05, 2.35, 2.25, C.red);
  metric(s, "8", "failures fixed by plan-then-code", 1.05, 3.6, 2.65, C.green);
  metric(s, "102", "tasks both strategies fail", 1.05, 4.85, 2.4, C.violet);
  card(s, 4.75, 1.45, 3.65, 4.95, { fill: "F8FBFF", line: "D7E5FF", shadow: true });
  label(s, "Where baseline fails", 5.05, 1.8, 2.1, C.cyan);
  addMiniTable(s, [
    ["Pattern", "Fails"],
    ["Plotting / visualization", "41"],
    ["Data wrangling / tables", "33"],
    ["General library/API use", "13"],
    ["Web / file I/O", "12"],
  ], 5.05, 2.25, 2.95, 2.75, 0.48, C.navy);
  card(s, 8.85, 1.45, 3.45, 4.95, { fill: C.white, shadow: true });
  label(s, "Interpretation", 9.15, 1.8, 1.55, C.green);
  bulletList(s, [
    "BCB-Hard is not just longer; it stresses exact library behavior, hidden tests, files, web I/O, and plotting APIs",
    "Most failures are hidden mismatches rather than syntax errors",
    "Plan-then-code does not solve the hard benchmark; it slightly lowers overall pass rate",
  ], 9.15, 2.28, 2.65, 2.65, 10.8);
  pill(s, "Baseline: 25.7%", 9.15, 5.45, 1.45, C.blue);
  pill(s, "Plan: 25.0%", 10.75, 5.45, 1.2, C.amber, C.ink);
  footer(s, 8);
  notes(s, [
    "Timing: 7:05-8:10.",
    "We also looked at BigCodeBench-Hard as a harder stress test. Here the direct baseline mostly fails: 110 of 148 tasks fail, which is 74.3 percent. Plan-then-code fixes only eight of those failures, and 102 tasks fail under both strategies.",
    "This is important because it prevents a simplistic conclusion that decomposition helps more as tasks get harder. In BCB-Hard, many failures are not just missing a step in the prompt. They involve exact library behavior, file or web I/O, plotting APIs, hidden-test expectations, and environment-sensitive details.",
    "The main baseline failure categories are plotting and visualization, data wrangling or tables, general library/API use, and web or file I/O. Most failures are hidden mismatches rather than syntax errors.",
    "So decomposition does not work as a general capability upgrade. It helps when the model was close and forgot a requirement, but it does not reliably solve tasks where the model lacks exact implementation knowledge."
  ]);
}

// Slide 9
{
  const s = pptx.addSlide();
  addHeader(s, "When decomposition wins", "It helps when the baseline misses clauses in a compound task");
  card(s, 0.75, 1.45, 3.65, 4.95, { fill: C.white, shadow: true });
  label(s, "Observed flips", 1.05, 1.8, 1.5, C.green);
  metric(s, "18", "total plan-then-code wins over baseline", 1.05, 2.35, 2.7, C.green);
  metric(s, "10", "HumanEval baseline failures fixed", 1.05, 3.6, 2.7, C.blue);
  metric(s, "8", "BCB-Hard baseline failures fixed", 1.05, 4.85, 2.7, C.violet);
  card(s, 4.85, 1.45, 3.35, 4.95, { fill: "F8FBFF", line: "D7E5FF", shadow: true });
  label(s, "Common pattern", 5.15, 1.8, 1.65, C.cyan);
  bulletList(s, [
    "Explicit edge cases: fallback values, empty inputs, not-enough-resource branches",
    "Composite outputs: return multiple objects or satisfy two constraints at once",
    "Multi-step pipelines: validate, transform, compute, then format or plot",
    "Clause-heavy docstrings where missing one rule causes hidden-test failure",
  ], 5.15, 2.25, 2.55, 2.9, 10.6);
  card(s, 8.65, 1.45, 3.65, 4.95, { fill: C.white, shadow: true });
  label(s, "Why better than baseline?", 8.95, 1.8, 2.35, C.amber);
  bodyText(s, "The direct baseline often jumps straight to code. Plan-then-code first externalizes requirements, making the model more likely to enumerate branches and preserve small but test-critical details.", 8.95, 2.28, 2.85, 1.2, 11.6);
  s.addShape(pptx.ShapeType.line, { x: 8.95, y: 3.82, w: 2.85, h: 0, line: { color: C.grid, pt: 1 } });
  bodyText(s, "But it is not a capability upgrade: on BCB-Hard, most failures are exact library/API mismatches that planning alone does not fix.", 8.95, 4.18, 2.85, 0.95, 11.6);
  pill(s, "Best use: selective routing", 8.95, 5.52, 2.0, C.green);
  footer(s, 9);
  notes(s, [
    "Timing: 8:10-9:35.",
    "This slide summarizes where the alternate approach, plan-then-code, succeeds compared with the baseline. Across HumanEval and BCB-Hard, we observed 18 total cases where decomposition flips a baseline failure into a pass: 10 in HumanEval and 8 in BCB-Hard.",
    "The common pattern is not simply that the tasks are longer or harder. The structural feature effect sizes are small. Qualitatively, the wins are tasks with explicit edge cases, composite outputs, and multi-step pipelines. Examples include HumanEval tasks with fallback values, two-key sorting, rotations plus substring checks, or path constraints. In BCB-Hard, the wins include file-processing pipelines, subprocess monitoring, DataFrame construction, and forecast-plus-plot outputs.",
    "The reason decomposition helps is that the plan phase externalizes the requirements. A direct baseline often jumps straight to code and misses one clause. Plan-then-code forces the model to enumerate branches before writing the solution, so it is more likely to preserve small but test-critical details.",
    "The limitation is equally important. When the baseline fails because of exact API behavior or environment details, planning alone usually does not fix it. That is why selective routing is the best framing."
  ]);
}

// Slide 10
{
  const s = pptx.addSlide();
  addHeader(s, "Future work", "If we had more time, we would test whether the signal generalizes", "Not presented");
  pill(s, "OPTIONAL - NOT PRESENTED", 0.75, 1.35, 2.15, C.amber, C.ink);
  const items = [
    ["More trials per task", "Estimate success rates instead of single pass/fail labels, reducing label noise."],
    ["Semantic features", "Add embeddings or transformer-derived features while keeping a simpler model for interpretability."],
    ["Stronger decomposition", "Compare plan-then-code to self-debugging, iterative repair, and explicit subproblem generation."],
    ["Broader benchmarks", "Extend the BCB-Hard audit into a full cross-benchmark generalization experiment."],
  ];
  items.forEach((it, i) => {
    const x = i % 2 === 0 ? 0.75 : 6.7;
    const y = i < 2 ? 2.0 : 4.3;
    card(s, x, y, 5.25, 1.45, { fill: C.white, shadow: true });
    s.addText(it[0], { x: x + 0.28, y: y + 0.25, w: 3.9, h: 0.28, fontSize: 14, bold: true, color: C.ink, margin: 0 });
    bodyText(s, it[1], x + 0.28, y + 0.67, 4.55, 0.5, 11.4, C.navy);
  });
  footer(s, 10, "Not presented");
  notes(s, [
    "Not presented unless asked.",
    "If there is extra time during questions, use this as a concise future-work slide. The main extensions are repeated trials per task to reduce label noise, semantic features or embeddings, stronger decomposition variants such as self-debugging, and a fuller cross-benchmark generalization analysis."
  ]);
}

// Slide 11
{
  const s = pptx.addSlide();
  addHeader(s, "Contributions", "Who did what", "Required, not presented");
  pill(s, "REQUIRED - NOT PRESENTED", 0.75, 1.35, 2.1, C.blue);
  card(s, 0.75, 1.9, 5.45, 4.75, { fill: C.white, shadow: true });
  label(s, "Xiaoyang Cao", 1.05, 2.25, 1.8, C.blue);
  bulletList(s, [
    "Owned SWE-Bench-focused project work",
    "Prepared or reviewed SWE-Bench baseline and decomposition setup",
    "Contributed cross-benchmark framing and comparison against HumanEval/BCB-Hard",
  ], 1.05, 2.75, 4.35, 1.75, 12);
  bodyText(s, "Email: [insert email]", 1.05, 5.55, 2.6, 0.28, 11, C.muted);
  card(s, 6.75, 1.9, 5.45, 4.75, { fill: C.white, shadow: true });
  label(s, "Supriya Lall", 7.05, 2.25, 1.8, C.cyan);
  bulletList(s, [
    "Owned HumanEval and BCB-Hard analysis",
    "Ran local routing/evaluation pipelines from saved baseline and decomposition outputs",
    "Analyzed where decomposition beats the baseline and where BCB-Hard baseline failures persist",
  ], 7.05, 2.75, 4.35, 1.75, 12);
  bodyText(s, "Email: [insert email]", 7.05, 5.55, 2.6, 0.28, 11, C.muted);
  s.addText("Edit this slide if the exact division differs. It is intentionally marked not presented.", {
    x: 0.75, y: 6.9, w: 8.5, h: 0.22, fontSize: 8.5, color: C.muted, margin: 0,
  });
  footer(s, 11, "Not presented");
  notes(s, [
    "Required but not presented.",
    "This slide documents contribution split. Xiaoyang worked on the SWE-Bench side. Supriya worked on HumanEval and BCB-Hard analysis. Replace email placeholders before submission."
  ]);
}

pptx.writeFile({ fileName: "/Users/admin/Documents/6.c011_final/outputs/manual-humaneval-presentation/presentations/humaneval-decomposition-routing/output/humaneval-decomposition-routing.pptx" });
