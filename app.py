import streamlit as st
import pandas as pd
from groq import Groq
import json
import re
from typing import Dict

# Initialize Groq client
@st.cache_resource
def init_groq_client():
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        return client
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")
        return None

class LinkedInProfileAnalyzer:
    def __init__(self, client):
        self.client = client
    
    def extract_and_analyze_profile(self, linkedin_text: str) -> Dict:
        """Extract all information from LinkedIn profile text and analyze using Groq"""
        
        prompt = f"""
        EXTRACT AND ANALYZE THIS LINKEDIN PROFILE FOR Wi-Fi/NETWORK INFRASTRUCTURE SOLUTIONS
        
        LINKEDIN PROFILE TEXT:
        {linkedin_text}
        
        CONTEXT FOR ANALYSIS:
        - Our Company: Syntel + Altai Super Wi-Fi (Enterprise Wi-Fi/Network Infrastructure)
        - We sell to: CIO, CTO, IT Infrastructure Manager, Network Architect, Operations Head
        - Target Industries: Manufacturing, Warehouses, BFSI, Education, Healthcare, Hospitality
        - Geography Focus: India
        
        EXTRACT THESE DETAILS FROM THE PROFILE:
        1. Full Name
        2. Current Designation/Title
        3. Current Company
        4. Industry/Sector
        5. Location/Geography
        6. Key Responsibilities
        
        THEN ANALYZE FOR:
        
        DESIGNATION RELEVANCE (Choose one: High/Medium/Low/No):
        - High: Direct IT/Network infrastructure roles (CIO, CTO, IT Infrastructure Manager, Network Architect, Wireless Engineer)
        - Medium: Indirect influence (Operations Head, Facilities Manager, COO, Head of Plant)
        - Low: Limited involvement in IT decisions
        - No: No relevance to IT infrastructure
        
        HOW IS HE RELEVANT (Detailed Analysis):
        - What they are responsible for based on profile
        - How their role aligns with Wi-Fi/network infrastructure needs  
        - Their potential influence on IT buying decisions
        - Specific responsibilities that could influence network decisions
        - Why they are/aren't the ideal persona for enterprise Wi-Fi
        
        IF NOT RELEVANT: Recommend exact persona to target instead
        
        GEOGRAPHY: Extract primary location from profile
        
        RETURN STRICT JSON FORMAT:
        {{
            "name": "extracted name",
            "designation": "extracted designation", 
            "company": "extracted company",
            "industry": "extracted industry",
            "geography": "extracted location",
            "designation_relevance": "High/Medium/Low/No",
            "how_relevant": "Detailed analysis here...",
            "recommended_target": "If not relevant, who to target instead",
            "next_steps": "Recommended engagement strategy"
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
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._fallback_analysis(linkedin_text)
                
        except Exception as e:
            st.error(f"Analysis error: {e}")
            return self._fallback_analysis(linkedin_text)
    
    def _fallback_analysis(self, linkedin_text: str) -> Dict:
        """Fallback analysis when Groq fails"""
        return {
            "name": "Extraction Failed",
            "designation": "Unknown", 
            "company": "Unknown",
            "industry": "Unknown",
            "geography": "India",
            "designation_relevance": "Low",
            "how_relevant": "Manual analysis required - AI extraction failed",
            "recommended_target": "CIO/Head of IT",
            "next_steps": "Manual research needed"
        }

def main():
    st.set_page_config(
        page_title="LinkedIn Profile Analyzer",
        page_icon="",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .relevance-high { 
        background-color: #D1FAE5; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #059669;
        margin: 10px 0;
    }
    .relevance-medium { 
        background-color: #FEF3C7; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #D97706;
        margin: 10px 0;
    }
    .relevance-low { 
        background-color: #FEE2E2; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #DC2626;
        margin: 10px 0;
    }
    .profile-card { 
        background-color: #F8FAFC; 
        padding: 20px; 
        border-radius: 10px; 
        margin: 10px 0;
        border-left: 5px solid #3B82F6;
    }
    .analysis-section {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header"> LinkedIn Profile Analyzer</div>', unsafe_allow_html=True)
    st.markdown("### Paste LinkedIn Profile Information Below")
    
    # Initialize Groq client
    client = init_groq_client()
    if not client:
        st.error("Please check your Groq API key in Streamlit secrets")
        return
    
    analyzer = LinkedInProfileAnalyzer(client)
    
    # Main input area
    linkedin_text = st.text_area(
        "Paste LinkedIn Profile Information",
        placeholder="Paste the entire LinkedIn profile text here including:\n• Name\n• Current position\n• Company\n• Location\n• Experience\n• Responsibilities\n• Education\n• Any other profile details...",
        height=300,
        help="Copy and paste all visible text from the LinkedIn profile"
    )
    
    if st.button("Analyze Profile", type="primary", use_container_width=True):
        if not linkedin_text.strip():
            st.warning("Please paste LinkedIn profile information to analyze")
        else:
            with st.spinner(" AI is analyzing the profile..."):
                analysis_result = analyzer.extract_and_analyze_profile(linkedin_text)
                
                # Display results in a structured format
                st.markdown("---")
                st.markdown("##  Analysis Results")
                
                # Profile Summary Card
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Name", analysis_result.get('name', 'N/A'))
                with col2:
                    st.metric("Designation", analysis_result.get('designation', 'N/A'))
                with col3:
                    st.metric("Company", analysis_result.get('company', 'N/A'))
                
                col4, col5, col6 = st.columns(3)
                with col4:
                    st.metric("Industry", analysis_result.get('industry', 'N/A'))
                with col5:
                    st.metric("Geography", analysis_result.get('geography', 'N/A'))
                with col6:
                    relevance = analysis_result.get('designation_relevance', 'Low')
                    st.metric("Relevance Score", relevance)
                
                # Relevance Visualization
                st.markdown("###  Designation Relevance")
                relevance = analysis_result.get('designation_relevance', 'Low')
                if relevance == 'High':
                    st.markdown(f"""
                    <div class="relevance-high">
                        <h3> HIGH RELEVANCE - Ideal Target</h3>
                        <p>This person is directly involved in IT/Network infrastructure decisions</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif relevance == 'Medium':
                    st.markdown(f"""
                    <div class="relevance-medium">
                        <h3> MEDIUM RELEVANCE - Good Prospect</h3>
                        <p>This person has indirect influence on infrastructure decisions</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="relevance-low">
                        <h3> {relevance.upper()} RELEVANCE - Limited Influence</h3>
                        <p>This person has limited involvement in IT infrastructure decisions</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Detailed Analysis
                st.markdown("###  How is this person relevant?")
                st.markdown(f'<div class="analysis-section">{analysis_result.get("how_relevant", "No analysis available")}</div>', unsafe_allow_html=True)
                
                # Recommendations for non-relevant profiles
                if relevance in ['Low', 'No']:
                    st.markdown("###  Recommended Alternative Target")
                    st.info(analysis_result.get('recommended_target', 'CIO/Head of IT Infrastructure'))
                
                # Next Steps
                st.markdown("###  Recommended Next Steps")
                st.success(analysis_result.get('next_steps', 'Schedule a discovery call to discuss Wi-Fi infrastructure needs'))

# Batch Analysis Section
def batch_analysis():
    st.markdown("---")
    st.markdown("##  Batch Analysis (Multiple Profiles)")
    
    uploaded_file = st.file_uploader("Upload text file with LinkedIn profiles", type="txt", 
                                   help="Upload a .txt file where each profile is separated by '===PROFILE==='")
    
    if uploaded_file is not None:
        content = uploaded_file.getvalue().decode("utf-8")
        profiles = content.split("===PROFILE===")
        
        st.write(f"Found {len(profiles)} profiles in file")
        
        if st.button("Analyze All Profiles", type="primary"):
            client = init_groq_client()
            if not client:
                return
                
            analyzer = LinkedInProfileAnalyzer(client)
            results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, profile_text in enumerate(profiles):
                if profile_text.strip():
                    status_text.text(f"Analyzing profile {i+1}/{len(profiles)}...")
                    analysis = analyzer.extract_and_analyze_profile(profile_text.strip())
                    results.append(analysis)
                    progress_bar.progress((i + 1) / len(profiles))
            
            # Create results dataframe
            if results:
                df = pd.DataFrame(results)
                st.markdown("### Analysis Results")
                st.dataframe(df)
                
                # Download results
                csv = df.to_csv(index=False)
                st.download_button(
                    label=" Download Results as CSV",
                    data=csv,
                    file_name="linkedin_profiles_analysis.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()
    batch_analysis()
