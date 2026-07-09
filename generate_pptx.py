import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Theme Colors (Dark Theme with Teal & Sky Blue accents)
    BG_COLOR = RGBColor(15, 23, 42)      # Slate-900 (Deep dark slate background)
    CARD_BG = RGBColor(30, 41, 59)      # Slate-800 (Lighter slate for content panels)
    TEAL = RGBColor(45, 212, 191)       # Teal-400 (Primary accent color)
    SKY_BLUE = RGBColor(56, 189, 248)   # Sky-400 (Secondary accent color)
    ROSE = RGBColor(251, 113, 133)      # Rose-400 (Alert/Warning/Problem highlights)
    TEXT_WHITE = RGBColor(248, 250, 252) # Slate-50 (Crisp off-white body text)
    TEXT_MUTED = RGBColor(148, 163, 184) # Slate-400 (Muted gray for subtitles/details)

    blank_slide_layout = prs.slide_layouts[6]
    
    def apply_background(slide):
        # Add a full screen rectangle for background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background() # No border
        
    def add_title(slide, text, category=None):
        if category:
            cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
            tf = cat_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = category.upper()
            p.font.name = "Arial"
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = SKY_BLUE
            
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(0.8))
        tf = title_box.text_frame
        tf.word_wrap = True
        tf.margin_top = 0
        tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = text
        p.font.name = "Arial"
        p.font.size = Pt(30)
        p.font.bold = True
        p.font.color.rgb = TEAL

    def create_card(slide, left, top, width, height, title, items, title_color=SKY_BLUE, is_rose=False):
        # Draw base card shape
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = ROSE if is_rose else SKY_BLUE
        card.line.width = Pt(1.5)
        
        # Add a text frame on top of the card
        tx = slide.shapes.add_textbox(left + Inches(0.1), top + Inches(0.1), width - Inches(0.2), height - Inches(0.2))
        tf = tx.text_frame
        tf.word_wrap = True
        
        # Title of the card
        p_title = tf.paragraphs[0]
        p_title.text = title
        p_title.font.name = "Arial"
        p_title.font.size = Pt(18)
        p_title.font.bold = True
        p_title.font.color.rgb = title_color
        p_title.space_after = Pt(12)
        
        # Bullet items
        for item in items:
            p = tf.add_paragraph()
            p.text = item
            p.font.name = "Arial"
            p.font.size = Pt(13)
            p.font.color.rgb = TEXT_WHITE
            p.level = 0
            p.space_after = Pt(8)

    # ----------------------------------------------------
    # Slide 1: Title Slide
    # ----------------------------------------------------
    slide = prs.slides.add_slide(blank_slide_layout)
    apply_background(slide)
    
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.7), Inches(4.0))
    tf = title_box.text_frame
    tf.word_wrap = True
    
    p_main = tf.paragraphs[0]
    p_main.text = "FLOWSENSE AI"
    p_main.font.name = "Arial"
    p_main.font.size = Pt(56)
    p_main.font.bold = True
    p_main.font.color.rgb = TEAL
    p_main.space_after = Pt(8)
    
    p_sub = tf.add_paragraph()
    p_sub.text = "Intelligent Construction Supply Chain Brain"
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(24)
    p_sub.font.bold = True
    p_sub.font.color.rgb = TEXT_WHITE
    p_sub.space_after = Pt(16)
    
    p_desc = tf.add_paragraph()
    p_desc.text = "Automating multi-modal tracking, Bayesian delay forecasting, and critical path resequencing."
    p_desc.font.name = "Arial"
    p_desc.font.size = Pt(14)
    p_desc.font.color.rgb = TEXT_MUTED
    p_desc.space_after = Pt(40)
    
    p_footer = tf.add_paragraph()
    p_footer.text = "Kaya AI IIT India Hackathon 2026  |  Supply Chain Track"
    p_footer.font.name = "Arial"
    p_footer.font.size = Pt(12)
    p_footer.font.bold = True
    p_footer.font.color.rgb = SKY_BLUE

    # ----------------------------------------------------
    # Slide 2: The Problem - Silent Failures
    # ----------------------------------------------------
    slide = prs.slides.add_slide(blank_slide_layout)
    apply_background(slide)
    add_title(slide, "The Problem: Construction Supply Chains Fail Silently", "Industry Pain Points")
    
    col_width = Inches(3.6)
    col_gap = Inches(0.4)
    left_margin = Inches(0.8)
    top_pos = Inches(1.8)
    height_pos = Inches(4.5)
    
    create_card(slide, 
                left_margin, 
                top_pos, 
                col_width, 
                height_pos,
                "1. The Visibility Gap",
                [
                    "• Siloed operations cause critical data latency. McKinsey reports 40%+ of construction projects experience delays due to supply chain bottlenecks.",
                    "• Materials are ordered, but status updates disappear in unstructured email PDFs, chats, and field paper logs.",
                    "• Lack of automated verification of onsite delivery or physical material arrival."
                ],
                title_color=ROSE,
                is_rose=True)
                
    create_card(slide, 
                left_margin + col_width + col_gap, 
                top_pos, 
                col_width, 
                height_pos,
                "2. Unpredictable ETAs",
                [
                    "• Industry productivity growth has averaged just 1% annually over 20 years vs 2.8% globally, largely driven by logistics lag (McKinsey).",
                    "• Promised vendor delivery dates are accepted blindly, ignoring dynamic shipping bottlenecks or port disruptions.",
                    "• PMs lack early warning indicators for factory-floor fabrication delays."
                ],
                title_color=ROSE,
                is_rose=True)

    create_card(slide, 
                left_margin + (col_width + col_gap) * 2, 
                top_pos, 
                col_width, 
                height_pos,
                "3. Cascading Schedule Impact",
                [
                    "• A delay in a single critical component stalls downstream operations. Bent Flyvbjerg's 'Iron Law of Megaprojects' shows 9 out of 10 projects exceed schedules & budgets.",
                    "• Cost overruns of 50%+ are common, driven by unmitigated risk propagation.",
                    "• Schedules are static and disconnected from physical supply chain data."
                ],
                title_color=ROSE,
                is_rose=True)

    # ----------------------------------------------------
    # Slide 3: The Solution - FlowSense AI
    # ----------------------------------------------------
    slide = prs.slides.add_slide(blank_slide_layout)
    apply_background(slide)
    add_title(slide, "The Solution: Real-Time Intelligence & Delay Mitigation", "Introducing FlowSense")
    
    col_width = Inches(5.6)
    col_gap = Inches(0.5)
    left_margin = Inches(0.8)
    top_pos = Inches(1.8)
    height_pos = Inches(4.5)
    
    create_card(slide,
                left_margin,
                top_pos,
                col_width,
                height_pos,
                "Traditional Supply Chain Tracking",
                [
                    "• Fragmented Waste: Up to 30% of field labor time is wasted waiting for materials or equipment (World Economic Forum).",
                    "• Manual Overhead: PMs waste hours tracking orders via scattered spreadsheets, phone calls, and emails.",
                    "• Isolated Schedules: Planning tools are decoupled from material status, making proactive forecast impossible.",
                    "• Delayed Response: Action is taken only after a critical constraint has already delayed work."
                ],
                title_color=TEXT_MUTED)
                
    create_card(slide,
                left_margin + col_width + col_gap,
                top_pos,
                col_width,
                height_pos,
                "FlowSense: AI-Powered Control Center",
                [
                    "• Proactive & Agentic: Continuous signal extraction via multi-modal agents directly from email & photo feeds.",
                    "• Predictive Analytics: Sequential Bayesian updates compute dynamic, realistic ETAs under logistics uncertainty.",
                    "• Schedule-Linked: Maps material status onto the CPM network DAG, reducing schedule risk by up to 20% (Automation in Construction).",
                    "• Instant Mitigation: One-click AI-drafted vendor actions and resequencing recommendations."
                ],
                title_color=TEAL)

    # ----------------------------------------------------
    # Slide 4: System Architecture
    # ----------------------------------------------------
    slide = prs.slides.add_slide(blank_slide_layout)
    apply_background(slide)
    add_title(slide, "System Architecture: End-to-End Pipeline", "Technical Architecture")
    
    col_width = Inches(3.6)
    col_gap = Inches(0.4)
    left_margin = Inches(0.8)
    top_pos = Inches(1.8)
    height_pos = Inches(4.5)
    
    create_card(slide,
                left_margin,
                top_pos,
                col_width,
                height_pos,
                "Layer 1: Ingestion Layer",
                [
                    "Pipes multi-modal raw sources:",
                    "• Email Agent extracts status and milestones from inbox text.",
                    "• Vision Agent scans delivery photos, packing slips, and receipts.",
                    "• Schedule Parser ingests Primavera XML schedules to build dependency maps."
                ],
                title_color=SKY_BLUE)
                
    create_card(slide,
                left_margin + col_width + col_gap,
                top_pos,
                col_width,
                height_pos,
                "Layer 2: Intelligence Layer",
                [
                    "Core mathematical brain:",
                    "• Tracker resolves conflicting data (e.g. portal vs email) using recency weights.",
                    "• Bayesian Forecaster projects probabilistic ETAs under uncertainty.",
                    "• Cascade Engine propagates delay through NetworkX dependency DAG."
                ],
                title_color=TEAL)
                
    create_card(slide,
                left_margin + (col_width + col_gap) * 2,
                top_pos,
                col_width,
                height_pos,
                "Layer 3: Action Layer",
                [
                    "PM command cockpit interface:",
                    "• Live dashboard with donut KPIs, risk trends, and alerts.",
                    "• Schedule network graph showing critical path highlight.",
                    "• Action drafts for vendor escalation and fast scheduling adjustment."
                ],
                title_color=SKY_BLUE)

    # ----------------------------------------------------
    # Slide 5: Ingest & Tracker Layer
    # ----------------------------------------------------
    slide = prs.slides.add_slide(blank_slide_layout)
    apply_background(slide)
    add_title(slide, "Multi-Modal Ingest & Status Consensus Tracking", "Layer 1: Ingestion & Tracking")
    
    col_width = Inches(5.6)
    col_gap = Inches(0.5)
    left_margin = Inches(0.8)
    top_pos = Inches(1.8)
    height_pos = Inches(4.5)
    
    create_card(slide,
                left_margin,
                top_pos,
                col_width,
                height_pos,
                "Cognitive Data Ingest Agents",
                [
                    "• LangChain Email Agent: Scans emails for status flags (e.g., 'Fabrication delay', 'Ready to dispatch') and converts to structured JSON events.",
                    "• VLM Vision Agent: Scans receipts, packing lists, and site delivery photos. Extracts PO numbers, items, quantities, and quality checks.",
                    "• Primavera Ingest: Ingests XML schedules directly, matching activities to material requirements."
                ],
                title_color=SKY_BLUE)
                
    create_card(slide,
                left_margin + col_width + col_gap,
                top_pos,
                col_width,
                height_pos,
                "Dynamic Consensus Tracking",
                [
                    "• Conflict Resolution: Resolves mismatch (e.g. vendor portal says 'fabrication' but email says 'shipped').",
                    "• Recency & Reliability Weights: Calculates confidence using age of signal and trustworthiness of source.",
                    "• Auditable Traceability: Maintains a ledger of evidence, logging exactly why a state changed."
                ],
                title_color=TEAL)

    # ----------------------------------------------------
    # Slide 6: Intelligence Layer (Forecasting & Cascade)
    # ----------------------------------------------------
    slide = prs.slides.add_slide(blank_slide_layout)
    apply_background(slide)
    add_title(slide, "Bayesian Delay Forecasting & NetworkX Graph Cascade", "Layer 2: Intelligence Layer")
    
    col_width = Inches(5.6)
    col_gap = Inches(0.5)
    left_margin = Inches(0.8)
    top_pos = Inches(1.8)
    height_pos = Inches(4.5)
    
    create_card(slide,
                left_margin,
                top_pos,
                col_width,
                height_pos,
                "Bayesian Delay Forecaster",
                [
                    "• Probabilistic ETA: Computes delivery dates as a probability distribution, not a single point.",
                    "• Sequential Bayes Updates: Prior lead time curves are updated instantly as new lifecycle checkpoints are reached.",
                    "• Confidence Metric: Computes P50 / P90 arrival dates and overall delay probability to flag warning states early."
                ],
                title_color=TEAL)
                
    create_card(slide,
                left_margin + col_width + col_gap,
                top_pos,
                col_width,
                height_pos,
                "Schedule Cascade Engine",
                [
                    "• Directed Acyclic Graphs (DAG): Rebuilds the static Primavera project schedule in memory via NetworkX.",
                    "• Delay Propagation: Automatically calculates the impact of delayed material delivery across the dependency graph (BFS/DFS).",
                    "• Critical Path Alerts: Instantly flags delays that consume schedule buffer and delay final project completion."
                ],
                title_color=SKY_BLUE)

    # ----------------------------------------------------
    # Slide 7: Action Layer
    # ----------------------------------------------------
    slide = prs.slides.add_slide(blank_slide_layout)
    apply_background(slide)
    add_title(slide, "The Action Layer: PM Cockpit & One-Click Resolves", "Layer 3: Action Layer")
    
    col_width = Inches(5.6)
    col_gap = Inches(0.5)
    left_margin = Inches(0.8)
    top_pos = Inches(1.8)
    height_pos = Inches(4.5)
    
    create_card(slide,
                left_margin,
                top_pos,
                col_width,
                height_pos,
                "Command Center Dashboard",
                [
                    "• Dashboard Cockpit: Tracks key metrics, total POs, delay distributions, at-risk orders, and live system warnings.",
                    "• Schedule Graph Viz: Dynamic, interactive layout built with React Flow + Dagre showing task nodes and highlights.",
                    "• Material Lifecycle Stepper: Details each order phase from fabrication through site delivery."
                ],
                title_color=SKY_BLUE)
                
    create_card(slide,
                left_margin + col_width + col_gap,
                top_pos,
                col_width,
                height_pos,
                "One-Click AI-Drafted Actions",
                [
                    "• Email Drafting Agent: Creates structured, professional email escalations tailored to specific vendor delays.",
                    "• Resequencing Recommendations: Ranks schedule correction logic to bypass delayed nodes and save days.",
                    "• Human-in-the-Loop: Empowers PMs to review and execute suggested recovery tasks in one click."
                ],
                title_color=TEAL)

    # ----------------------------------------------------
    # Slide 8: Technical Architecture & Core Tech Stack
    # ----------------------------------------------------
    slide = prs.slides.add_slide(blank_slide_layout)
    apply_background(slide)
    add_title(slide, "Under the Hood: Modern Tech Stack", "Technology Architecture")
    
    col_width = Inches(3.6)
    col_gap = Inches(0.4)
    left_margin = Inches(0.8)
    top_pos = Inches(1.8)
    height_pos = Inches(4.5)
    
    create_card(slide,
                left_margin,
                top_pos,
                col_width,
                height_pos,
                "Frontend (Action Layer)",
                [
                    "• React 18 & Vite: High performance modular UI rendering.",
                    "• React Flow + Dagre: Automated graph auto-layouts for schedules.",
                    "• Recharts: Smooth analytics for lifecycle stages & status shares.",
                    "• Tailwind CSS: Custom dark / light theme configuration."
                ],
                title_color=SKY_BLUE)
                
    create_card(slide,
                left_margin + col_width + col_gap,
                top_pos,
                col_width,
                height_pos,
                "Backend & Database",
                [
                    "• FastAPI (Python): Asynchronous request handling and APIs.",
                    "• SQLite & SQLAlchemy: Structured schemas for orders, schedules, activities, and signal logs.",
                    "• Pydantic: Bulletproof type enforcement and JSON validation."
                ],
                title_color=TEAL)
                
    create_card(slide,
                left_margin + (col_width + col_gap) * 2,
                top_pos,
                col_width,
                height_pos,
                "AI / ML Modeling",
                [
                    "• NetworkX: Schedule DAG representation and traversal algorithms.",
                    "• NumPy & SciPy: Custom mathematical Bayesian updating logic.",
                    "• OpenAI / Groq: LLMs for email processing, photo VLM, and action drafts."
                ],
                title_color=SKY_BLUE)

    # ----------------------------------------------------
    # Slide 9: Why FlowSense Wins (Hackathon Value Proposition)
    # ----------------------------------------------------
    slide = prs.slides.add_slide(blank_slide_layout)
    apply_background(slide)
    add_title(slide, "Why FlowSense Wins: Real Value & Engineering Depth", "Value Proposition")
    
    col_width = Inches(5.6)
    col_gap = Inches(0.5)
    left_margin = Inches(0.8)
    top_pos = Inches(1.8)
    height_pos = Inches(4.5)
    
    create_card(slide,
                left_margin,
                top_pos,
                col_width,
                height_pos,
                "Engineering Depth over Wrapper Apps",
                [
                    "• Synthesizes multi-disciplinary models: VLM + LLMs + Bayesian statistics + Graph theory.",
                    "• Dual Core: Handles both ingest agents (unstructured data) and scheduled constraints (structured engineering data).",
                    "• Resilient Offline Mode: Falls back to rule-based parser and local mock data if API limits or credentials fail."
                ],
                title_color=TEAL)
                
    create_card(slide,
                left_margin + col_width + col_gap,
                top_pos,
                col_width,
                height_pos,
                "Real Industry Pain & Value",
                [
                    "• Targets the largest cost driver: Material shortages and supply chain fragmentation are the primary triggers of megaproject overruns (Flyvbjerg).",
                    "• Grounded in McKinsey Best Practices: Integrates long-lead material tracking and digital transparency onto a single source of truth.",
                    "• Direct ROI: Automates manual documentation, saving PMs 8+ hours a week while reducing wait-time wastes."
                ],
                title_color=SKY_BLUE)

    # ----------------------------------------------------
    # Slide 10: 2-Minute Pitch & Walkthrough Plan
    # ----------------------------------------------------
    slide = prs.slides.add_slide(blank_slide_layout)
    apply_background(slide)
    add_title(slide, "Live Demo Walkthrough: 2-Minute Script", "Hackathon Pitch Strategy")
    
    col_width = Inches(5.6)
    col_gap = Inches(0.5)
    left_margin = Inches(0.8)
    top_pos = Inches(1.8)
    height_pos = Inches(4.5)
    
    create_card(slide,
                left_margin,
                top_pos,
                col_width,
                height_pos,
                "0:00 - 1:00  |  Visualizing Chaos & Ingest",
                [
                    "• 0:00 - 0:20 (The Pain): Load the dashboard. Show the list of material orders and explain that several are at-risk, triggering critical path warnings.",
                    "• 0:20 - 0:40 (Multi-Modal Ingest): Upload a delivery receipt photo. Show the Vision Agent parsing it in real-time.",
                    "• 0:40 - 1:00 (Consensus): Explain how status updates to 'Delivered' automatically, recalculating confidence and audit history."
                ],
                title_color=SKY_BLUE)
                
    create_card(slide,
                left_margin + col_width + col_gap,
                top_pos,
                col_width,
                height_pos,
                "1:00 - 2:00  |  Intelligence & One-Click Resolve",
                [
                    "• 1:00 - 1:30 (Cascade Graph): View the interactive schedule graph. Show how a forecasted delayed steel beam propagates delay through downstream concrete pours.",
                    "• 1:30 - 1:50 (Mitigation): Click 'Draft Action' for the late PO. Show the AI-generated escalation mail detailing exact PO items.",
                    "• 1:50 - 2:00 (Close): Execute the simulated send. Pitch how FlowSense puts PMs back in control."
                ],
                title_color=TEAL)

    # ----------------------------------------------------
    # Slide 11: Summary & Future Vision
    # ----------------------------------------------------
    slide = prs.slides.add_slide(blank_slide_layout)
    apply_background(slide)
    add_title(slide, "FlowSense: The Future of Supply Chain Intelligence", "Conclusion")
    
    create_card(slide,
                Inches(1.8),
                Inches(1.8),
                Inches(9.733),
                Inches(4.5),
                "Key Takeaways & Future Outlook",
                [
                    "• Resolves Industry-Wide Fragmentation: Bridges raw multi-modal logistics with schedule CPM networks, solving the core challenge highlighted by McKinsey and WEF.",
                    "• Empowers Proactive Resiliency: Replaces slow, manual spreadsheets with Bayesian forecasting and graph-based cascade alerts.",
                    "• Modern Roadmap: Expanding into automated RFQ/subcontractor updates, and IoT/GPS container tracking to achieve full global supply chain transparency.",
                    "",
                    "FlowSense — The supply chain brain construction has been waiting for."
                ],
                title_color=TEAL)

    prs.save("FlowSense_AI_Hackathon_Pitch.pptx")
    print("Successfully generated FlowSense_AI_Hackathon_Pitch.pptx!")

if __name__ == "__main__":
    create_presentation()
