import json
from fpdf import FPDF

# Example JSON data
data = {
    "executive_summary": {
        "problem_statement": "There is a growing need for personalized and affordable education solutions in the market.",
        "solution_statement": "An edtech startup like Byju's can provide personalized and affordable education solutions to students.",
        "value_proposition": "The edtech startup will provide students with access to high-quality educational content, personalized learning experiences, and affordable pricing.",
        "target_market": "The target market for the edtech startup is students from K-12.",
        "competitive_advantage": "The edtech startup will have a competitive advantage over other edtech companies by providing personalized and affordable education solutions.",
        "key_metrics": [
            "Number of users",
            "Monthly active users",
            "Revenue",
            "Profitability"
        ],
        "exit_strategy": "The exit strategy for the edtech startup is to be acquired by a larger education company."
    },
    "product_feasibility_analysis": {
        "market_analysis": {
            "market_size": "The global edtech market is expected to reach $404 billion by 2025.",
            "market_growth": "The edtech market is growing at a CAGR of 15%.",
            "target_market": "The target market for the edtech startup is students from K-12.",
            "customer_needs": "Students need personalized and affordable education solutions.",
            "competitive_landscape": "The competitive landscape for the edtech market is fragmented, with a number of small and large players."
        },
        "product_description": {
            "product_name": "Byju's",
            "product_description": "Byju's is an edtech startup that provides personalized and affordable education solutions to students.",
            "product_features": [
                "Personalized learning experiences",
                "High-quality educational content",
                "Affordable pricing"
            ]
        },
        "technical_feasibility": {
            "technology_stack": "The edtech startup will use a cloud-based technology stack.",
            "development_timeline": "The edtech startup will be developed in 6 months.",
            "development_cost": "The development cost for the edtech startup is $1 million."
        },
        "operational_feasibility": {
            "operations_plan": "The edtech startup will be operated by a team of experienced professionals.",
            "customer_support": "The edtech startup will provide customer support 24/7.",
            "marketing_plan": "The edtech startup will use a variety of marketing channels to reach its target market."
        },
        "financial_feasibility": {
            "revenue_model": "The edtech startup will generate revenue through subscriptions.",
            "cost_structure": "The edtech startup's cost structure will include costs for content development, marketing, and customer support.",
            "profitability_analysis": "The edtech startup is expected to be profitable within 3 years."
        },
        "risk_analysis": {
            "risks": [
                "Competition",
                "Regulatory changes",
                "Technology failures"
            ],
            "mitigation_strategies": [
                "The edtech startup will differentiate itself from the competition by providing personalized and affordable education solutions.",
                "The edtech startup will comply with all applicable regulations.",
                "The edtech startup will invest in a robust technology infrastructure."
            ]
        }
    },
    "reliability_analysis": {
        "reliability_metrics": [
            "Uptime",
            "Data integrity",
            "Security"
        ],
        "reliability_targets": [
            "99.9% uptime",
            "99.99% data integrity",
            "100% security"
        ],
        "reliability_measures": [
            "The edtech startup will use a cloud-based technology stack to ensure high uptime.",
            "The edtech startup will use a data backup and recovery system to ensure data integrity.",
            "The edtech startup will use a variety of security measures to protect user data."
        ]
    },
    "break_even_analysis": {
        "fixed_costs": "$1 million",
        "variable_costs": "$0.50 per user",
        "revenue_per_user": "$1.00",
        "break_even_point": "2 million users"
    },
    "conclusion_and_recommendations": {
        "conclusion": "The edtech startup is a feasible and viable business opportunity.",
        "recommendations": [
            "The edtech startup should focus on developing a strong product that meets the needs of its target market.",
            "The edtech startup should invest in marketing and customer support to reach its target market and build a loyal customer base.",
            "The edtech startup should monitor its key metrics and make adjustments as needed to ensure its success."
        ]
    },
    "appendices": [
        "Financial statements",
        "Market research report",
        "Technical specifications"
    ]
}

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Comprehensive Report', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

def generate_pdf(report_data):
    pdf = PDF()
    pdf.add_page()

    # Executive Summary
    pdf.chapter_title('Executive Summary')
    for key, value in report_data['executive_summary'].items():
        if isinstance(value, list):
            value = ', '.join(value)
        pdf.chapter_body(f"{key.replace('_', ' ').capitalize()}: {value}")

    # Product Feasibility Analysis
    pdf.chapter_title('Product Feasibility Analysis')
    for section, content in report_data['product_feasibility_analysis'].items():
        pdf.chapter_title(section.replace('_', ' ').capitalize())
        for key, value in content.items():
            if isinstance(value, list):
                value = ', '.join(value)
            pdf.chapter_body(f"{key.replace('_', ' ').capitalize()}: {value}")

    # Reliability Analysis
    pdf.chapter_title('Reliability Analysis')
    for key, value in report_data['reliability_analysis'].items():
        if isinstance(value, list):
            value = ', '.join(value)
        pdf.chapter_body(f"{key.replace('_', ' ').capitalize()}: {value}")

    # Break Even Analysis
    pdf.chapter_title('Break Even Analysis')
    for key, value in report_data['break_even_analysis'].items():
        pdf.chapter_body(f"{key.replace('_', ' ').capitalize()}: {value}")

    # Conclusion and Recommendations
    pdf.chapter_title('Conclusion and Recommendations')
    for key, value in report_data['conclusion_and_recommendations'].items():
        if isinstance(value, list):
            value = ', '.join(value)
        pdf.chapter_body(f"{key.replace('_', ' ').capitalize()}: {value}")

    # Appendices
    pdf.chapter_title('Appendices')
    pdf.chapter_body(', '.join(report_data['appendices']))

    pdf_output_path = "comprehensive_report.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path

# Generate the PDF
pdf_path = generate_pdf(data)
print(f"PDF generated and saved to: {pdf_path}")
