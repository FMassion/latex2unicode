# Abdeckungsbericht

Quelle: `spickzettel.md` (410 verschiedene Formeln und LaTeX-Befehle).
Erzeugt mit `python3 tools/abdeckung.py`.

| Status | Anzahl | Bedeutung |
|---|---|---|
| OK | 370 | vollständig in Unicode umgesetzt |
| Ersatz | 7 | umgesetzt mit Ersatzzeichen (ᵀ für ⊤, * für ∗) |
| Grenze | 33 | Unicode hat das Hoch-/Tiefzeichen nicht; Ersatzschreibweise. Im Bild-Export der App als echte Hoch-/Tiefstellung bzw. gestapelt dargestellt |
| FEHLT | 0 | Befehl nicht unterstützt |

## Einzelergebnisse (FEHLT und Grenze zuerst)

| Status | LaTeX | Unicode-Ergebnis | Hinweis |
|---|---|---|---|
| Grenze | `\underset{Y}{\operatorname{Select}}(L, M, \Gamma, \rho, \delta, \pi)` | Select_Y(𝐿, 𝑀, Γ, ρ, δ, π) | Tiefstellung von 'Y' nicht vollständig in Unicode verfügbar (fehlt: Y) – Ersatzschreibweise verwendet. |
| Grenze | `E_{\text{visual}} \circ F_{\text{DE/TR}} \circ T_{\text{DE}\rightarrow\{\text{DE,TR}\}}(S)` | 𝐸ᵥᵢₛᵤₐₗ ∘ 𝐹_(DE/TR) ∘ 𝑇_(DE→{DE,TR})(𝑆) | Tiefstellung von 'DE/TR' nicht vollständig in Unicode verfügbar (fehlt: / D E R T) – Ersatzschreibweise verwendet.; Tiefstellung von 'DE→{DE,TR}' nicht vollständig in Unicode verfügbar (fehlt: D E R T { } →) – Ersatzschreibweise verwendet. |
| Grenze | `W \xrightarrow{\;A_H\;} P_H \qquad W \xrightarrow{\;A_M\;} P_M` | 𝑊 →^(A_H) 𝑃_H  𝑊 →^(A_M) 𝑃_M | Tiefstellung von 'H' nicht vollständig in Unicode verfügbar (fehlt: H) – Ersatzschreibweise verwendet.; Hochstellung von 'A_H' nicht vollständig in Unicode verfügbar (fehlt: _) – Ersatzschreibweise verwendet.; Tiefstellung von 'M' nicht vollständig in Unicode verfügbar (fehlt: M) – Ersatzschreibweise verwendet.; Hochstellung von 'A_M' nicht vollständig in Unicode verfügbar (fehlt: _) – Ersatzschreibweise verwendet. |
| Grenze | `\operatorname{Core}(S) \subseteq \operatorname{Recover}(y_i) \qquad \Delta(y_i, S) \leq \epsilon_G` | Core(𝑆) ⊆ Recover(𝑦ᵢ)  Δ(𝑦ᵢ, 𝑆) ≤ ϵ_G | Tiefstellung von 'G' nicht vollständig in Unicode verfügbar (fehlt: G) – Ersatzschreibweise verwendet. |
| Grenze | `D_{\text{effective}} = \frac{\text{korrekt erschlossene Propositionen}}{\text{Rezeptionszeit}\cdot(1+\lambda\,CL)}` | 𝐷_(effective) = (korrekt erschlossene Propositionen)/(Rezeptionszeit ⋅ (1 + λ 𝐶𝐿)) | Tiefstellung von 'effective' nicht vollständig in Unicode verfügbar (fehlt: c f) – Ersatzschreibweise verwendet. |
| Grenze | `H_{A1}: \text{Human+AI} > \text{Human}` | 𝐻_(A1) : Human+AI > Human | Tiefstellung von 'A1' nicht vollständig in Unicode verfügbar (fehlt: A) – Ersatzschreibweise verwendet. |
| Grenze | `H_C: P(\text{Path} \mid \text{Human+AI}) \neq P(\text{Path} \mid \text{Human})` | 𝐻_C : 𝑃(Path ∣ Human+AI) ≠ 𝑃(Path ∣ Human) | Tiefstellung von 'C' nicht vollständig in Unicode verfügbar (fehlt: C) – Ersatzschreibweise verwendet. |
| Grenze | `Y_{ij} = \beta_0 + \beta_1\,\text{Condition} + \ldots + u_{\text{participant}} + v_{\text{stimulus}} + \epsilon` | 𝑌ᵢⱼ = β₀ + β₁ Condition + … + 𝑢_(participant) + 𝑣ₛₜᵢₘᵤₗᵤₛ + ϵ | Tiefstellung von 'participant' nicht vollständig in Unicode verfügbar (fehlt: c) – Ersatzschreibweise verwendet. |
| Grenze | `\mathbb{R}^{m\times n}` | ℝ^(m×n) | Hochstellung von 'm×n' nicht vollständig in Unicode verfügbar (fehlt: ×) – Ersatzschreibweise verwendet. |
| Grenze | `\mathbb{R}_{\geq 0}` | ℝ_(≥0) | Tiefstellung von '≥0' nicht vollständig in Unicode verfügbar (fehlt: ≥) – Ersatzschreibweise verwendet. |
| Grenze | `\binom{n}{k}` | C(𝑛, 𝑘) | \binom ist im Klartext nicht stapelbar – als C(n, k) geschrieben. |
| Grenze | `\mathbf{1}_A` | 𝟏_A | Tiefstellung von 'A' nicht vollständig in Unicode verfügbar (fehlt: A) – Ersatzschreibweise verwendet. |
| Grenze | `\frac{e^{z_i}}{\sum_j e^{z_j}}` | 𝑒^(zᵢ)/(∑ⱼ 𝑒^(zⱼ)) | Hochstellung von 'zᵢ' nicht vollständig in Unicode verfügbar (fehlt: ᵢ) – Ersatzschreibweise verwendet.; Hochstellung von 'zⱼ' nicht vollständig in Unicode verfügbar (fehlt: ⱼ) – Ersatzschreibweise verwendet. |
| Grenze | `\lim_{x\to a} f(x)` | lim_(x→a) 𝑓(𝑥) | Tiefstellung von 'x→a' nicht vollständig in Unicode verfügbar (fehlt: →) – Ersatzschreibweise verwendet. |
| Grenze | `\sum_{n=0}^{\infty}` | ∑ₙ₌₀^∞ | Hochstellung von '∞' nicht vollständig in Unicode verfügbar (fehlt: ∞) – Ersatzschreibweise verwendet. |
| Grenze | `\lVert A\rVert_F` | ‖𝐴‖_F | Tiefstellung von 'F' nicht vollständig in Unicode verfügbar (fehlt: F) – Ersatzschreibweise verwendet. |
| Grenze | `\mathbb{E}_{x\sim p}[f(x)]` | 𝔼_(x∼p)[𝑓(𝑥)] | Tiefstellung von 'x∼p' nicht vollständig in Unicode verfügbar (fehlt: ∼) – Ersatzschreibweise verwendet. |
| Grenze | `\rho_{XY}` | ρ_(XY) | Tiefstellung von 'XY' nicht vollständig in Unicode verfügbar (fehlt: X Y) – Ersatzschreibweise verwendet. |
| Grenze | `\hat{\theta}_{\mathrm{MLE}}` | θ̂_(MLE) | Tiefstellung von 'MLE' nicht vollständig in Unicode verfügbar (fehlt: E L M) – Ersatzschreibweise verwendet. |
| Grenze | `f_X(x)` | 𝑓_X(𝑥) | Tiefstellung von 'X' nicht vollständig in Unicode verfügbar (fehlt: X) – Ersatzschreibweise verwendet. |
| Grenze | `F_X(x)` | 𝐹_X(𝑥) | Tiefstellung von 'X' nicht vollständig in Unicode verfügbar (fehlt: X) – Ersatzschreibweise verwendet. |
| Grenze | `\mathrm{CI}_{95\%}` | CI_(95%) | Tiefstellung von '95%' nicht vollständig in Unicode verfügbar (fehlt: %) – Ersatzschreibweise verwendet. |
| Grenze | `D_{\mathrm{KL}}(P \parallel Q)` | 𝐷_(KL)(𝑃 ∥ 𝑄) | Tiefstellung von 'KL' nicht vollständig in Unicode verfügbar (fehlt: K L) – Ersatzschreibweise verwendet. |
| Grenze | `f_\theta(x)` | 𝑓_θ(𝑥) | Tiefstellung von 'θ' nicht vollständig in Unicode verfügbar (fehlt: θ) – Ersatzschreibweise verwendet. |
| Grenze | `\theta \leftarrow \theta - \eta \nabla_\theta \mathcal{L}` | θ ← θ − η∇_θℒ | Tiefstellung von 'θ' nicht vollständig in Unicode verfügbar (fehlt: θ) – Ersatzschreibweise verwendet. |
| Grenze | `d_{\text{model}}` | 𝑑_(model) | Tiefstellung von 'model' nicht vollständig in Unicode verfügbar (fehlt: d) – Ersatzschreibweise verwendet. |
| Grenze | `D_{\text{formal}}` | 𝐷_(formal) | Tiefstellung von 'formal' nicht vollständig in Unicode verfügbar (fehlt: f) – Ersatzschreibweise verwendet. |
| Grenze | `\underbrace{\ldots}_{\text{Text}}` | …_(Text) | Tiefstellung von 'Text' nicht vollständig in Unicode verfügbar (fehlt: T) – Ersatzschreibweise verwendet. |
| Grenze | `A_H` | 𝐴_H | Tiefstellung von 'H' nicht vollständig in Unicode verfügbar (fehlt: H) – Ersatzschreibweise verwendet. |
| Grenze | `P_H` | 𝑃_H | Tiefstellung von 'H' nicht vollständig in Unicode verfügbar (fehlt: H) – Ersatzschreibweise verwendet. |
| Grenze | `A_M` | 𝐴_M | Tiefstellung von 'M' nicht vollständig in Unicode verfügbar (fehlt: M) – Ersatzschreibweise verwendet. |
| Grenze | `P_M` | 𝑃_M | Tiefstellung von 'M' nicht vollständig in Unicode verfügbar (fehlt: M) – Ersatzschreibweise verwendet. |
| Grenze | `\epsilon_G` | ϵ_G | Tiefstellung von 'G' nicht vollständig in Unicode verfügbar (fehlt: G) – Ersatzschreibweise verwendet. |
| Ersatz | `A^\top` | 𝐴ᵀ | Hochstellung: '⊤' durch Ersatzzeichen 'ᵀ' (U+1D40 MODIFIER LETTER CAPITAL T) dargestellt. |
| Ersatz | `x^\top y` | 𝑥ᵀ𝑦 | Hochstellung: '⊤' durch Ersatzzeichen 'ᵀ' (U+1D40 MODIFIER LETTER CAPITAL T) dargestellt. |
| Ersatz | `A = U\Sigma V^\top` | 𝐴 = 𝑈Σ𝑉ᵀ | Hochstellung: '⊤' durch Ersatzzeichen 'ᵀ' (U+1D40 MODIFIER LETTER CAPITAL T) dargestellt. |
| Ersatz | `\cos\theta = \dfrac{x^\top y}{\lVert x\rVert\,\lVert y\rVert}` | cos θ = 𝑥ᵀ𝑦/(‖𝑥‖ ‖𝑦‖) | Hochstellung: '⊤' durch Ersatzzeichen 'ᵀ' (U+1D40 MODIFIER LETTER CAPITAL T) dargestellt. |
| Ersatz | `\theta^*` | θ* | Hochstellung: '∗' durch Ersatzzeichen '*' (U+002A ASTERISK) dargestellt. |
| Ersatz | `\operatorname{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V` | softmax(𝑄𝐾ᵀ/√𝑑ₖ)𝑉 | Hochstellung: '⊤' durch Ersatzzeichen 'ᵀ' (U+1D40 MODIFIER LETTER CAPITAL T) dargestellt. |
| Ersatz | `x^*` | 𝑥* | Hochstellung: '∗' durch Ersatzzeichen '*' (U+002A ASTERISK) dargestellt. |
| OK | `...` | ... |  |
| OK | `A \approx B \ \land\ B \approx C \ \nRightarrow\ A \approx C` | 𝐴 ≈ 𝐵 ∧ 𝐵 ≈ 𝐶 ⇏ 𝐴 ≈ 𝐶 |  |
| OK | `P(A \mid B) = \frac{P(B \mid A)\,P(A)}{P(B)}` | 𝑃(𝐴 ∣ 𝐵) = (𝑃(𝐵 ∣ 𝐴) 𝑃(𝐴))/(𝑃(𝐵)) |  |
| OK | `Y_{ij} = \beta_0 + \beta_1 x_{ij} + u_i + \epsilon_{ij}` | 𝑌ᵢⱼ = β₀ + β₁𝑥ᵢⱼ + 𝑢ᵢ + ϵᵢⱼ |  |
| OK | `X = \langle S, A, G, C, R\rangle` | 𝑋 = ⟨𝑆, 𝐴, 𝐺, 𝐶, 𝑅⟩ |  |
| OK | `Y = \{y_1, \ldots, y_n\}` | 𝑌 = {𝑦₁, …, 𝑦ₙ} |  |
| OK | `F \circ T \neq T \circ F` | 𝐹 ∘ 𝑇 ≠ 𝑇 ∘ 𝐹 |  |
| OK | `\forall\,\text{Output}:\ \operatorname{Provenance}(\text{Output}) \neq \varnothing` | ∀ Output : Provenance(Output) ≠ ∅ |  |
| OK | `\operatorname{EC}(H, M) > 0` | EC(𝐻, 𝑀) > 0 |  |
| OK | `\approx` | ≈ |  |
| OK | `x \in X` | 𝑥 ∈ 𝑋 |  |
| OK | `i` | 𝑖 |  |
| OK | `n` | 𝑛 |  |
| OK | `x=0` | 𝑥 = 0 |  |
| OK | `n=1` | 𝑛 = 1 |  |
| OK | `\lambda \to 0` | λ → 0 |  |
| OK | `\alpha` | α |  |
| OK | `\beta` | β |  |
| OK | `\gamma` | γ |  |
| OK | `\delta` | δ |  |
| OK | `\Delta` | Δ |  |
| OK | `\epsilon` | ϵ |  |
| OK | `\varepsilon` | ε |  |
| OK | `\zeta` | ζ |  |
| OK | `\zeta(s)` | ζ(𝑠) |  |
| OK | `\eta` | η |  |
| OK | `\theta` | θ |  |
| OK | `\Theta` | Θ |  |
| OK | `\kappa` | κ |  |
| OK | `\lambda` | λ |  |
| OK | `\mu` | μ |  |
| OK | `\nu` | ν |  |
| OK | `\pi` | π |  |
| OK | `\Pi` | Π |  |
| OK | `\rho` | ρ |  |
| OK | `\sigma` | σ |  |
| OK | `\Sigma` | Σ |  |
| OK | `\tau` | τ |  |
| OK | `\phi` | ϕ |  |
| OK | `\varphi` | φ |  |
| OK | `\Phi` | Φ |  |
| OK | `\chi` | χ |  |
| OK | `\chi^2` | χ² |  |
| OK | `\psi` | ψ |  |
| OK | `\Psi` | Ψ |  |
| OK | `\omega` | ω |  |
| OK | `\Omega` | Ω |  |
| OK | `\mathbb{N}` | ℕ |  |
| OK | `\mathbb{Z}` | ℤ |  |
| OK | `\mathbb{Q}` | ℚ |  |
| OK | `\mathbb{R}` | ℝ |  |
| OK | `\mathbb{C}` | ℂ |  |
| OK | `\mathbb{R}^n` | ℝⁿ |  |
| OK | `m` | 𝑚 |  |
| OK | `[0,1]` | [0, 1] |  |
| OK | `(0,1)` | (0, 1) |  |
| OK | `\forall` | ∀ |  |
| OK | `\forall x \in \mathbb{R}: x^2 \geq 0` | ∀𝑥 ∈ ℝ : 𝑥² ≥ 0 |  |
| OK | `\exists` | ∃ |  |
| OK | `\exists x: x^2 = 4` | ∃𝑥 : 𝑥² = 4 |  |
| OK | `\exists!` | ∃! |  |
| OK | `\nexists` | ∄ |  |
| OK | `\land` | ∧ |  |
| OK | `A \land B` | 𝐴 ∧ 𝐵 |  |
| OK | `\lor` | ∨ |  |
| OK | `A \lor B` | 𝐴 ∨ 𝐵 |  |
| OK | `\lnot` | ¬ |  |
| OK | `\lnot A` | ¬𝐴 |  |
| OK | `\Rightarrow` | ⇒ |  |
| OK | `A \Rightarrow B` | 𝐴 ⇒ 𝐵 |  |
| OK | `\Leftarrow` | ⇐ |  |
| OK | `\Leftrightarrow` | ⇔ |  |
| OK | `A \Leftrightarrow B` | 𝐴 ⇔ 𝐵 |  |
| OK | `\iff` | ⟺ |  |
| OK | `\vdash` | ⊢ |  |
| OK | `\Gamma \vdash \varphi` | Γ ⊢ φ |  |
| OK | `\models` | ⊨ |  |
| OK | `\Gamma \models \varphi` | Γ ⊨ φ |  |
| OK | `\therefore` | ∴ |  |
| OK | `\because` | ∵ |  |
| OK | `\top` | ⊤ |  |
| OK | `\bot` | ⊥ |  |
| OK | `:=` | := |  |
| OK | `\coloneqq` | ≔ |  |
| OK | `f(x) := x^2` | 𝑓(𝑥) := 𝑥² |  |
| OK | `\equiv` | ≡ |  |
| OK | `a \equiv b \pmod n` | 𝑎 ≡ 𝑏 (mod 𝑛) |  |
| OK | `\blacksquare` | ■ |  |
| OK | `\square` | □ |  |
| OK | `\{a,b,c\}` | {𝑎, 𝑏, 𝑐} |  |
| OK | `a,b,c` | 𝑎, 𝑏, 𝑐 |  |
| OK | `\{x \mid P(x)\}` | {𝑥 ∣ 𝑃(𝑥)} |  |
| OK | `x` | 𝑥 |  |
| OK | `P` | 𝑃 |  |
| OK | `\in` | ∈ |  |
| OK | `x \in A` | 𝑥 ∈ 𝐴 |  |
| OK | `\notin` | ∉ |  |
| OK | `\subset` | ⊂ |  |
| OK | `\subseteq` | ⊆ |  |
| OK | `A \subseteq B` | 𝐴 ⊆ 𝐵 |  |
| OK | `\subsetneq` | ⊊ |  |
| OK | `\supseteq` | ⊇ |  |
| OK | `\cup` | ∪ |  |
| OK | `A \cup B` | 𝐴 ∪ 𝐵 |  |
| OK | `\cap` | ∩ |  |
| OK | `A \cap B` | 𝐴 ∩ 𝐵 |  |
| OK | `\setminus` | ∖ |  |
| OK | `A \setminus B` | 𝐴 ∖ 𝐵 |  |
| OK | `\varnothing` | ∅ |  |
| OK | `\emptyset` | ∅ |  |
| OK | `A^c` | 𝐴ᶜ |  |
| OK | `\overline{A}` | 𝐴̅ |  |
| OK | `A` | 𝐴 |  |
| OK | `A \times B` | 𝐴 × 𝐵 |  |
| OK | `(a,b)` | (𝑎, 𝑏) |  |
| OK | `A^n` | 𝐴ⁿ |  |
| OK | `\mathcal{P}(A)` | 𝒫(𝐴) |  |
| OK | `2^A` | 2ᴬ |  |
| OK | `\lvert A \rvert` | \|𝐴\| |  |
| OK | `\#A` | #𝐴 |  |
| OK | `\bigcup_i A_i` | ⋃ᵢ 𝐴ᵢ |  |
| OK | `\bigcap_i A_i` | ⋂ᵢ 𝐴ᵢ |  |
| OK | `\bigcup_i` | ⋃ᵢ |  |
| OK | `\bigcap_i` | ⋂ᵢ |  |
| OK | `\sqcup` | ⊔ |  |
| OK | `\uplus` | ⊎ |  |
| OK | `=` | = |  |
| OK | `\neq` | ≠ |  |
| OK | `<` | < |  |
| OK | `>` | > |  |
| OK | `\leq` | ≤ |  |
| OK | `\geq` | ≥ |  |
| OK | `\ll` | ≪ |  |
| OK | `\gg` | ≫ |  |
| OK | `\simeq` | ≃ |  |
| OK | `\cong` | ≅ |  |
| OK | `\sim` | ∼ |  |
| OK | `\propto` | ∝ |  |
| OK | `\prec` | ≺ |  |
| OK | `\succ` | ≻ |  |
| OK | `\perp` | ⊥ |  |
| OK | `\parallel` | ∥ |  |
| OK | `\mid` | ∣ |  |
| OK | `\not` | ̸ |  |
| OK | `\not\approx` | ≉ |  |
| OK | `\not\equiv` | ≢ |  |
| OK | `\nsim` | ≁ |  |
| OK | `\ncong` | ≇ |  |
| OK | `\nless` | ≮ |  |
| OK | `\ngtr` | ≯ |  |
| OK | `\nleq` | ≰ |  |
| OK | `\ngeq` | ≱ |  |
| OK | `\not\subset` | ⊄ |  |
| OK | `\nsubseteq` | ⊈ |  |
| OK | `\nmid` | ∤ |  |
| OK | `\nparallel` | ∦ |  |
| OK | `\not\perp` | ⊥̸ |  |
| OK | `\nRightarrow` | ⇏ |  |
| OK | `\nLeftrightarrow` | ⇎ |  |
| OK | `\nrightarrow` | ↛ |  |
| OK | `\nvdash` | ⊬ |  |
| OK | `\nvDash` | ⊭ |  |
| OK | `0 \approx 1` | 0 ≈ 1 |  |
| OK | `1 \approx 2` | 1 ≈ 2 |  |
| OK | `0 \not\approx 2` | 0 ≉ 2 |  |
| OK | `\to` | → |  |
| OK | `\rightarrow` | → |  |
| OK | `f: A \to B` | 𝑓 : 𝐴 → 𝐵 |  |
| OK | `x \to 0` | 𝑥 → 0 |  |
| OK | `\mapsto` | ↦ |  |
| OK | `x \mapsto x^2` | 𝑥 ↦ 𝑥² |  |
| OK | `\hookrightarrow` | ↪ |  |
| OK | `\twoheadrightarrow` | ↠ |  |
| OK | `\xrightarrow{f}` | →ᶠ |  |
| OK | `f` | 𝑓 |  |
| OK | `\leftarrow` | ← |  |
| OK | `x \leftarrow x+1` | 𝑥 ← 𝑥 + 1 |  |
| OK | `\uparrow` | ↑ |  |
| OK | `\downarrow` | ↓ |  |
| OK | `\rightsquigarrow` | ⇝ |  |
| OK | `\sum_{i=1}^{n} a_i` | ∑ᵢ₌₁ⁿ 𝑎ᵢ |  |
| OK | `a_1 + \dots + a_n` | 𝑎₁ + … + 𝑎ₙ |  |
| OK | `\prod_{i=1}^{n} a_i` | ∏ᵢ₌₁ⁿ 𝑎ᵢ |  |
| OK | `a_1 \cdot \ldots \cdot a_n` | 𝑎₁ ⋅ … ⋅ 𝑎ₙ |  |
| OK | `\cdot` | ⋅ |  |
| OK | `\times` | × |  |
| OK | `\frac{a}{b}` | 𝑎/𝑏 |  |
| OK | `a/b` | 𝑎/𝑏 |  |
| OK | `a^n` | 𝑎ⁿ |  |
| OK | `\sqrt{x}` | √𝑥 |  |
| OK | `\sqrt[n]{x}` | ⁿ√𝑥 |  |
| OK | `n!` | 𝑛! |  |
| OK | `n\cdot(n-1)\cdots 1` | 𝑛 ⋅ (𝑛 − 1)⋯1 |  |
| OK | `\lvert x \rvert` | \|𝑥\| |  |
| OK | `\lfloor x \rfloor` | ⌊𝑥⌋ |  |
| OK | `\lceil x \rceil` | ⌈𝑥⌉ |  |
| OK | `\bmod` | mod |  |
| OK | `\pmod{n}` | (mod 𝑛) |  |
| OK | `\pm` | ± |  |
| OK | `\mp` | ∓ |  |
| OK | `\circ` | ∘ |  |
| OK | `(f\circ g)(x) = f(g(x))` | (𝑓 ∘ 𝑔)(𝑥) = 𝑓(𝑔(𝑥)) |  |
| OK | `\ldots` | … |  |
| OK | `\cdots` | ⋯ |  |
| OK | `\vdots` | ⋮ |  |
| OK | `\ddots` | ⋱ |  |
| OK | `\max` | max |  |
| OK | `\min` | min |  |
| OK | `\sup` | sup |  |
| OK | `\inf` | inf |  |
| OK | `\arg\max_x f(x)` | arg maxₓ 𝑓(𝑥) |  |
| OK | `\arg\min_x f(x)` | arg minₓ 𝑓(𝑥) |  |
| OK | `B` | 𝐵 |  |
| OK | `f(x)` | 𝑓(𝑥) |  |
| OK | `f^{-1}` | 𝑓⁻¹ |  |
| OK | `1/f` | 1/𝑓 |  |
| OK | `f^2(x)` | 𝑓²(𝑥) |  |
| OK | `f(x)^2` | 𝑓(𝑥)² |  |
| OK | `f(f(x))` | 𝑓(𝑓(𝑥)) |  |
| OK | `\exp(x)` | exp(𝑥) |  |
| OK | `e^x` | 𝑒ˣ |  |
| OK | `\log x` | log 𝑥 |  |
| OK | `\ln x` | ln 𝑥 |  |
| OK | `\log_2 x` | log₂ 𝑥 |  |
| OK | `\ln` | ln |  |
| OK | `e` | 𝑒 |  |
| OK | `\log = \log_2` | log = log₂ |  |
| OK | `\log` | log |  |
| OK | `\log_2` | log₂ |  |
| OK | `\mathbb{1}[A]` | 𝟙[𝐴] |  |
| OK | `\operatorname{sign}(x)` | sign(𝑥) |  |
| OK | `\delta_{ij}` | δᵢⱼ |  |
| OK | `i=j` | 𝑖 = 𝑗 |  |
| OK | `\sigma(x)` | σ(𝑥) |  |
| OK | `\frac{1}{1+e^{-x}}` | 1/(1 + 𝑒⁻ˣ) |  |
| OK | `\operatorname{softmax}` | softmax |  |
| OK | `O(n)` | 𝑂(𝑛) |  |
| OK | `\Theta(n)` | Θ(𝑛) |  |
| OK | `\Omega(n)` | Ω(𝑛) |  |
| OK | `o(1)` | 𝑜(1) |  |
| OK | `\arg` | arg |  |
| OK | `a` | 𝑎 |  |
| OK | `\infty` | ∞ |  |
| OK | `f'(x)` | 𝑓′(𝑥) |  |
| OK | `\dfrac{df}{dx}` | 𝑑𝑓/𝑑𝑥 |  |
| OK | `\frac{df}{dx}` | 𝑑𝑓/𝑑𝑥 |  |
| OK | `\dot{x}` | 𝑥̇ |  |
| OK | `\partial` | ∂ |  |
| OK | `\dfrac{\partial f}{\partial x}` | ∂𝑓/∂𝑥 |  |
| OK | `\nabla f` | ∇𝑓 |  |
| OK | `\nabla \cdot F` | ∇ ⋅ 𝐹 |  |
| OK | `\Delta f` | Δ𝑓 |  |
| OK | `\nabla^2 f` | ∇²𝑓 |  |
| OK | `\int_a^b f(x)\,dx` | ∫ₐᵇ 𝑓(𝑥) 𝑑𝑥 |  |
| OK | `b` | 𝑏 |  |
| OK | `\oint` | ∮ |  |
| OK | `\iint` | ∬ |  |
| OK | `\iiint` | ∭ |  |
| OK | `\epsilon>0` | ϵ > 0 |  |
| OK | `\delta>0` | δ > 0 |  |
| OK | `\mathbf{x}` | 𝐱 |  |
| OK | `\vec{x}` | 𝑥⃗ |  |
| OK | `\boldsymbol{x}` | 𝒙 |  |
| OK | `\mathbf{A}` | 𝐀 |  |
| OK | `A^T` | 𝐴ᵀ |  |
| OK | `A^{-1}` | 𝐴⁻¹ |  |
| OK | `I` | 𝐼 |  |
| OK | `I_n` | 𝐼ₙ |  |
| OK | `\det(A)` | det(𝐴) |  |
| OK | `\operatorname{tr}(A)` | tr(𝐴) |  |
| OK | `\operatorname{rank}(A)` | rank(𝐴) |  |
| OK | `\langle x, y\rangle` | ⟨𝑥, 𝑦⟩ |  |
| OK | `x\cdot y` | 𝑥 ⋅ 𝑦 |  |
| OK | `\lVert x\rVert` | ‖𝑥‖ |  |
| OK | `\lVert x\rVert_2` | ‖𝑥‖₂ |  |
| OK | `_2` | ₂ |  |
| OK | `\lVert x\rVert_1` | ‖𝑥‖₁ |  |
| OK | `\hat{x}` | 𝑥̂ |  |
| OK | `\odot` | ⊙ |  |
| OK | `\otimes` | ⊗ |  |
| OK | `\oplus` | ⊕ |  |
| OK | `\mathbb{R}^3` | ℝ³ |  |
| OK | `\operatorname{span}` | span |  |
| OK | `\ker` | ker |  |
| OK | `\operatorname{im}` | im |  |
| OK | `Av = \lambda v` | 𝐴𝑣 = λ𝑣 |  |
| OK | `v` | 𝑣 |  |
| OK | `P(A)` | 𝑃(𝐴) |  |
| OK | `\Pr(A)` | Pr(𝐴) |  |
| OK | `P(A \mid B)` | 𝑃(𝐴 ∣ 𝐵) |  |
| OK | `P(A \cap B)` | 𝑃(𝐴 ∩ 𝐵) |  |
| OK | `X \perp Y` | 𝑋 ⊥ 𝑌 |  |
| OK | `X` | 𝑋 |  |
| OK | `Y` | 𝑌 |  |
| OK | `X \sim \mathcal{N}(\mu,\sigma^2)` | 𝑋 ∼ 𝒩(μ, σ²) |  |
| OK | `\sigma^2` | σ² |  |
| OK | `\mathcal{U}(a,b)` | 𝒰(𝑎, 𝑏) |  |
| OK | `\mathrm{Bernoulli}(p)` | Bernoulli(𝑝) |  |
| OK | `\mathrm{Bin}(n,p)` | Bin(𝑛, 𝑝) |  |
| OK | `\mathbb{E}[X]` | 𝔼[𝑋] |  |
| OK | `E(X)` | 𝐸(𝑋) |  |
| OK | `p` | 𝑝 |  |
| OK | `\operatorname{Var}(X)` | Var(𝑋) |  |
| OK | `\operatorname{Cov}(X,Y)` | Cov(𝑋, 𝑌) |  |
| OK | `r` | 𝑟 |  |
| OK | `\bar{x}` | 𝑥̄ |  |
| OK | `\hat{\theta}` | θ̂ |  |
| OK | `L(\theta)` | 𝐿(θ) |  |
| OK | `\ell(\theta)` | ℓ(θ) |  |
| OK | `p(x)` | 𝑝(𝑥) |  |
| OK | `P(X\leq x)` | 𝑃(𝑋 ≤ 𝑥) |  |
| OK | `H_0` | 𝐻₀ |  |
| OK | `H_1` | 𝐻₁ |  |
| OK | `1-\beta` | 1 − β |  |
| OK | `d` | 𝑑 |  |
| OK | `t` | 𝑡 |  |
| OK | `F` | 𝐹 |  |
| OK | `z` | 𝑧 |  |
| OK | `N` | 𝑁 |  |
| OK | `\mathrm{df}` | df |  |
| OK | `\beta_0` | β₀ |  |
| OK | `\beta_1,\dots` | β₁, … |  |
| OK | `u_i` | 𝑢ᵢ |  |
| OK | `v_k` | 𝑣ₖ |  |
| OK | `k` | 𝑘 |  |
| OK | `i,j` | 𝑖, 𝑗 |  |
| OK | `H(X)` | 𝐻(𝑋) |  |
| OK | `-\sum_x p(x)\log p(x)` | −∑ₓ 𝑝(𝑥) log 𝑝(𝑥) |  |
| OK | `H(X \mid Y)` | 𝐻(𝑋 ∣ 𝑌) |  |
| OK | `I(X;Y)` | 𝐼(𝑋; 𝑌) |  |
| OK | `Q` | 𝑄 |  |
| OK | `-\log p(x)` | −log 𝑝(𝑥) |  |
| OK | `\mathrm{PPL}` | PPL |  |
| OK | `\exp` | exp |  |
| OK | `\mathcal{L}(\theta)` | ℒ(θ) |  |
| OK | `\mathcal{D}` | 𝒟 |  |
| OK | `(x^{(i)}, y^{(i)})` | (𝑥⁽ⁱ⁾, 𝑦⁽ⁱ⁾) |  |
| OK | `y` | 𝑦 |  |
| OK | `\hat{y}` | 𝑦̂ |  |
| OK | `\lambda \lVert\theta\rVert^2` | λ‖θ‖² |  |
| OK | `\mathbf{h}` | 𝐡 |  |
| OK | `h_t` | ℎₜ |  |
| OK | `\mathbf{W}` | 𝐖 |  |
| OK | `\mathbf{b}` | 𝐛 |  |
| OK | `\operatorname{Attention}(Q,K,V)` | Attention(𝑄, 𝐾, 𝑉) |  |
| OK | `\mathcal{A}` | 𝒜 |  |
| OK | `\mathcal{L}` | ℒ |  |
| OK | `\mathcal{N}` | 𝒩 |  |
| OK | `\mathfrak{g}` | 𝔤 |  |
| OK | `\mathbb{E}` | 𝔼 |  |
| OK | `\mathbb{P}` | ℙ |  |
| OK | `\tilde{x}` | 𝑥̃ |  |
| OK | `x'` | 𝑥′ |  |
| OK | `x_i` | 𝑥ᵢ |  |
| OK | `x^{(i)}` | 𝑥⁽ⁱ⁾ |  |
| OK | `f(x;\theta)` | 𝑓(𝑥; θ) |  |
| OK | `\boxed{\ \ }` |  |  |
| OK | `S` | 𝑆 |  |
| OK | `G` | 𝐺 |  |
| OK | `C` | 𝐶 |  |
| OK | `R` | 𝑅 |  |
| OK | `\langle\ \rangle` | ⟨ ⟩ |  |
| OK | `\arg\max_x` | arg maxₓ |  |
| OK | `T` | 𝑇 |  |
| OK | `E` | 𝐸 |  |
| OK | `W` | 𝑊 |  |
| OK | `y_i` | 𝑦ᵢ |  |
| OK | `CL` | 𝐶𝐿 |  |
| OK | `H` | 𝐻 |  |
| OK | `M` | 𝑀 |  |
