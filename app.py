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
        ANALYZE THIS LINKEDIN PROFILE FOR Wi-Fi/NETWORK INFRASTRUCTURE RELEVANCE:

        PROFILE TEXT:
        {linkedin_text}

        STRICT CLASSIFICATION RULES - FOLLOW EXACTLY:

        HIGH RELEVANCE (Primary Buyers) - ONLY IF:
        - CIO, CTO, Head of IT, IT Infrastructure Head, Network Infrastructure Head
        - Runs IT Infrastructure, Network Infrastructure, Wi-Fi/wireless systems, Data centers
        - Head of Automation, Head of WMS/TOS, OT (Operational Technology) owner
        - Smart Port/Smart Warehouse lead, Engineering head for scanners/IoT/sensors
        - Infra project manager, Warehouse/Port infrastructure lead WITH budget/vendor authority

        MEDIUM RELEVANCE (Influencers) - ONLY IF:
        - COO, Head of Operations (Port/Warehouse/Terminal), Warehouse Managers
        - Operations roles that DEPEND on infrastructure but don't own it
        - Face pain points like downtime, scanner issues, IoT problems
        - Can influence decisions or introduce to decision makers

        LOW RELEVANCE (Avoid) - IF:
        - Strategy, Planning, Supply Chain Planning, Procurement (non-IT)
        - HR, Marketing, Admin, Sales, Customer Service, Finance
        - Transport/Logistics (pure transportation), Vendor management
        - Any role that doesn't touch IT infrastructure or operations tech

        CRITICAL DECISION FLOW:
        1. FIRST check if profile matches ANY HIGH criteria -> if YES = HIGH
        2. THEN check if profile matches ANY MEDIUM criteria -> if YES = MEDIUM  
        3. ELSE = LOW

        EXAMPLES:
        - "CIO at ABC Company" = HIGH
        - "Head of IT Infrastructure" = HIGH
        - "Network Manager" = HIGH
        - "COO at Port Authority" = MEDIUM
        - "Warehouse Operations Manager" = MEDIUM
        - "Supply Chain Planner" = LOW
        - "HR Manager" = LOW
        - "Transportation Head" = LOW

        RETURN ONLY VALID JSON - NO OTHER TEXT:

        {{
            "designation_relevance": "High/Medium/Low",
            "how_relevant": "Brief explanation based on role and responsibilities",
            "target_persona": "If Low/Medium, suggest correct High persona",
            "next_step": "High='Direct outreach', Medium='Build influence', Low='Avoid or ask referral'"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.1,
                max_tokens=800
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Debug: Show raw response
            st.sidebar.text("Raw AI Response:")
            st.sidebar.text(result_text[:500] + "..." if len(result_text) > 500 else result_text)
            
            # Extract JSON from response using regex
            json_match = re.search(r'\{[^{}]*\{.*\}[^{}]*\}|\{.*\}', result_text, re.DOTALL)
            if json_match:
                json_string = json_match.group().strip()
                parsed_data = json.loads(json_string)
                
                # Validate the response has required fields
                if all(key in parsed_data for key in ['designation_relevance', 'how_relevant', 'target_persona', 'next_step']):
                    return parsed_data
                else:
                    return self._fallback_analysis("Missing required fields in AI response")
            else:
                return self._fallback_analysis("No JSON found in AI response")
                
        except Exception as e:
            st.error(f"Analysis error: {e}")
            return self._fallback_analysis(f"API error: {str(e)}")
    
    def _fallback_analysis(self, reason: str) -> Dict[str, Any]:
        """Fallback analysis when Groq fails or JSON is unparseable."""
        return {
            "designation_relevance": "Low",
            "how_relevant": f"Manual analysis required - {reason}",
            "target_persona": "CIO/Head of IT Infrastructure",
            "next_step": "Manual review of profile needed"
        }

def main():
    st.set_page_config(
        page_title="LinkedIn Profile Analyzer",
        layout="wide"
    )
    
    st.title("LinkedIn Profile Analyzer for Wi-Fi/Network Solutions")
    st.markdown("Analyze LinkedIn profiles for Wi-Fi/Network Infrastructure relevance using strict criteria")
    
    # Sidebar with examples
    st.sidebar.header("Quick Examples")
    st.sidebar.markdown("""
    HIGH Examples:
    - CIO, CTO, Head of IT
    - IT Infrastructure Manager
    - Network Infrastructure Head
    - Head of Automation
    
    MEDIUM Examples:
    - COO, Operations Head
    - Warehouse Operations Manager
    - Terminal Operations Lead
    
    LOW Examples:
    - HR Manager, Finance Head
    - Supply Chain Planner
    - Transportation Manager
    """)
    
    client = init_groq_client()
    if not client:
        st.error("Application cannot run without a valid Groq client.")
        return
    
    analyzer = LinkedInProfileAnalyzer(client)
    
    tab1, tab2 = st.tabs(["Single Profile Analysis", "Batch Analysis"])
    
    with tab1:
        st.header("Single Profile Analysis")
        
        # Example profiles for testing
        example_profiles = {
            "Select Example": "",
            "CIO Example": "John Smith\nChief Information Officer\nABC Manufacturing\nResponsible for IT infrastructure, network systems, data centers, and technology budget approval. Leads digital transformation initiatives.",
            "COO Example": "Sarah Johnson\nChief Operating Officer\nXYZ Logistics\nOversees warehouse operations, terminal management, and supply chain operations. Manages operational efficiency and process improvement.",
            "HR Example": "Mike Brown\nHR Director\nGlobal Corporation\nResponsible for talent acquisition, employee relations, and organizational development across multiple locations."
        }
        
        selected_example = st.selectbox("Load example profile:", list(example_profiles.keys()))
        
        linkedin_text = st.text_area(
            "LinkedIn Profile Information",
            value=example_profiles[selected_example],
            placeholder="Paste the entire LinkedIn profile text here...",
            height=300,
            help="Include full profile with title, company, and responsibilities"
        )
        
        if st.button("Analyze Profile", type="primary", key="analyze_single"):
            if not linkedin_text.strip():
                st.warning("Please paste LinkedIn profile information to analyze")
            else:
                with st.spinner("AI is analyzing the profile..."):
                    analysis_result = analyzer.extract_and_analyze_profile(linkedin_text)
                    
                    # Display results with better formatting
                    _display_single_results(analysis_result)
    
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
            
            st.info(f"Found {len(profiles)} profiles in file. Ready to analyze.")
            
            if st.button("Analyze All Profiles", type="primary", key="analyze_batch"):
                with st.spinner(f"Analyzing {len(profiles)} profiles..."):
                    all_results = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, profile_text in enumerate(profiles):
                        status_text.text(f"Analyzing profile {i+1}/{len(profiles)}...")
                        analysis = analyzer.extract_and_analyze_profile(profile_text)
                        all_results.append(analysis)
                        progress_bar.progress((i + 1) / len(profiles))
                    
                    status_text.text("Batch analysis complete!")
                    
                    if all_results:
                        _display_batch_results(all_results)

def _display_single_results(analysis_result: Dict[str, Any]):
    """Display single profile analysis results"""
    relevance = analysis_result.get('designation_relevance', 'Low').lower()
    
    # Create colored boxes for relevance
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if relevance == "high":
            st.success("HIGH RELEVANCE")
            st.metric("Decision Level", "Primary Buyer")
        else:
            st.info("HIGH RELEVANCE")
            
    with col2:
        if relevance == "medium":
            st.warning("MEDIUM RELEVANCE")
            st.metric("Decision Level", "Influencer")
        else:
            st.info("MEDIUM RELEVANCE")
            
    with col3:
        if relevance == "low":
            st.error("LOW RELEVANCE")
            st.metric("Decision Level", "Avoid")
        else:
            st.info("LOW RELEVANCE")
    
    # Detailed results
    st.subheader("Analysis Details")
    
    results_data = {
        "Metric": ["Relevance Level", "Analysis", "Target Persona", "Recommended Action"],
        "Details": [
            analysis_result.get('designation_relevance', 'Low'),
            analysis_result.get('how_relevant', 'No analysis available'),
            analysis_result.get('target_persona', 'N/A'),
            analysis_result.get('next_step', 'N/A')
        ]
    }
    
    results_df = pd.DataFrame(results_data)
    st.table(results_df)
    
    # Download buttons
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
        json_data = json.dumps(analysis_result, indent=2)
        st.download_button(
            label="Download as JSON",
            data=json_data,
            file_name="profile_analysis.json",
            mime="application/json"
        )

def _display_batch_results(all_results: list):
    """Display batch analysis results"""
    results_data_list = []
    for i, result in enumerate(all_results):
        results_data_list.append({
            "Profile": f"Profile {i+1}",
            "Relevance": result.get('designation_relevance', 'Low'),
            "Analysis": result.get('how_relevant', 'No analysis')[:100] + "..." if len(result.get('how_relevant', '')) > 100 else result.get('how_relevant', 'No analysis'),
            "Target Persona": result.get('target_persona', 'N/A'),
            "Next Step": result.get('next_step', 'N/A')
        })
    
    results_df = pd.DataFrame(results_data_list)
    
    # Summary statistics
    high_count = len([r for r in all_results if r.get('designation_relevance', '').lower() == 'high'])
    medium_count = len([r for r in all_results if r.get('designation_relevance', '').lower() == 'medium'])
    low_count = len([r for r in all_results if r.get('designation_relevance', '').lower() == 'low'])
    
    st.subheader("Batch Analysis Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("High Relevance", high_count)
    with col2:
        st.metric("Medium Relevance", medium_count)
    with col3:
        st.metric("Low Relevance", low_count)
    
    st.subheader("Detailed Results")
    st.dataframe(results_df, use_container_width=True)
    
    # Download options
    col1, col2 = st.columns(2)
    with col1:
        csv = results_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="batch_analysis.csv",
            mime="text/csv"
        )
    with col2:
        tsv = results_df.to_csv(index=False, sep='\t')
        st.download_button(
            label="Download TSV",
            data=tsv,
            file_name="batch_analysis.tsv",
            mime="text/tab-separated-values"
        )

if __name__ == "__main__":
    main()
