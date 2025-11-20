import streamlit as st
import pandas as pd
from groq import Groq
import json
import re
from typing import Dict, Any

# Initialize Groq client
@st.cache_resource
def init_groq_client():
    """Initializes the Groq client, caching the resource."""
    try:
        # st.secrets is used to securely access environment variables/secrets
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        return client
    except Exception as e:
        st.error(f"Failed to initialize Groq client. Please check your API key in Streamlit secrets: {e}")
        return None

class LinkedInProfileAnalyzer:
    def __init__(self, client):
        self.client = client
    
    def extract_and_analyze_profile(self, linkedin_text: str) -> Dict[str, Any]:
        """
        Extracts information from LinkedIn profile text and analyzes its relevance 
        to Wi-Fi/Network Infrastructure sales using Groq and strict criteria.
        """
        
        prompt = f"""
        EXTRACT AND ANALYZE THIS LINKEDIN PROFILE FOR Wi-Fi/NETWORK INFRASTRUCTURE SOLUTIONS
        
        LINKEDIN PROFILE TEXT:
        {linkedin_text}
        
        CONTEXT FOR ANALYSIS:
        - Our Company: Syntel + Altai Super Wi-Fi (Enterprise Wi-Fi/Network Infrastructure)
        - We sell Wi-Fi and network infrastructure solutions
        - Target Industries: Manufacturing, Warehouses, BFSI, Education, Healthcare, Hospitality, Telecom, IT/ITES, FMCG, Unicorns, PSUs/Government
        - Geography Focus: India
        
        THEN ANALYZE FOR:
        
        DESIGNATION RELEVANCE (Choose one: High/Medium/Low/No):
        
        Based on the provided Key Decision Makers and Influencers across industries:
        - **High**: The primary technical or financial owner (Key Decision Maker). This includes: CIO, CTO, Head of IT, IT Director, Head of Network, IT Infrastructure Manager, and any dual CFO/CTO role.
        
        - **Medium**: Strategic Operational Leaders and Financial Gatekeepers (Key Decision Makers or Major Influencers). This includes: COO, Operations Head, General Manager (Hotels), Chief Medical Officer (CMO), Strategic Procurement/Sourcing Head, and CFO/Finance Manager (where they influence capex/tech ROI). These roles sponsor initiatives or approve large budgets.
        
        - **Low**: Roles with operational dependency, site execution, or peripheral involvement (Minor Influencers or dependent users). This includes: Network Engineers, Facilities Manager, Procurement Manager/Purchase Head (non-strategic), Banking Operations Head, Department Heads, IT Operations Lead (zone-level), and application/software focus (WMS, SAP).
            
        - **No**: Completely irrelevant functional role (e.g., HR, Marketing, Sales/BD, roles clearly outside the scope of influence or dependency).
        
        **CRITICAL ENFORCEMENT: Use the Medium category for strategic operational leaders (COO, Operations Head) as requested, to separate them from the technical owners (High) and the tactical/peripheral roles (Low).**
        
        HOW IS HE/SHE RELEVANT (Detailed Write-up):
        - **IF HIGH/MEDIUM**: Detailed write-up justifying the score, including what the person is responsible for and specific duties that influence Wi-Fi/network decisions (aligning with intent trigger).
        - **IF LOW/NO**: **Concise** explanation of why they are not the ideal persona, focusing on the gap and the correct department/owner.
        
        IF NOT RELEVANT (i.e., Low or No relevance) → WHO TO TARGET + NEXT STEP:
        - **Target Persona**: Exact persona(s) we should target (e.g., Head of IT Infra, CIO, Head of Automation, GM Operations).
        - **Next Step**: Recommended next action for our sales rep (e.g., 'new connect request', 'warm introduction', 'email', 'tele').
        
        RETURN STRICT JSON FORMAT:
        {{
            "designation_relevance": "High/Medium/Low/No",
            "how_relevant": "Detailed write-up justifying the relevance score and decision influence.",
            "target_persona": "If Low/No, the exact person to target instead (e.g., Head of IT Infra)",
            "next_step": "If Low/No, the recommended next action for the sales rep."
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.3,
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response using regex
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                json_string = json_match.group().strip()
                return json.loads(json_string)
            else:
                return self._fallback_analysis()
                
        except Exception as e:
            st.error(f"Analysis error: {e}")
            return self._fallback_analysis()
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when Groq fails or JSON is unparseable."""
        return {
            "designation_relevance": "No",
            "how_relevant": "Manual analysis required - AI extraction failed.",
            "target_persona": "CIO/Head of IT Infrastructure",
            "next_step": "Manual review of profile needed."
        }

