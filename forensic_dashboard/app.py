import sys
import pandas as pd
import plotly.express as px
from django.conf import settings
from django.core.management import execute_from_command_line
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.template import Template, Context

# --- 1. SETTINGS ---
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='forensic-audit-secret',
        ROOT_URLCONF=__name__,
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
        }],
    )

# --- 2. DATA LOGIC ---
def get_data():
    try:
        df = pd.read_csv('audit_data_5year.csv')
        ny_df = df[df['area_title'].str.contains("New York", na=False)].copy()
        return df, ny_df
    except FileNotFoundError:
        return pd.DataFrame(), pd.DataFrame()

# --- 3. TEMPLATES (The "HTML" inside the Python file) ---
BASE_TEMPLATE = """
<!DOCTYPE html><html><head>
    <title>OTB Forensic Audit</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        .sidebar { height: 100vh; background: #1a1a1a; color: white; padding: 20px; position: fixed; width: 240px; }
        .content { margin-left: 260px; padding: 40px; }
        .interpretation { background: #f8f9fa; border-left: 5px solid #dc3545; padding: 15px; margin-top: 20px; }
    </style></head><body>
    <div class="sidebar">
        <h4>🔍 Audit Menu</h4><hr>
        <a href="/" class="text-white d-block mb-2">1. Overview</a>
        <a href="/jobs/" class="text-white d-block mb-2">2. Jobs Audit</a>
        <a href="/ny/" class="text-white d-block mb-2">3. NY Deep-Dive</a>
        <a href="/efficiency/" class="text-white d-block mb-2">4. Efficiency Index</a>
    </div>
    <div class="content">{% block content %}{% endblock %}</div>
</body></html>
"""

# --- 4. VIEWS ---
def overview(request):
    html = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
        <h1>🏛️ Project Overview: The Taxpayer Price Tag</h1>
        <div class="card mb-4"><div class="card-body">
            <h3>The Logic (Non-Technical)</h3>
            <p>We calculate <b>Efficiency</b> by asking: <i>How much does it cost the taxpayer to support one job?</i></p>
            <p>1. <b>Data:</b> 5 years (2020-2024) of BLS Labor stats + Earmark data.</p>
            <p>2. <b>Goal:</b> Identify "Market Perversions" where gov spending > private salary.</p>
        </div></div>
        <div class="interpretation"><strong>Interpretation:</strong> This project identifies where the government is overpaying for economic growth.</div>
    """)
    return HttpResponse(html)

def jobs_audit(request):
    df, _ = get_data()
    fig = px.bar(df, x='area_title', y=['avg_annual_pay', 'Efficiency_Index'], barmode='group', title="Gov Spending vs Private Salary")
    chart_html = fig.to_html(full_html=False)
    html = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", f"<h1>📊 Jobs Audit</h1>{chart_html}<div class='interpretation'>Comparing what the worker takes home vs what the taxpayer pays.</div>")
    return HttpResponse(html)

def ny_focus(request):
    _, ny_df = get_data()
    table = ny_df[['area_title', 'avg_annual_pay', 'Efficiency_Index']].to_html(classes="table table-striped")
    html = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", f"<h1>🍎 New York Deep-Dive</h1><p>Focusing on the $1.88B NY Earmark pool.</p>{table}")
    return HttpResponse(html)

def efficiency(request):
    df, _ = get_data()
    fig = px.scatter(df, x='avg_annual_pay', y='Efficiency_Index', size='Efficiency_Index', color='year', title="The Efficiency/Taxpayer Burden Map")
    chart_html = fig.to_html(full_html=False)
    html = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", f"<h1>🛡️ Efficiency Index</h1>{chart_html}")
    return HttpResponse(html)

# --- 5. URLS ---
urlpatterns = [
    path('', overview),
    path('jobs/', jobs_audit),
    path('ny/', ny_focus),
    path('efficiency/', efficiency),
]

# --- 6. EXECUTION ---
if __name__ == "__main__":
    execute_from_command_line([sys.argv[0], 'runserver'])
