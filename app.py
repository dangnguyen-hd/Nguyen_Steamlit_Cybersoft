import streamlit as st
import pandas as pd
import openai

st.set_page_config(
    page_title="Ask your CSV",
    page_icon="📊",
    layout="wide"
)

# Initialize OpenAI Client
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Session state initialization:
if 'massage' not in st.session_state:
    st.session_state.massages = []
if 'df' not in st.session_state:
    st.session_state.df = None
if 'data_summary' not in st.session_state:
    st.session_state.data_summary = None

st.title("Ask your CSV")
st.markdown("Upload your data and ask questions in plain English!")

#Sidebar for file upload
with st.sidebar:
    st.header("Data Upload")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.df = df
            st.success(f"Loaded {df.shape[0]} rows x {df.shape[1]} columns.")

            # Data preview
            with st.expander("Preview data"):
                st.dataframe(df.head(5))

            # Basic status
            with st.expander("Data Summary"):
                col1, col2 = st.columns(2) 
                with col1:
                    st.metric("Total row", df.shape[0])
                    st.metric("Total columns", df.shape[1])
                with col2:
                    st.metric("Memory Usage", f"{df.memory_usage().sum() / 1024:.1f} KB")
                    st.metric("Missing value", df.isnull().sum().sum())
        except Exception as e:
            st.error(f"Eror reading file: {e}")
            st.info("Please make sure your file is a valid CSV format")
    else:
        st.info("Upload a CSV file to start analyzing!")

# Main chat interface
if st.session_state.df is not None:
    # Display chat history
    for msg in st.session_state.massages:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])

    # Chat input 
    user_input = st.chat_input("Ask a question about your data")

    if user_input:
        # Add user massage to history
        st.session_state.massages.append({'role': 'user', 'content': user_input})

        # Display user massage
        with st.chat_message('user'):
            st.markdown(user_input)
else:
    # No data upload stata:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.info("Please upload a CSV file to start")

        # Example question
        st.markdown("### Example questions you can ask")
        st.markdown("""
        1. dfasfdas
        2. gfdsgfsdgsfdgffsd.
        3. fgdsjhgsfdghjds
        """)