def main():
    st.set_page_config(
        page_title="LinkedIn Profile Analyzer",
        layout="wide"
    )
    
    st.title("LinkedIn Profile Analyzer for Wi-Fi Solutions")
    st.markdown("Paste LinkedIn profile information below for analysis using custom relevance criteria.")
    
    client = init_groq_client()
    if not client:
        st.error("Application cannot run without a valid Groq client.")
        return
    
    analyzer = LinkedInProfileAnalyzer(client)
    
    st.markdown("""
    <style>
    .dataframe {
        width: 100%;
    }
    .dataframe th {
        background-color: #1E3A8A;
        color: white;
        padding: 10px;
        text-align: left;
    }
    .dataframe td {
        padding: 8px;
        border-bottom: 1px solid #ddd;
    }
    .dataframe tr:hover {
        background-color: #f5f5f5;
    }
    </style>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Single Profile Analysis", "Batch Analysis"])
    
    with tab1:
        st.header("Single Profile Analysis")
        
        linkedin_text = st.text_area(
            "LinkedIn Profile Information",
            placeholder="Paste the entire LinkedIn profile text here...",
            height=300
        )
        
        if st.button("Analyze Profile", type="primary"):
            if not linkedin_text.strip():
                st.warning("Please paste LinkedIn profile information to analyze")
            else:
                with st.spinner("AI is analyzing the profile..."):
                    analysis_result = analyzer.extract_and_analyze_profile(linkedin_text)
                    
                    results_data = {
                        "Designation Relevance": [analysis_result.get('designation_relevance', 'No')],
                        "How is he relevant": [analysis_result.get('how_relevant', 'No analysis available')],
                        "Target Persona (If Low/No)": [analysis_result.get('target_persona', 'N/A')],
                        "Next Step (If Low/No)": [analysis_result.get('next_step', 'N/A')]
                    }
                    
                    results_df = pd.DataFrame(results_data)
                    
                    st.header("Analysis Results")
                    
                    st.dataframe(
                        results_df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="Download as CSV",
                            data=csv,
                            file_name="profile_analysis.csv",
                            mime="text/csv"
                        )
                    with col2:
                        tsv = results_df.to_csv(index=False, sep='\t')
                        st.download_button(
                            label="Download as TSV",
                            data=tsv,
                            file_name="profile_analysis.tsv",
                            mime="text/tab-separated-values"
                        )

    with tab2:
        st.header("Batch Profile Analysis")
        
        uploaded_file = st.file_uploader(
            "Upload text file with LinkedIn profiles", 
            type="txt", 
            help="Upload a .txt file where each profile is separated by '===PROFILE==='"
        )
        
        if uploaded_file is not None:
            content = uploaded_file.getvalue().decode("utf-8")
            profiles = [p.strip() for p in content.split("===PROFILE===") if p.strip()]
            
            st.info(f"Found **{len(profiles)}** profiles in file. Ready to analyze.")
            
            if st.button("Analyze All Profiles", type="primary"):
                
                analyzer = LinkedInProfileAnalyzer(client)
                all_results = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, profile_text in enumerate(profiles):
                    status_text.text(f"Analyzing profile {i+1}/{len(profiles)}...")
                    analysis = analyzer.extract_and_analyze_profile(profile_text)
                    all_results.append(analysis)
                    progress_bar.progress((i + 1) / len(profiles))
                
                status_text.text("Batch analysis complete.")
                
                if all_results:
                    results_data_list = []
                    for result in all_results:
                        results_data_list.append({
                            "Designation Relevance": result.get('designation_relevance', 'No'),
                            "How is he relevant": result.get('how_relevant', 'No analysis available'),
                            "Target Persona (If Low/No)": result.get('target_persona', 'N/A'),
                            "Next Step (If Low/No)": result.get('next_step', 'N/A')
                        })
                    
                    results_df = pd.DataFrame(results_data_list)
                    
                    st.header("Batch Analysis Results")
                    
                    st.dataframe(
                        results_df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="Download as CSV",
                            data=csv,
                            file_name="batch_analysis.csv",
                            mime="text/csv"
                        )
                    with col2:
                        tsv = results_df.to_csv(index=False, sep='\t')
                        st.download_button(
                            label="Download as TSV",
                            data=tsv,
                            file_name="batch_analysis.tsv",
                            mime="text/tab-separated-values"
                        )

if __name__ == "__main__":
    main()
