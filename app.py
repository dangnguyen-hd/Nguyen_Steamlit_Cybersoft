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

            # Create data summary for token optimization:
            st.session_state.data_summary ={
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.to_list(),
                "sample": df.head(3).to_dict(),
                "stats": df.describe().to_dict() if not df.empty else {} #nếu df rỗng -> ko kết quả
            }

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

        #Prepare data context with token optimization:
        df = st.session_state.df 
        if len(df) > 100:
            data_context = f"""
            Data shape: {st.session_state.data_summary['shape']},
            Columns: {', '.join(st.session_state.data_summary['columns'])},
            Data types: {st.session_state.data_summary['dtypes']},
            Sample row: {st.session_state.data_summary['sample']},
            Basic statistics {st.session_state.data_summary['stats']}: 
            """
        else: #Nếu data nhỏ hơn 100 dòng -> đưa cho AI full data
            data_context = f"""
            Full dataset:
            {df.to_string()}
            """

        #System prompt:
        system_prompt = f"""
        You are a helpful data analyst assistant.
        The user has uploaded a CSV file with the following information:
        {data_context}

        Guidelines:
        1. Answer the user's question clearly and concisely
        2. Focus on providing insights about the data
        3. Be specific and helpful.
        4. Extremly important notices: Don't answer any question in outside data range, please reponse: "Câu hỏi nằm ngoài phạm vi, vui lòng hỏi đúng phạm vi dữ liệu!"
        """

        #Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your data..."):
                try: #định nghĩa model và cấu hình AI Model
                    response = client.chat.completions.create(
                        model="gpt-6-luna",
                        messages=[
                            {"role": "system", "content": system_prompt}, 
                            {"role":"user", "content": user_input} 
                        ],
                        #temperature=0.1,
                        max_completion_tokens=1500 
                    )

                    reply = response.choices[0].message.content 
                    st.markdown(reply) #in kết quả từ AI ra

                    #Save assistant response to history
                    st.session_state.messages.append({"role":"assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
                    st.info("Please try again or rephrase your question.")

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
