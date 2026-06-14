CSS_STYLING = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Apply Fonts */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

/* Global Dark Theme Overrides */
.stApp {
    background-color: #0A0D14;
    color: #E2E8F0;
}

/* Sidebar Custom Styling */
[data-testid="stSidebar"] {
    background-color: #0F131E;
    border-right: 1px solid #1E293B;
}

/* Tab Bar Custom Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 2px solid #1E293B;
}

.stTabs [data-baseweb="tab"] {
    background-color: #111827;
    border: 1px solid #1E293B;
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    padding: 8px 16px;
    color: #94A3B8;
    font-weight: 500;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #F8FAFC;
    background-color: #1F2937;
}

.stTabs [aria-selected="true"] {
    color: #818CF8 !important;
    background-color: #1E1B4B !important;
    border-color: #4F46E5 !important;
    font-weight: 600;
}

/* Custom Concept Cards */
.concept-card {
    background-color: #111827;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.concept-title {
    color: #818CF8;
    font-size: 1.15rem;
    font-weight: 600;
    margin-bottom: 10px;
    border-bottom: 1px solid #1E293B;
    padding-bottom: 6px;
}

/* Code sandbox background adjustment */
textarea {
    background-color: #090D16 !important;
    color: #F8FAFC !important;
    font-family: 'JetBrains Mono', monospace !important;
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
}

/* Custom terminal console for tests */
.terminal-window {
    background-color: #05070C;
    border: 1px solid #1E293B;
    border-radius: 8px;
    margin-top: 15px;
    overflow: hidden;
}

.terminal-header {
    background-color: #0F131E;
    border-bottom: 1px solid #1E293B;
    padding: 8px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.terminal-dots {
    display: flex;
    gap: 6px;
}

.dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}
.dot-red { background-color: #EF4444; }
.dot-yellow { background-color: #F59E0B; }
.dot-green { background-color: #10B981; }

.terminal-title {
    color: #64748B;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
}

.terminal-console {
    color: #F8FAFC;
    font-family: 'JetBrains Mono', monospace;
    border-left: 4px solid #EF4444;
    padding: 14px;
    max-height: 250px;
    overflow-y: auto;
    font-size: 0.85rem;
    white-space: pre-wrap;
    background-color: #05070C;
    margin: 0;
}

.terminal-success {
    color: #34D399;
    font-family: 'JetBrains Mono', monospace;
    border-left: 4px solid #10B981;
    padding: 14px;
    font-size: 0.85rem;
    background-color: #05070C;
    margin: 0;
}

/* Difficulty Badges */
.badge-easy {
    background-color: #064E3B;
    color: #6EE7B7;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
}
.badge-medium {
    background-color: #78350F;
    color: #FDE68A;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
}
.badge-hard {
    background-color: #7F1D1D;
    color: #FCA5A5;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
}

/* Group Cards */
.group-card {
    background: linear-gradient(135deg, #111827 0%, #0F172A 100%);
    border: 1px solid #1E293B;
    border-radius: 10px;
    padding: 16px 18px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    min-height: 100px;
}

.group-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    border-radius: 10px 10px 0 0;
}

.group-card:hover {
    transform: translateY(-3px);
    border-color: #4F46E5;
    box-shadow: 0 8px 25px -5px rgba(79, 70, 229, 0.25);
}

.group-card-active {
    border-color: #818CF8 !important;
    box-shadow: 0 0 0 1px #818CF8, 0 8px 25px -5px rgba(79, 70, 229, 0.3) !important;
}

.group-card-name {
    color: #F8FAFC;
    font-size: 0.95rem;
    font-weight: 600;
    margin-top: 6px;
}

.group-card-count {
    color: #64748B;
    font-size: 0.8rem;
    margin-top: 4px;
}

.group-card-emoji {
    font-size: 1.5rem;
}

/* Module Section Headers */
.module-section-header {
    color: #F8FAFC;
    font-size: 1.1rem;
    font-weight: 600;
    margin: 20px 0 12px 0;
    padding: 10px 14px;
    border-radius: 8px;
    border-left: 4px solid;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Progress Bar Animation */
@keyframes progressFill {
    from { width: 0%; }
}

.animated-progress {
    animation: progressFill 1.2s ease-out;
}

/* Search Results Table Header */
.table-header {
    display: grid;
    grid-template-columns: 0.8fr 2.5fr 2fr 2fr 2fr 1.2fr 1.8fr;
    gap: 10px;
    padding: 12px 0;
    border-bottom: 2px solid #1E293B;
    margin-bottom: 8px;
    font-weight: 600;
    color: #94A3B8;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Hero Section */
.hero-section {
    background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #0F172A 100%);
    border: 1px solid #1E293B;
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 24px;
    text-align: center;
}

.hero-title {
    background: linear-gradient(135deg, #818CF8, #C084FC, #F472B6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 8px;
}

.hero-subtitle {
    color: #94A3B8;
    font-size: 1rem;
    max-width: 600px;
    margin: 0 auto;
}

/* Stats Cards */
.stat-card {
    background-color: #111827;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
}

.stat-value {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #818CF8, #C084FC);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stat-label {
    color: #64748B;
    font-size: 0.8rem;
    font-weight: 500;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

</style>
"""
