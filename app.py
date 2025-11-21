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
        to Wi-Fi/Network Infrastructure sales using Groq and the strictly defined criteria.
        """
        
        prompt = f"""
        EXTRACT AND ANALYZE THIS LINKEDIN PROFILE FOR Wi-Fi/NETWORK INFRASTRUCTURE SOLUTIONS
        
        LINKEDIN PROFILE TEXT:
        {linkedin_text}
        
        CONTEXT FOR ANALYSIS:
        - Our Company: Syntel + Altai Super Wi-Fi (Enterprise Wi-Fi/Network Infrastructure)
        - We sell Wi-Fi and network infrastructure solutions (Network Infra, Wi-Fi, IoT, OT/IT Integration)
        - Geography Focus: India
        
        STRICT RELEVANCE CRITERIA - FOLLOW EXACTLY:
        
        1. HIGH Relevance (Primary Buyers / Decision Makers)
        A person is HIGH only if they directly own IT infrastructure or warehouse/port digital systems.
        
        Conditions for HIGH (ANY of these):
        A. Direct ownership of network / IT infra:
           - Runs IT Infrastructure
           - Runs Network Infrastructure  
           - Runs Wi-Fi / wireless systems
           - Runs Data centers / connectivity
           - CIO / CTO / GM IT / Head IT Infra
           - Any role that signs off network vendors
        
        B. Direct ownership of warehouse/port tech systems:
           - Head of Automation
           - Head of WMS / TOS
           - Head of Digital Transformation (only infra-heavy)
           - OT (Operational Technology) owner
           - Smart Port / Smart Warehouse lead
           - Engineering head responsible for scanners, IoT, rack systems, sensors
        
        C. Direct role in infra commissioning:
           - Infra project manager (IT/Tech)
           - Warehouse infrastructure lead
           - Port technology commissioning lead
           - They have: Budget authority, Technical evaluation responsibility, Vendor selection power
        
        2. MEDIUM Relevance (Influencers / Operational Stakeholders)
        A person is MEDIUM if they do NOT own infra but their operations depend on it.
        
        Conditions for MEDIUM (ANY of these):
        A. Operational leaders affected by connectivity:
           - COO
           - Head of Operations (Port / Warehouse / Terminal)
           - Yard Operations Lead
           - Marine Operations
           - Warehouse Managers
           - Supply Chain Ops leads (inside warehousing org)
        
        B. They influence decisions indirectly:
           - They face pain points like downtime, scanner issues, IoT drop-offs
           - They escalate issues to IT
           - They have process responsibility
           - They can introduce you to the real decision maker
        
        C. They partially oversee teams that touch tech:
           - Field technicians
           - On-ground warehouse staff
           - Service teams
           - Tech support but not infra owners
           - Ops people working with automation systems but not owning them
        
        3. LOW Relevance (Peripheral / Not connected to infra)
        A person is LOW if their role does not touch infra or operations tech, even if they are senior.
        
        Conditions for LOW (ANY of these):
        A. Strategy / Planning / SCM not linked to infra:
           - Strategy roles
           - Business planning
           - Supply chain planners
           - Market intelligence
           - Procurement (general)
           - S&OP
           - Corporate strategy
           - Finance / MIS owners
        
        B. Corporate functions:
           - HR
           - Marketing
           - Admin
           - Sales
           - Customer service
        
        C. Ops roles that don't touch tech:
           - Transport/logistics (pure transportation, not warehouse logistics)
           - Vendor management
           - P&L operations
           - Purely commercial roles
           - People who work at sister companies (e.g., Adani Cement vs Adani Ports)
        
        D. Tech background but irrelevant function:
           - SAP consultant now in business role
           - Cloud/software roles not tied to infra
           - Digital but non-infra
        
        CRITICAL RULES:
        - HIGH ONLY when person directly owns IT Infrastructure / Networks / OT Systems
        - MEDIUM when person does not own infra but heavily depends on it for operations  
        - LOW when person has no stake in IT/Infra and does not run infra-dependent operations
        - COO/Operations Head: Only HIGH if they have direct infra commissioning authority, otherwise MEDIUM
        
        RETURN STRICT JSON FORMAT:
        {{
            "designation_relevance": "High/Medium/Low",
            "how_relevant": "Detailed analysis justifying the relevance score based on strict criteria.",
            "target_persona": "If Low/Medium, suggest the exact HIGH relevance persona to target",
            "next_step": "Recommended action: For High='Direct outreach', For Medium='Build influence and ask for intro to IT', For Low='Ask for referral or avoid'"
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
            "designation_relevance": "Low",
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
    st.markdown("Paste LinkedIn profile information below for analysis using strict relevance criteria.")
    
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
                        "Designation Relevance": [analysis_result.get('designation_relevance', 'Low')],
                        "How is he relevant": [analysis_result.get('how_relevant', 'No analysis available')],
                        "Target Persona": [analysis_result.get('target_persona', 'N/A')],
                        "Next Step": [analysis_result.get('next_step', 'N/A')]
                    }
                    
                    results_df = pd.DataFrame(results_data)
                    
                    st.header("Analysis Results")
                    
                    # Color code the relevance
                    relevance = analysis_result.get('designation_relevance', 'Low')
                    if relevance == "High":
                        st.success(" HIGH RELEVANCE - Primary Decision Maker")
                    elif relevance == "Medium":
                        st.warning(" MEDIUM RELEVANCE - Influencer/Stakeholder")
                    else:
                        st.info(" LOW RELEVANCE - Peripheral Role")
                    
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
                            "Designation Relevance": result.get('designation_relevance', 'Low'),
                            "How is he relevant": result.get('how_relevant', 'No analysis available'),
                            "Target Persona": result.get('target_persona', 'N/A'),
                            "Next Step": result.get('next_step', 'N/A')
                        })
                    
                    results_df = pd.DataFrame(results_data_list)
                    
                    st.header("Batch Analysis Results")
                    
                    # Show summary statistics
                    high_count = len([r for r in all_results if r.get('designation_relevance') == 'High'])
                    medium_count = len([r for r in all_results if r.get('designation_relevance') == 'Medium'])
                    low_count = len([r for r in all_results if r.get('designation_relevance') == 'Low'])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("High Relevance", high_count)
                    with col2:
                        st.metric("Medium Relevance", medium_count)
                    with col3:
                        st.metric("Low Relevance", low_count)
                    
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
