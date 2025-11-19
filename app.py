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
        - We sell Wi-Fi and network infrastructure solutions
        - Target Roles: CIO, CTO, IT Infrastructure Manager, Network Architect, Operations Head
        - Target Industries: Manufacturing, Warehouses, BFSI, Education, Healthcare, Hospitality
        - Geography Focus: India
        
        EXTRACT THESE DETAILS FROM THE PROFILE:
        1. Current Designation/Title
        2. Location/Geography
        3. Key Responsibilities
        
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
        
        GEOGRAPHY: Extract primary location from profile
        
        IF NOT RELEVANT: Recommend exact persona to target instead in 'who_is_relevant' field
        
        RETURN STRICT JSON FORMAT:
        {{
            "designation_relevance": "High/Medium/Low/No",
            "how_relevant": "Detailed analysis here...",
            "geography": "extracted location",
            "who_is_relevant": "If not relevant, who to target instead"
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
                return self._fallback_analysis()
                
        except Exception as e:
            st.error(f"Analysis error: {e}")
            return self._fallback_analysis()
    
    def _fallback_analysis(self) -> Dict:
        """Fallback analysis when Groq fails"""
        return {
            "designation_relevance": "Low",
            "how_relevant": "Manual analysis required - AI extraction failed",
            "geography": "India",
            "who_is_relevant": "CIO/Head of IT"
        }

def main():
    st.set_page_config(
        page_title="LinkedIn Profile Analyzer",
        layout="wide"
    )
    
    st.title("LinkedIn Profile Analyzer for Wi-Fi Solutions")
    st.markdown("Paste LinkedIn profile information below for analysis")
    
    # Initialize Groq client
    client = init_groq_client()
    if not client:
        st.error("Please check your Groq API key in Streamlit secrets")
        return
    
    analyzer = LinkedInProfileAnalyzer(client)
    
    # Custom CSS for better table styling
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
    
    # Tab interface
    tab1, tab2 = st.tabs(["Single Profile Analysis", "Batch Analysis"])
    
    with tab1:
        st.header("Single Profile Analysis")
        
        linkedin_text = st.text_area(
            "LinkedIn Profile Information",
            placeholder="Paste the entire LinkedIn profile text here including name, current position, company, location, experience, responsibilities, etc.",
            height=300
        )
        
        if st.button("Analyze Profile", type="primary"):
            if not linkedin_text.strip():
                st.warning("Please paste LinkedIn profile information to analyze")
            else:
                with st.spinner("AI is analyzing the profile..."):
                    analysis_result = analyzer.extract_and_analyze_profile(linkedin_text)
                    
                    # Create results table
                    results_data = {
                        "Designation Relevance": [analysis_result.get('designation_relevance', 'Low')],
                        "How is he relevant": [analysis_result.get('how_relevant', 'No analysis available')],
                        "Geography": [analysis_result.get('geography', 'India')],
                        "Who is relevant then": [analysis_result.get('who_is_relevant', 'N/A')]
                    }
                    
                    results_df = pd.DataFrame(results_data)
                    
                    st.header("Analysis Results")
                    
                    # Display with better formatting
                    st.dataframe(
                        results_df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Download options
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
            
            st.write(f"Found {len(profiles)} profiles in file")
            
            if st.button("Analyze All Profiles", type="primary"):
                client = init_groq_client()
                if not client:
                    return
                    
                analyzer = LinkedInProfileAnalyzer(client)
                all_results = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, profile_text in enumerate(profiles):
                    status_text.text(f"Analyzing profile {i+1}/{len(profiles)}...")
                    analysis = analyzer.extract_and_analyze_profile(profile_text)
                    all_results.append(analysis)
                    progress_bar.progress((i + 1) / len(profiles))
                
                # Create results dataframe with required columns
                if all_results:
                    results_data = []
                    for result in all_results:
                        results_data.append({
                            "Designation Relevance": result.get('designation_relevance', 'Low'),
                            "How is he relevant": result.get('how_relevant', 'No analysis available'),
                            "Geography": result.get('geography', 'India'),
                            "Who is relevant then": result.get('who_is_relevant', 'N/A')
                        })
                    
                    results_df = pd.DataFrame(results_data)
                    
                    st.header("Batch Analysis Results")
                    
                    # Display with better formatting
                    st.dataframe(
                        results_df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Download options
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
